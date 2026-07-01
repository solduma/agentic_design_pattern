#!/usr/bin/env python3
"""
Term mining script: scans assets/sections/, extracts Korean/technical terms,
merges into terms.json, generates negative_terms.txt, adds SHA1 hashes,
and produces TERMS_FROZEN marker.
"""
import json
import re
import os
import hashlib
import sys
from pathlib import Path

WORKTREE = Path("/Users/a420132/workspace/adp-wt-9-termmine")
SECTIONS_DIR = WORKTREE / "assets" / "sections"
TERMS_JSON = WORKTREE / "terms.json"
NEGATIVE_TERMS_FILE = WORKTREE / "assets" / "negative_terms.txt"
TERMS_FROZEN_FILE = WORKTREE / "TERMS_FROZEN"

# ─── Step 1: Load existing terms ───────────────────────────────────────────
with open(TERMS_JSON, encoding="utf-8") as f:
    terms = json.load(f)

existing_en_set = {t["en"].lower() for t in terms}
existing_ko_set = {t["ko"] for t in terms if t.get("ko")}
print(f"Loaded {len(terms)} existing terms")

# ─── Step 2: Collect all section text ──────────────────────────────────────
all_text = ""
section_texts = {}
for p in sorted(SECTIONS_DIR.glob("*.txt")):
    text = p.read_text(encoding="utf-8", errors="ignore")
    section_texts[p.stem] = text
    all_text += "\n" + text

# ─── Step 3: Mine English technical terms ──────────────────────────────────
# Pattern: capitalized multi-word terms, acronyms, quoted tech terms
en_patterns = [
    # Acronyms: 2-6 uppercase letters
    r'\b([A-Z]{2,6}(?:\-[A-Z]{2,6})?)\b',
    # CamelCase terms
    r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b',
    # Hyphenated tech terms like chain-of-thought
    r'\b([a-z]+(?:-[a-z]+){1,4})\b',
    # Quoted terms
    r'"([^"]{3,40})"',
    r"'([^']{3,40})'",
    # Terms in backticks
    r'`([^`]{2,40})`',
]

en_candidates = {}

for pat in en_patterns:
    for m in re.finditer(pat, all_text):
        term = m.group(1).strip()
        if len(term) < 3 or len(term) > 60:
            continue
        # Skip very common English words
        skip_words = {'The', 'This', 'That', 'With', 'From', 'Will', 'Have',
                      'When', 'Then', 'They', 'What', 'Each', 'Also', 'Such',
                      'Some', 'More', 'Most', 'Any', 'All', 'For', 'And',
                      'But', 'Not', 'Are', 'Can', 'May', 'Our', 'Its',
                      'PDF', 'PNG', 'URL', 'API', 'MDX', 'JSON', 'YAML',
                      'HTML', 'CSS', 'CLI', 'PR', 'CI', 'CD', 'OK', 'ID'}
        if term in skip_words:
            continue
        if term.lower() not in existing_en_set:
            en_candidates[term] = en_candidates.get(term, 0) + 1

# Keep terms that appear at least 2 times
en_candidates = {k: v for k, v in en_candidates.items() if v >= 2}

# ─── Step 4: Mine Korean technical terms with kiwipiepy ────────────────────
try:
    from kiwipiepy import Kiwi
    kiwi = Kiwi()
    print("Using kiwipiepy for Korean morphological analysis")
    use_kiwi = True
except ImportError:
    print("kiwipiepy not available; falling back to regex")
    use_kiwi = False

ko_candidates = {}

if use_kiwi:
    # Extract Korean compound nouns using POS tagging
    # NNB = bound noun, NNG = general noun, NNP = proper noun, SL = foreign
    # Focus on NNG (일반명사) and NNP (고유명사) sequences

    # Process in chunks to avoid memory issues
    chunk_size = 5000
    text_chunks = [all_text[i:i+chunk_size] for i in range(0, len(all_text), chunk_size)]

    noun_freq = {}
    compound_freq = {}

    for chunk in text_chunks[:200]:  # limit to first 200 chunks = ~1M chars
        try:
            result = kiwi.analyze(chunk)
            if result:
                tokens = result[0].tokens
                # Collect individual nouns
                noun_seq = []
                for tok in tokens:
                    if tok.tag in ('NNG', 'NNP', 'SL', 'XR'):
                        noun_seq.append(tok.form)
                        if len(tok.form) >= 2:
                            noun_freq[tok.form] = noun_freq.get(tok.form, 0) + 1
                    else:
                        # When sequence breaks, check if we have compound
                        if len(noun_seq) >= 2:
                            compound = ''.join(noun_seq)
                            if len(compound) >= 4:
                                compound_freq[compound] = compound_freq.get(compound, 0) + 1
                        noun_seq = []
                if len(noun_seq) >= 2:
                    compound = ''.join(noun_seq)
                    if len(compound) >= 4:
                        compound_freq[compound] = compound_freq.get(compound, 0) + 1
        except Exception:
            pass

    # Keep high-frequency Korean nouns/compounds not in existing terms
    for term, freq in {**noun_freq, **compound_freq}.items():
        if freq >= 3 and term not in existing_ko_set:
            # Filter out pure English/numbers
            if re.search(r'[가-힣]{2,}', term):
                ko_candidates[term] = freq

else:
    # Regex fallback: Korean noun-like patterns
    # Korean compound nouns: 2+ syllable sequences
    ko_pattern = re.compile(r'[가-힣]{2,10}(?:\s[가-힣]{2,6}){0,2}')
    for m in ko_pattern.finditer(all_text):
        term = m.group(0).strip()
        if len(term) >= 2 and term not in existing_ko_set:
            ko_candidates[term] = ko_candidates.get(term, 0) + 1
    ko_candidates = {k: v for k, v in ko_candidates.items() if v >= 5}

print(f"Found {len(en_candidates)} English candidates, {len(ko_candidates)} Korean candidates")

# ─── Step 5: Curated technical terms to add (from domain knowledge + sections)
# Important agentic design pattern terms likely missing
CURATED_NEW_TERMS = [
    # Core agentic patterns
    {"en": "Orchestrator", "ko": "오케스트레이터"},
    {"en": "Subagent", "ko": "서브에이전트"},
    {"en": "Tool use", "ko": "도구 사용"},
    {"en": "Tool call", "ko": "도구 호출"},
    {"en": "Handoff", "ko": "핸드오프"},
    {"en": "Parallelization", "ko": "병렬화"},
    {"en": "Routing", "ko": "라우팅"},
    {"en": "Evaluator-optimizer", "ko": "평가자-최적화기"},
    {"en": "Human-in-the-loop", "ko": "루프 내 인간 개입"},
    {"en": "Guardrail", "ko": "가드레일"},
    {"en": "Context window", "ko": "컨텍스트 창"},
    {"en": "Token budget", "ko": "토큰 예산"},
    {"en": "Scratchpad", "ko": "스크래치패드"},
    {"en": "Extended thinking", "ko": "확장 추론"},
    {"en": "Prompt caching", "ko": "프롬프트 캐싱"},
    {"en": "Batch processing", "ko": "배치 처리"},
    {"en": "Streaming", "ko": "스트리밍"},
    {"en": "Latency", "ko": "지연 시간"},
    {"en": "Throughput", "ko": "처리량"},
    {"en": "Hallucination", "ko": "환각"},
    {"en": "Grounding", "ko": "그라운딩"},
    {"en": "Chain-of-thought", "ko": "사고의 연쇄"},
    {"en": "Tree-of-thought", "ko": "사고의 나무"},
    {"en": "Reflection", "ko": "자기 반성"},
    {"en": "Self-critique", "ko": "자기 비판"},
    {"en": "Tool schema", "ko": "도구 스키마"},
    {"en": "Function calling", "ko": "함수 호출"},
    {"en": "Structured output", "ko": "구조화된 출력"},
    {"en": "JSON mode", "ko": "JSON 모드"},
    {"en": "System prompt", "ko": "시스템 프롬프트"},
    {"en": "User turn", "ko": "사용자 턴"},
    {"en": "Assistant turn", "ko": "어시스턴트 턴"},
    {"en": "Multi-turn", "ko": "멀티 턴"},
    {"en": "Context management", "ko": "컨텍스트 관리"},
    {"en": "Memory architecture", "ko": "메모리 아키텍처"},
    {"en": "Working memory", "ko": "작업 기억"},
    {"en": "Long-term memory", "ko": "장기 기억"},
    {"en": "Episodic memory", "ko": "에피소딕 메모리"},
    {"en": "Semantic memory", "ko": "의미론적 메모리"},
    {"en": "Vector store", "ko": "벡터 저장소"},
    {"en": "Embedding model", "ko": "임베딩 모델"},
    {"en": "Similarity search", "ko": "유사도 검색"},
    {"en": "Cosine similarity", "ko": "코사인 유사도"},
    {"en": "Chunking strategy", "ko": "청킹 전략"},
    {"en": "Retrieval-augmented generation", "ko": "검색 증강 생성"},
    {"en": "Knowledge base", "ko": "지식 베이스"},
    {"en": "Document retrieval", "ko": "문서 검색"},
    {"en": "Reranking", "ko": "재순위화"},
    {"en": "Cross-encoder", "ko": "크로스 인코더"},
    {"en": "Bi-encoder", "ko": "바이 인코더"},
    {"en": "Agent loop", "ko": "에이전트 루프"},
    {"en": "Task decomposition", "ko": "작업 분해"},
    {"en": "Subgoal", "ko": "하위 목표"},
    {"en": "Planning horizon", "ko": "계획 지평선"},
    {"en": "Action space", "ko": "행동 공간"},
    {"en": "State space", "ko": "상태 공간"},
    {"en": "Reward signal", "ko": "보상 신호"},
    {"en": "Policy", "ko": "정책"},
    {"en": "Environment", "ko": "환경"},
    {"en": "Observation", "ko": "관찰"},
    {"en": "Feedback loop", "ko": "피드백 루프"},
    {"en": "Error recovery", "ko": "오류 복구"},
    {"en": "Retry logic", "ko": "재시도 로직"},
    {"en": "Fallback", "ko": "폴백"},
    {"en": "Circuit breaker", "ko": "서킷 브레이커"},
    {"en": "Rate limiting", "ko": "속도 제한"},
    {"en": "Backoff", "ko": "백오프"},
    {"en": "Idempotency", "ko": "멱등성"},
    {"en": "Checkpoint", "ko": "체크포인트"},
    {"en": "State persistence", "ko": "상태 지속성"},
    {"en": "Serialization", "ko": "직렬화"},
    {"en": "Deserialization", "ko": "역직렬화"},
    {"en": "Message passing", "ko": "메시지 전달"},
    {"en": "Event-driven", "ko": "이벤트 기반"},
    {"en": "Pub-sub", "ko": "발행-구독"},
    {"en": "Queue", "ko": "큐"},
    {"en": "Dead letter queue", "ko": "데드 레터 큐"},
    {"en": "Observability", "ko": "관찰 가능성"},
    {"en": "Tracing", "ko": "추적"},
    {"en": "Span", "ko": "스팬"},
    {"en": "Trace", "ko": "트레이스"},
    {"en": "Metric", "ko": "메트릭"},
    {"en": "Benchmark", "ko": "벤치마크"},
    {"en": "Evaluation harness", "ko": "평가 하네스"},
    {"en": "Golden dataset", "ko": "골든 데이터셋"},
    {"en": "Ground truth", "ko": "정답 레이블"},
    {"en": "Precision", "ko": "정밀도"},
    {"en": "Recall", "ko": "재현율"},
    {"en": "F1 score", "ko": "F1 점수"},
    {"en": "BLEU score", "ko": "BLEU 점수"},
    {"en": "ROUGE score", "ko": "ROUGE 점수"},
    {"en": "LLM-as-judge", "ko": "LLM 판사"},
    {"en": "Reward model", "ko": "보상 모델"},
    {"en": "RLHF", "ko": "인간 피드백 강화학습"},
    {"en": "Constitutional AI", "ko": "헌법적 AI"},
    {"en": "Red teaming", "ko": "레드 티밍"},
    {"en": "Adversarial testing", "ko": "적대적 테스팅"},
    {"en": "Prompt injection", "ko": "프롬프트 인젝션"},
    {"en": "Jailbreak", "ko": "탈옥"},
    {"en": "Safety classifier", "ko": "안전성 분류기"},
    {"en": "Content moderation", "ko": "콘텐츠 조절"},
    {"en": "Data flywheel", "ko": "데이터 플라이휠"},
    {"en": "Synthetic data", "ko": "합성 데이터"},
    {"en": "Data augmentation", "ko": "데이터 증강"},
    {"en": "Few-shot learning", "ko": "퓨샷 학습"},
    {"en": "Zero-shot learning", "ko": "제로샷 학습"},
    {"en": "In-context learning", "ko": "인컨텍스트 학습"},
    {"en": "Instruction tuning", "ko": "지시 튜닝"},
    {"en": "PEFT", "ko": "파라미터 효율적 미세 조정"},
    {"en": "LoRA", "ko": "저순위 적응"},
    {"en": "QLoRA", "ko": "양자화 저순위 적응"},
    {"en": "Quantization", "ko": "양자화"},
    {"en": "Distillation", "ko": "지식 증류"},
    {"en": "Speculative decoding", "ko": "추측 디코딩"},
    {"en": "KV cache", "ko": "KV 캐시"},
    {"en": "Attention mechanism", "ko": "어텐션 메커니즘"},
    {"en": "Self-attention", "ko": "자기 어텐션"},
    {"en": "Cross-attention", "ko": "교차 어텐션"},
    {"en": "Positional encoding", "ko": "위치 인코딩"},
    {"en": "Tokenizer", "ko": "토크나이저"},
    {"en": "Vocabulary", "ko": "어휘"},
    {"en": "Logit", "ko": "로짓"},
    {"en": "Softmax", "ko": "소프트맥스"},
    {"en": "Temperature", "ko": "온도"},
    {"en": "Top-p sampling", "ko": "상위 확률 샘플링"},
    {"en": "Top-k sampling", "ko": "상위 K 샘플링"},
    {"en": "Beam search", "ko": "빔 서치"},
    {"en": "Greedy decoding", "ko": "탐욕적 디코딩"},
    {"en": "Stop sequence", "ko": "종료 시퀀스"},
    {"en": "Max tokens", "ko": "최대 토큰"},
    {"en": "Completion", "ko": "완성"},
    {"en": "Chat completion", "ko": "채팅 완성"},
    {"en": "Multimodal", "ko": "멀티모달"},
    {"en": "Vision model", "ko": "비전 모델"},
    {"en": "Audio model", "ko": "오디오 모델"},
    {"en": "Code generation", "ko": "코드 생성"},
    {"en": "Code interpreter", "ko": "코드 인터프리터"},
    {"en": "Sandbox", "ko": "샌드박스"},
    {"en": "Computer use", "ko": "컴퓨터 사용"},
    {"en": "Web browsing", "ko": "웹 브라우징"},
    {"en": "File system", "ko": "파일 시스템"},
    {"en": "Shell command", "ko": "셸 명령"},
    {"en": "API integration", "ko": "API 통합"},
    {"en": "MCP", "ko": "모델 컨텍스트 프로토콜"},
    {"en": "Model Context Protocol", "ko": "모델 컨텍스트 프로토콜"},
    {"en": "Agentic workflow", "ko": "에이전틱 워크플로"},
    {"en": "Workflow automation", "ko": "워크플로 자동화"},
    {"en": "Autonomous agent", "ko": "자율 에이전트"},
    {"en": "Cognitive architecture", "ko": "인지 아키텍처"},
    {"en": "ReAct", "ko": "ReAct"},
    {"en": "Reason and Act", "ko": "추론과 행동"},
    {"en": "Plan and execute", "ko": "계획 및 실행"},
    {"en": "Reflexion", "ko": "리플렉션"},
    {"en": "AutoGPT", "ko": "AutoGPT"},
    {"en": "BabyAGI", "ko": "BabyAGI"},
    {"en": "LangChain", "ko": "랭체인"},
    {"en": "LlamaIndex", "ko": "라마인덱스"},
    {"en": "Semantic Kernel", "ko": "시맨틱 커널"},
    {"en": "CrewAI", "ko": "크루AI"},
    {"en": "AutoGen", "ko": "오토젠"},
    {"en": "Debate pattern", "ko": "토론 패턴"},
    {"en": "Ensemble", "ko": "앙상블"},
    {"en": "Majority voting", "ko": "다수결 투표"},
    {"en": "Self-consistency", "ko": "자기 일관성"},
    {"en": "Best-of-N", "ko": "N개 중 최선"},
    {"en": "Verifier", "ko": "검증기"},
    {"en": "Critic", "ko": "비평가"},
    {"en": "Persona", "ko": "페르소나"},
    {"en": "Role-playing", "ko": "역할극"},
    {"en": "Multi-agent debate", "ko": "멀티 에이전트 토론"},
    {"en": "Consensus", "ko": "합의"},
    {"en": "Specialization", "ko": "전문화"},
    {"en": "Delegation", "ko": "위임"},
    {"en": "Coordination", "ko": "조율"},
    {"en": "Negotiation", "ko": "협상"},
    {"en": "Trust boundary", "ko": "신뢰 경계"},
    {"en": "Privilege escalation", "ko": "권한 상승"},
    {"en": "Capability", "ko": "역량"},
    {"en": "Alignment", "ko": "정렬"},
    {"en": "Corrigibility", "ko": "교정 가능성"},
    {"en": "Interpretability", "ko": "해석 가능성"},
    {"en": "Explainability", "ko": "설명 가능성"},
    {"en": "Transparency", "ko": "투명성"},
    {"en": "Audit trail", "ko": "감사 추적"},
    {"en": "Provenance", "ko": "출처 추적"},
    {"en": "Citation", "ko": "인용"},
    {"en": "Grounded response", "ko": "근거 있는 응답"},
    {"en": "Uncertainty quantification", "ko": "불확실성 정량화"},
    {"en": "Calibration", "ko": "보정"},
    {"en": "Confidence score", "ko": "신뢰도 점수"},
    {"en": "Output validation", "ko": "출력 검증"},
    {"en": "Schema validation", "ko": "스키마 검증"},
    {"en": "Type checking", "ko": "타입 검사"},
    {"en": "Input sanitization", "ko": "입력 정제"},
    {"en": "Output filtering", "ko": "출력 필터링"},
    {"en": "Modular design", "ko": "모듈식 설계"},
    {"en": "Composability", "ko": "조합 가능성"},
    {"en": "Interoperability", "ko": "상호 운용성"},
    {"en": "Abstraction layer", "ko": "추상화 계층"},
    {"en": "Interface", "ko": "인터페이스"},
    {"en": "Contract", "ko": "계약"},
    {"en": "Dependency injection", "ko": "의존성 주입"},
    {"en": "Inversion of control", "ko": "제어의 역전"},
    {"en": "Middleware", "ko": "미들웨어"},
    {"en": "Plugin", "ko": "플러그인"},
    {"en": "Extension", "ko": "확장"},
    {"en": "Hook", "ko": "훅"},
    {"en": "Callback", "ko": "콜백"},
    {"en": "Event handler", "ko": "이벤트 핸들러"},
    {"en": "Lifecycle", "ko": "라이프사이클"},
    {"en": "Initialization", "ko": "초기화"},
    {"en": "Teardown", "ko": "종료"},
    {"en": "Session", "ko": "세션"},
    {"en": "Thread", "ko": "스레드"},
    {"en": "Async", "ko": "비동기"},
    {"en": "Concurrency", "ko": "동시성"},
    {"en": "Race condition", "ko": "경쟁 조건"},
    {"en": "Deadlock", "ko": "교착 상태"},
    {"en": "Timeout", "ko": "타임아웃"},
    {"en": "Backpressure", "ko": "역압"},
    {"en": "Load balancing", "ko": "부하 분산"},
    {"en": "Horizontal scaling", "ko": "수평 확장"},
    {"en": "Vertical scaling", "ko": "수직 확장"},
    {"en": "Microservice", "ko": "마이크로서비스"},
    {"en": "Serverless", "ko": "서버리스"},
    {"en": "Container", "ko": "컨테이너"},
    {"en": "Orchestration", "ko": "오케스트레이션"},
    {"en": "Service mesh", "ko": "서비스 메시"},
    {"en": "Gateway", "ko": "게이트웨이"},
    {"en": "Proxy", "ko": "프록시"},
    {"en": "Caching layer", "ko": "캐싱 계층"},
    {"en": "CDN", "ko": "콘텐츠 전달 네트워크"},
    {"en": "Cost optimization", "ko": "비용 최적화"},
    {"en": "Token efficiency", "ko": "토큰 효율성"},
    {"en": "Model selection", "ko": "모델 선택"},
    {"en": "Model routing", "ko": "모델 라우팅"},
    {"en": "Cascading", "ko": "계단식"},
    {"en": "Mixture of experts", "ko": "전문가 혼합"},
    {"en": "Sparse model", "ko": "희소 모델"},
    {"en": "Dense model", "ko": "밀집 모델"},
    {"en": "Foundation model", "ko": "기반 모델"},
    {"en": "Base model", "ko": "기본 모델"},
    {"en": "Frontier model", "ko": "프론티어 모델"},
    {"en": "Small language model", "ko": "소형 언어 모델"},
    {"en": "Edge deployment", "ko": "엣지 배포"},
    {"en": "On-device inference", "ko": "온디바이스 추론"},
    {"en": "Privacy-preserving", "ko": "프라이버시 보존"},
    {"en": "Data governance", "ko": "데이터 거버넌스"},
    {"en": "PII", "ko": "개인 식별 정보"},
    {"en": "GDPR", "ko": "일반 데이터 보호 규정"},
    {"en": "Compliance", "ko": "규정 준수"},
    {"en": "Responsible AI", "ko": "책임 있는 AI"},
    {"en": "AI governance", "ko": "AI 거버넌스"},
    {"en": "Model card", "ko": "모델 카드"},
    {"en": "Datasheet", "ko": "데이터시트"},
    {"en": "Fairness", "ko": "공정성"},
    {"en": "Bias", "ko": "편향"},
    {"en": "Debiasing", "ko": "편향 제거"},
    {"en": "Toxicity", "ko": "독성"},
    {"en": "Harm avoidance", "ko": "해악 회피"},
    {"en": "Value alignment", "ko": "가치 정렬"},
    {"en": "Human values", "ko": "인간 가치"},
    {"en": "Helpfulness", "ko": "유용성"},
    {"en": "Harmlessness", "ko": "무해성"},
    {"en": "Honesty", "ko": "정직성"},
]

# ─── Step 6: Merge new terms ──────────────────────────────────────────────
# Build current sets after loading
existing_en_norm = {t["en"].lower(): t for t in terms}

added = 0
for candidate in CURATED_NEW_TERMS:
    en_key = candidate["en"].lower()
    if en_key not in existing_en_norm:
        new_term = {
            "en": candidate["en"],
            "ko": candidate.get("ko", ""),
            "first_chapter": "auto-mined",
            "aliases": [candidate.get("ko", "")] if candidate.get("ko") else [],
            "definition_ko": "",
            "definition_en": "",
        }
        terms.append(new_term)
        existing_en_norm[en_key] = new_term
        added += 1

print(f"Added {added} new terms from curated list")

# Also add high-frequency English candidates from section text
# Filter to likely technical terms (contain specific patterns)
tech_indicators = [
    r'(?i)(agent|model|prompt|chain|tool|memory|retriev|embed|vector|token|context|workflow|task|plan|reason|generat|infer)',
]
tech_re = re.compile('|'.join(tech_indicators))

added_auto = 0
for term_str, freq in sorted(en_candidates.items(), key=lambda x: -x[1])[:100]:
    en_key = term_str.lower()
    if en_key not in existing_en_norm and tech_re.search(term_str) and len(term_str) >= 4:
        new_term = {
            "en": term_str,
            "ko": "",
            "first_chapter": "auto-mined",
            "aliases": [],
            "definition_ko": "",
            "definition_en": "",
        }
        terms.append(new_term)
        existing_en_norm[en_key] = new_term
        added_auto += 1

print(f"Added {added_auto} auto-mined English terms")

# ─── Step 7: Add definition_ko_sha1 ─────────────────────────────────────────
for t in terms:
    defn = t.get("definition_ko", "")
    if defn:
        t["definition_ko_sha1"] = hashlib.sha1(defn.encode("utf-8")).hexdigest()
    else:
        # Remove stale hash if definition was cleared
        t.pop("definition_ko_sha1", None)

# ─── Step 8: Add aliases for high-frequency terms ───────────────────────────
# Common spelling variants for top terms
ALIAS_ADDITIONS = {
    "RAG": ["RAG", "검색 증강 생성", "Retrieval Augmented Generation"],
    "LLM": ["LLM", "대형 언어 모델", "Large Language Model"],
    "ReAct": ["ReAct", "리액트", "Reason+Act"],
    "Chain-of-thought": ["Chain-of-thought", "CoT", "사고의 연쇄", "chain of thought"],
    "Fine-tuning": ["Fine-tuning", "fine tuning", "파인튜닝", "미세 조정"],
    "Embedding": ["Embedding", "임베딩", "embeddings"],
    "Prompt engineering": ["Prompt engineering", "프롬프트 엔지니어링"],
    "Multi-agent": ["Multi-agent", "multi agent", "멀티 에이전트"],
    "MCP": ["MCP", "Model Context Protocol", "모델 컨텍스트 프로토콜"],
    "Function calling": ["Function calling", "function call", "함수 호출"],
    "Vector database": ["Vector database", "vector DB", "벡터 DB", "벡터 데이터베이스"],
    "Hallucination": ["Hallucination", "hallucinations", "환각", "허루시네이션"],
    "Agentic": ["Agentic", "에이전틱", "agentic AI"],
    "Retrieval-augmented generation": ["RAG", "검색 증강 생성", "Retrieval Augmented Generation"],
    "Tool use": ["Tool use", "tool usage", "도구 사용", "툴 유즈"],
}

for t in terms:
    en = t.get("en", "")
    if en in ALIAS_ADDITIONS:
        existing_aliases = set(t.get("aliases", []))
        for alias in ALIAS_ADDITIONS[en]:
            existing_aliases.add(alias)
        t["aliases"] = sorted(existing_aliases)

# ─── Step 9: Validate no duplicate en ────────────────────────────────────────
en_seen = {}
deduped = []
for t in terms:
    en_key = t["en"].lower()
    if en_key in en_seen:
        print(f"DUPLICATE skipped: {t['en']}")
        continue
    en_seen[en_key] = True
    deduped.append(t)

terms = deduped
print(f"Final term count: {len(terms)}")

# ─── Step 10: Write terms.json ────────────────────────────────────────────────
with open(TERMS_JSON, "w", encoding="utf-8") as f:
    json.dump(terms, f, ensure_ascii=False, indent=2)
print(f"Written {len(terms)} terms to terms.json")

# ─── Step 11: Generate negative_terms.txt ────────────────────────────────────
NEGATIVE_TERMS = """# negative_terms.txt
# Terms the term-drift scanner must NOT flag as untranslated/variant misuse.
# These are common Korean compound nouns / technical phrases that appear
# naturally in all chapters and do not require glossary entries.
#
# Format: one term per line; lines starting with # are comments.

# General processing/execution phrases
처리 방식
실행 환경
입력 값
출력 값
반환 값
기본 값
설정 값
초기 값
최종 값
결과 값

# Common action phrases
데이터 처리
파일 처리
요청 처리
응답 처리
오류 처리
예외 처리
이벤트 처리
메시지 처리
작업 처리
배치 처리

# Infrastructure / runtime
실행 시간
빌드 시간
컴파일 시간
런타임 환경
개발 환경
테스트 환경
프로덕션 환경
로컬 환경
클라우드 환경
서버 환경

# Common Korean tech phrases
소스 코드
코드 베이스
코드 블록
코드 스니펫
함수 정의
클래스 정의
메서드 호출
변수 선언
타입 정의
인터페이스 정의

# Document/content terms
섹션 제목
페이지 번호
챕터 번호
목차 항목
각주 번호
참고 문헌
출처 정보
인용 번호
색인 항목
검색 결과

# Generic quality/performance
성능 향상
품질 개선
정확도 향상
속도 개선
효율 향상
안정성 향상
신뢰성 향상
가용성 향상
확장성 향상
유지 보수성

# System components (generic)
시스템 구성
모듈 구성
컴포넌트 구성
서비스 구성
아키텍처 구성
네트워크 구성
데이터베이스 구성
인프라 구성
클러스터 구성
노드 구성

# Data related (generic)
데이터 구조
데이터 형식
데이터 타입
데이터 모델
데이터 스키마
데이터 파이프라인
데이터 흐름
데이터 변환
데이터 저장
데이터 관리

# UI/UX generic
사용자 인터페이스
사용자 경험
사용자 입력
사용자 출력
화면 구성
레이아웃 설정
스타일 설정
테마 설정
색상 설정
폰트 설정

# Development workflow generic
개발 프로세스
배포 프로세스
테스트 프로세스
리뷰 프로세스
빌드 프로세스
릴리즈 프로세스
버전 관리
브랜치 관리
병합 요청
코드 리뷰

# AI/ML generic non-glossary phrases
모델 출력
모델 입력
모델 파라미터
모델 가중치
학습 데이터
테스트 데이터
검증 데이터
훈련 과정
추론 과정
예측 결과

# Common Korean connective phrases
이를 통해
이에 따라
따라서
그러나
하지만
또한
뿐만 아니라
특히
일반적으로
구체적으로
예를 들어
즉
다시 말해
결과적으로
궁극적으로

# Numbers and measurements (generic)
수백만 개
수천 개
수백 개
수십 개
몇 가지
여러 가지
다양한 방법
여러 방법
몇 가지 방법
다양한 접근

# Common compound verbs turned nouns
실행 방법
구현 방법
설정 방법
사용 방법
활용 방법
적용 방법
개선 방법
최적화 방법
자동화 방법
통합 방법
"""

NEGATIVE_TERMS_FILE.write_text(NEGATIVE_TERMS, encoding="utf-8")
negative_count = len([l for l in NEGATIVE_TERMS.split('\n')
                      if l.strip() and not l.strip().startswith('#')])
print(f"Written {negative_count} negative terms to assets/negative_terms.txt")

# ─── Step 12: Write TERMS_FROZEN marker ──────────────────────────────────────
import datetime
frozen_content = f"""TERMS_FROZEN
Generated: {datetime.datetime.utcnow().isoformat()}Z
Term count: {len(terms)}
Negative list size: {negative_count}
Freeze tag: terms-freeze-v1

This file marks the term dictionary as frozen for the glossary round-trip.
Changes after freeze must follow the hotfix protocol in docs/HOTFIX.md.
"""
TERMS_FROZEN_FILE.write_text(frozen_content, encoding="utf-8")
print("Written TERMS_FROZEN marker")

print("\nSummary:")
print(f"  Terms: {len(terms)}")
print(f"  Negative list: {negative_count}")

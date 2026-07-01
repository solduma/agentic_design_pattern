# 작업 계획서 — Agentic Design Patterns 한국어 웹 문서화

> 원본: `pdf/Agentic_Design_Patterns.pdf` (482p, 21개 챕터 + 서문/서론 + 부록 + 용어집/색인, 이미지 65개)
> 목표: AI 엔지니어가 **빠지는 내용 없이** 쉽고 빠르게 이해할 수 있는 **한국어 웹 문서 사이트**
> 근거: `/deep-research`(106 서브에이전트) + adversarial 평가(34건 제기→24건 REAL) + PDF 구조 실측

---

## 0. 확정된 의사결정 (사용자 승인)

| 항목 | 결정 | 근거 |
|---|---|---|
| 빌드 스택 | **Docusaurus 3** (React + MDX + SSG/SPA) | 리서치 "올인원 최적". MDX·Mermaid·사이드바·다크모드 기본 제공. ⚠️ 내부 webpack이라 엄밀히 "Vite" 아님 — 콘텐츠 이관 집중 위해 채택 |
| 번역 깊이 | **자연스러운 한국어 + 핵심 기술용어 영문 병기** | AI 엔지니어 가독성 최우선. `embedding`, `fine-tuning`, `RAG` 등 병기 유지, 코드·주석은 원문 |
| 다이어그램 | **최대한 Mermaid로 재생성** (라이트/다크·한국어 라벨), 재현 불가한 복잡 도식만 원본 PNG 폴백 | 리서치: Mermaid는 doc-rot 해결·SVG·Docusaurus 퍼스트파티 지원 |
| 검색 | **Pagefind** (CJK n-gram 토크나이징 내장, 서버리스) | 아래 §0.5-M10: Algolia는 한국어 형태소 설정을 개발자가 직접 해야 해 부적합 |
| 코드 하이라이팅 | **Prism** (Docusaurus 기본, 별도 설치 불필요) | 아래 §0.5-M11: Shiki는 추가 구성 필요 — 기본값으로 확정해 T4/T5 충돌 제거 |
| 존댓말체 | **합쇼체(–습니다/합니다)로 통일** | 아래 §0.5-H2: "존댓말체"는 모호 → 단일 종결어미로 고정 |
| 색인(Index) | **원서 Index 페이지 미이관 — Pagefind 전문검색으로 대체** | V-9: 책 색인은 영문 슬러그·페이지번호 기반이라 번역 시 죽은 링크만 남음. 전문검색이 우월한 대체재. 사이트에 "색인 대신 검색 이용" 안내. ⚠️ "빠지는 내용 없이"는 **본문·설명 콘텐츠 기준** — 탐색 보조물(페이지번호 색인)은 검색으로 기능 대체하며 이 예외를 명문화 |
| Gemini 트랜스크립트 처리 | **FAQ 부록의 하위 페이지로 편입·번역**(W3-H10) | Index 내 추론 로그(p445–448)는 "에이전트 예시"로서 본문 가치 있음 → 누락 대신 이관. 결정권=agent-extract, manifest에 기록 |

---

## 0.5 Adversarial 평가 — 감사 추적 (상세 수정은 T1~T9 본문에 반영됨)

계획을 5개 관점(일관성·의존성·스택·완결성·품질게이트·비용)으로 공격→검증. **Critical 1 + High 6 + Medium 13** 생존. 각 항목이 반영된 위치:

| ID | 결함 | 반영 위치 |
|---|---|---|
| C-1 | MDX 특수문자(`< > { }`) 미이스케이프 → 빌드 전면 실패 | §5 규약2·8, §5.1 PR게이트 |
| H-1/M-9 | `terms.candidates` 동시 append → SSOT 손실 | §2 T3+T3a, §5 규약6 |
| H-2 | 문체 drift | §0 결정, §2 T3a(기준번역본), §7 |
| H-3 | Mermaid 한글 tofu(□) 폰트 | §2 T2, §7 |
| H-4 | Appendix F(14p) 본문 없음 무감지 | §1.2, §2 T1, §7 |
| H-5 | "1:1 매핑" QC 실행 스크립트 없음 | §2 T1(섹션ID/체크섬), §7 `check_coverage.py` |
| H-6 | 용어 grep이 챕터 간 변형 미검출 | §7 용어 변형 스캐너(blocking) |
| M-1 | T7 의존성 오류(T5 누락) | §3 T7 blocked-by, §6 |
| M-2 | DiagramPlaceholder ID 전역 고유성 | §2 T1(전역 ID), §5 규약5 |
| M-3 | 섹션 수 "44" 오류 | §1.1·§1.2·§4 → T1 실측값 |
| M-4/M-5 | FAQ·Gemini 트랜스크립트 미등록 | §1.2, §2 T1(처리방침 필드) |
| M-6 | 병기 "최초 등장" 챕터 단위 오해 | §2 T3(`first_chapter`), §5 규약2 |
| M-7 | 교차참조 구조화 마커 없음 | §2 T1(레지스트리), §5 규약5, §7 |
| M-8 | T6 트리거 모호 | §3 T6 → §5.1 PR게이트로 편입 |
| M-10 | Algolia 한국어 토크나이징 | §0 결정(Pagefind) |
| M-11 | Prism/Shiki 미결 | §0 결정(Prism) |
| M-12 | 산문 완결성 기계검증 없음 | §2 T1(단락/토큰 수), §7 단락비율 |
| M-13 | Mermaid 의미 정확성 미검증 | §6, §7 side-by-side 대조 |

> **verdict**: 아키텍처(Docusaurus + 병렬 워크트리 + SSOT)는 건전. C-1·H-1은 fan-out 전 필수 수정 — 아래 본문에 모두 반영 완료.

### 2차 재검수 반영 (v2, 19건 제기 → 12건 REAL, Critical 0 / High 10 / Medium 2)
게이트 조건("High 이상 전부 수정")에 따라 아래 HIGH를 모두 반영:

| ID | 결함 | 반영 위치 |
|---|---|---|
| V-1 | Ch1 기준번역본 생성 태스크 부재 → 병렬성 붕괴·드리프트 전파 | §2 **T5.0** 신설, §3·§4·§9 |
| V-2 | T7이 T5에 불필요하게 의존 → 크리티컬 패스 연장 | §3 T7 `blocked-by T1`로 수정, §4·§9 |
| V-3 | T5 완료 신호 미정의 | §3·§9 `check_t5_coverage.py` |
| V-4 | §5.1/§7 게이트 스크립트 오너 없음 | §2 **T2a**(게이트 스크립트)·**T9a**(QC 스크립트) 신설 |
| V-5 | 단락비율 게이트 우회 가능(내용 누락) | §5.1·§7 **토큰비율 ≥0.75** 서브게이트 |
| V-6 | 용어 변형 스캐너가 미등록 신조어 못 잡음 | §7 **allowlist 방식** + §5.1 term-drift 게이트 |
| V-7 | 합쇼체 체커 비산문 줄 오탐 | §7 필터 규칙 명시 |
| V-8 | 교차참조 grep이 영문 `Figure/Table/Appendix` 미탐지 | §7 패턴 세트 확장 |
| V-9 | Index 처리방침 미결(죽은 링크 위험) | §0·§1.2 결정(Pagefind 대체) |

> **v2 verdict**: 잔존 결함은 대부분 **오케스트레이션 순서·게이트 소유권·스크립트 정확도** 문제 — 아키텍처 재설계 불필요, 태스크 2개(T2a·T9a·T5.0) 추가와 게이트 명세 정교화로 해소. 아래 본문에 반영 완료.

### 3차 재검수 반영 (v3=W3, 23건 제기 → 19건 REAL, Critical 1 / High 11 / Medium 7)
v2 수정이 새 태스크(T2a/T5.0/T9a)를 만들며 노출한 결함면. 근본 원인 4개로 통합 해소:

| ID | 결함 | 반영 위치 |
|---|---|---|
| W3-C1/H6/H8 | term-drift 게이트 데드락(탈출로 없음)·오탐 폭풍 | T3a **hotfix 프로토콜**(24h SLA·waiver 레이블) + T2a-term **정밀도 필터** |
| W3-C2/H3 | T5.0 승인자·SLA·폴백 미명세 | §3 T5.0 승인 프로토콜(`@maintainer`·24h·폴백), §4 수용기준 |
| W3-H1/H2 | T2a가 T3a에 통째 묶여 크리티컬 패스 연장 | **T2a-core**(blocked-by T1, T3a와 병렬) / **T2a-term**(blocked-by T3a) 분리 |
| W3-H4 | T8이 T9a 완료 전 종료 가능 | T8 blocked-by에 **T9a 추가** |
| W3-H5 | T2a·T9a 소유권 경계 모호 | T2a=합성 스텁 통과, T9a=실출력 FP/FN 임계 이하로 경계 |
| W3-H6(계약) | manifest para/token 의미 미정의 | T1이 **단락/토큰 정의 고정**(코드 제외, tiktoken cl100k_base) |
| W3-H7 | 토큰비율 토크나이저 미지정 | **tiktoken cl100k_base 고정** + 임계값 경험 검증 |
| W3-H9 | Glossary↔terms.json 불일치 | Glossary를 **terms.json에서 자동 생성** + §7 동기화 검사 |
| W3-H10 | Gemini 트랜스크립트 처리 미결 | §0 결정: **FAQ 하위로 translate**, agent-extract 확정 |
| W3-M1/M2/M3 | 스텁 안내문·중복 델타·Index 참조 규칙 | T1 스텁 안내문·`duplicate_delta_bytes`, §5·§7 Index 참조 처리 |

> **v3 verdict**: Critical/High 전량이 **순서·오너십·스크립트 명세**의 정교화로 해소(아키텍처·스택 불변). 반영 후 High+ 잔존 0을 목표로 4차 재검수 실시.

### 4차 재검수 반영 (v4=W4, 15건 제기 → 13 REAL, Critical 0 / High 5 / Medium 8)
게이트 기계장치의 세부 결함. 모두 반영:

| ID | 결함 | 반영 위치 |
|---|---|---|
| W4-H1 | T9a가 실출력 하드닝 때문에 T5에 이행 의존(T8 선행 불가) | **T9a-pre(T5무관, T8선행) / T9a-post(T5후, T9만 block)** 분리 |
| W4-H2 | per-PR term-drift 빈도 3회↑ → sparse 신조어 false negative | per-PR 빈도 미적용(≥1), 3회↑ 임계는 §7 전체사이트만 |
| W4-H3 | token-ratio 0.75가 BPE 팽창으로 죽은 게이트 | 경험 보정 `μ−2σ`·양방향, 25% 절삭 테스트로 검증 |
| W4-H4 | terms-hotfix 승인자가 T5 구간 부재(agent 종료됨) | **T3a-hotfix-watch** 상시 `@maintainer` + 에스컬레이션 |
| W4-H5 | terms.json에 definition 없어 Glossary 산문 정의 유실 | `definition_ko/_en` 필드 추가, 자동 생성에 정의 포함 |
| W4-M1/M2/M3/M6 | waiver 재검사·폴백 교정 오너·Glossary 항등식·coverage 필터 | post-merge 재검사, T5.0-fix, round-trip 검증, disposition 제외 |

> **v4 verdict**: High 5건 전량이 게이트 파라미터·태스크 분할로 해소. 잔존 Medium은 안전망(T9 전체 스캔) 존재. 반영 후 5차 재검수로 High+ 0 확인.

### 5차 재검수 반영 (v5=W5, 17건 제기 → 10 REAL, Critical 0 / High 4 / Medium 6)
남은 High는 전부 **완결성 게이트·style_checker 파라미터 정밀도**에 국한(아키텍처 안정). 모두 반영:

| ID | 결함 | 반영 위치 |
|---|---|---|
| W5-H1 | token-ratio μ/σ 보정에 쓸 실번역 샘플이 T2a-core 시점에 없음(부트스트랩) | **T2a-core-scaffold(느슨)/T2a-core-calibrate(Ch1 실측, blocked-by T5.0)** 분리, T5.1~N은 calibrate에 의존 |
| W5-H2 | style_checker가 `:::` 어드모니션 제목 false-fail | §7 필터에 `:::` skip 규칙 추가 |
| W5-H3 | 단일 전역 μ가 코드/산문 혼동 → 정상 확장 false-fail | **code_ratio 2계층(코드≥30%/산문) μ/σ**, 상한 μ+3σ |
| W5-H4 | hotfix 승인 인간(@maintainer)이 크리티컬 패스 병목 재도입 | **자동 검증 통과 시 봇 자율 머지**, @maintainer 알림 전용 |
| W5-M2/M3/M5 | Glossary 공유파서 맹점·waiver 재검사 행위자·AppendixG 자동병합 | 독립 파서+해시, agent-tr-{sec} 자동 할당, `duplicate_delta>0` 수동검토 콜아웃 |

> **v5 verdict**: High가 6→5→4로 수렴, 잔존은 모두 QC 게이트 파라미터의 국소 조정. 반영 후 6차 재검수로 High+ 0 최종 확인.

### 6차 재검수 결과 (v6=W6) — ✅ **Critical 0 / High 0 (게이트 통과)**
10건 제기 → 7 REAL, **전부 Medium**(High/Critical 0). 각 Medium은 T9 전체사이트 스캔이 안전망. 그중 견고화가 값싼 3건 + 콘텐츠 손실 방지 2건을 추가 반영:

| ID | 결함(Medium) | 반영 위치 |
|---|---|---|
| W6-M1 | Ch1 단독 보정 시 코드중심 계층 표본 부족(σ 붕괴) | T2a-core-calibrate 영어 토큰 비율 사전분포 시드 |
| W6-M2 | hotfix 봇이 `ko` 의미검증 없이 자동 머지 | 신규-`ko` hotfix는 `@maintainer` 리뷰 필수, alias/스키마만 자동 |
| W6-M3 | style_checker가 어드모니션 **본문**은 미필터 | `:::` 블록 전체 상태 추적 제외 |
| W6(누락) | Conclusion 등에 `omit-with-notice` 오지정 시 조용한 누락 | `omit-with-notice`는 Index만 화이트리스트, 그 외 검증 오류 |
| W6(누락) | 각주·사이드바·에피그래프 보존 미명시 | §5 규약4에 포함 + T1 각주 수 기록 |

> **최종 verdict**: 6회 adversarial 검수(누적 34+24+19+15+17+10건 제기)를 거쳐 **High 이상 잔존 0으로 수렴**. 아키텍처(Docusaurus+병렬 워크트리+SSOT)는 6회 내내 불변, 수정은 전부 순서·오너십·게이트 파라미터의 정교화였음. 잔존 Medium은 구현 단계 튜닝 사항이며 T9 전체 스캔이 백스톱. **계획 실행 준비 완료.**

---

## 1. Plan (전체 개요)

### 1.1 산출물 정의
- Docusaurus 3 정적 문서 사이트 (`docs/` 하위 MDX 문서 — **정확한 수는 T1이 실측 산출**, 고정값 사용 금지)
- 좌측 사이드바 = 원서 목차(Part 1–4 + 부록), 우측 TOC, **Pagefind** 검색, 라이트/다크 토글
- 모든 챕터: 한국어 본문 + 원문 코드(Prism 강조) + Mermaid/PNG 다이어그램 + "이 장의 핵심" 콜아웃
- Glossary 페이지: 영-한 대응표 = 번역 일관성의 **SSOT(단일 진실 원천, `terms.json`)**

### 1.2 콘텐츠 인벤토리 (PDF 실측 — 평가로 정정됨)
| 구분 | 내용 | PDF 페이지 | 비고 |
|---|---|---|---|
| 전면부 | Foreword, Preface, Frameworks Intro | 7–22 | 3섹션 |
| Part 1 | Ch1 Prompt Chaining … Ch7 Multi-Agent | 23–131 | |
| Part 2 | Ch8 Memory … Ch9 Learning & Adaptation | 132–166 | |
| Part 3 | Ch10 MCP … Ch13 Human-in-the-Loop | 167–212 | |
| Part 4 | Ch14 RAG … Ch21 Exploration | 213–348 | |
| 부록 | Appendix A·B·C·D·E·G | 349–420 | ⚠️ **F 없음**, G 중복 |
| 후면부 | Conclusion, Glossary, Index, **FAQ** | 421–482 | Glossary/Index 중복 존재 |

**실측 확정 사항 (T1이 재검증):**
- **고유 섹션 ≈ 34개**(전면3 + 챕터21 + 부록6 + 후면4). "44"는 오류였음.
- **Appendix F(14p)는 목차에만 있고 본문 부재** — E(p399–403) 다음 바로 G(p404). → **T1이 안내 콜아웃을 담은 스텁 MDX를 정식 경로에 생성**("이 부록은 원본 PDF에서 확인되지 않았습니다 (Appendix F, pp.X–Y)"). check_coverage가 스텁 존재 + 안내 문구 존재를 검사(W3-M1).
- **"Appendix G" p404·p410 두 번 수록**(MD5 상이) → **T1이 양쪽 추출→diff→manifest `duplicate_delta_bytes` 기록→합집합(또는 뒤 페이지)을 정본 채택 + 델타 주석**. 고유 콘텐츠 유실 방지(W3-M2).
- **Glossary(p421–436)·Index(p437–448)가 p449–482에 통째 중복**(Glossary MD5 동일) → 중복 무시. **Glossary는 1회 이관, Index 페이지는 미이관(§0 결정 V-9 — Pagefind 대체)**.
- **미등록 콘텐츠**: FAQ(p477–482, 6p) → `translate`로 이관. Gemini 추론 트랜스크립트(p445–448) → **`translate`, FAQ 부록의 하위 페이지로 편입**(§0 결정 W3-H10). T1이 T5 범위 정의에 전파.
- **이미지 65개**(대부분 2048×1445) → 전역 고유 ID 부여.
- 텍스트/코드는 PyMuPDF로 **깨끗하게 추출** → 비전 모델(Zerox 등) 불필요, 경량 파이프라인.

### 1.3 아키텍처 파이프라인
```
PDF ─(PyMuPDF)→ manifest.json(섹션ID·체크섬·이미지ID·교차참조·처리방침·단락수)
                + 챕터별 원문 텍스트/코드 + 이미지 PNG
   │
   ├─ T3a term-mining → terms.json FREEZE ─┐
   │                                        ▼
   ├─ [번역 서브에이전트 × N] ─(MDX 이스케이프 + 합쇼체 + SSOT 참조)→ 챕터 MDX
   │        └─ 챕터별 PR 게이트: MDX 컴파일 체크 + 코드 diff(구 T6)
   │
   ├─ [다이어그램 에이전트] 원본 PNG ─(구조 판독)→ Mermaid 에셋 or PNG 폴백 (ID 기반)
   │
   └─ 사이트 통합(placeholder 치환) → QC 스크립트 게이트 → 배포
```

---

## 2. Divide — 독립 병렬 태스크 (상호 의존 없음)

동시 착수 가능:

- **T1. 추출 파이프라인 & manifest** — `scripts/extract.py`로 섹션별 텍스트·코드·이미지(PNG) 분리. 산출 `assets/manifest.json`에 다음을 **모두** 포함(평가 M-2·M-3·M-4·M-5·M-7·M-12·H-4·H-5 일괄 해소):
  - **섹션 레코드**: `{id, title, page_range, checksum, para_count, token_count, status, disposition}` — `status`는 `ok`/`MISSING`/`DUPLICATE`.
  - **카운팅 의미 고정(W3-H6)**: `para_count` = 하나 이상의 빈 줄로 구분된 텍스트 블록 수(코드 블록 제외). `token_count` = **코드 블록 제거 후 순수 텍스트를 `tiktoken cl100k_base`로 인코딩한 토큰 수**(원문·번역 동일 토크나이저·전처리). 이 정의를 manifest 스키마 주석에 명시 → T2a `check_ratio.py`가 그대로 소비(계약 고정).
  - **TOC↔본문 교차검증 + 스텁 생성(H-4/W3-M1)**: 목차 항목마다 본문 존재 대조. 부재 시 `MISSING` + **안내 콜아웃 스텁 MDX 생성**.
  - **중복 델타 처리(W3-M2/W5-M5)**: `DUPLICATE`이며 MD5 상이 시 양쪽 diff→`duplicate_delta_bytes` 기록→합집합/뒤 페이지를 정본 채택. **`duplicate_delta_bytes > 0`이면 해당 섹션에 `⚠️ 수동 검토 필요` 콜아웃 삽입 + T1 이슈에 diff 첨부**(의미 충돌 자동 병합 방지).
  - **이미지 레지스트리**: 65개 전역 고유 ID `img-p{페이지}-{idx}` + 소속 섹션 + 원본 캡션(M-2).
  - **교차참조 레지스트리**: 그림 번호·섹션 제목 ↔ Docusaurus 앵커 슬러그 매핑(M-7).
  - **처리방침 필드(`disposition`)**: `translate`/`keep-english`/`omit-with-notice`. **`omit-with-notice` 허용 대상은 Index 단 하나로 화이트리스트 고정 — 그 외 섹션에 부여 시 T1 검증 오류(W6)**. 전면부(Foreword/Preface/Frameworks Intro)·Conclusion·모든 챕터·부록·FAQ는 반드시 `translate`. Gemini 트랜스크립트=`translate`(FAQ 하위, W3-H10). agent-extract가 확정·기록하되 화이트리스트로 강제(M-4·M-5).
  - **본문 요소 보존(W6)**: 각주·사이드바·에피그래프도 "본문 100% 이관" 대상. T1이 각주 문단 수를 별도 필드로 기록해 §5.1 완결성 게이트가 누락을 잡도록 함(§5 규약4 참조).
- **T2. Docusaurus 스캐폴딩** — 프로젝트 초기화, `docusaurus.config.js`:
  - locale=ko **단일 로케일**(다국어 i18n 파이프라인 아님), 라이트/다크.
  - **Prism** 확정(Shiki 미사용) — binding decision, `CONTRIBUTING.md`에 명시(M-11).
  - **Pagefind** 검색 통합(Algolia 미사용) — 빌드 후 인덱싱 스텝(M-10).
  - **Mermaid**: `fontFamily:"'Noto Sans KR',sans-serif"` 설정 + `src/css/custom.css`에 Noto Sans KR `@import`(H-3).
  - 완료기준: `npm run build` 통과 + 한글 Mermaid 샘플이 tofu 없이 렌더.
- **T2a-core-scaffold. 게이트 스크립트(용어 무관) & CI 배선** (신규; blocked-by: **T1만** → T3a와 병렬, W3-H1/H2) — terms.json 불필요 스크립트 일체 소유·구현 + GitHub Actions 연결: `check_mdx.py`(단독 MDX 컴파일), `check_code_integrity.py`(코드 라인 diff), `check_ratio.py`, `check_coverage.py`, `check_t5_coverage.py`, `xref_checker.py`, `style_checker.py`(합쇼체+비산문 필터 — **`:::` 어드모니션 라인 skip 규칙 포함**, W5-H2).
  - **완결성 비율(W4-H3/W5-H3)**: 토크나이저=tiktoken cl100k_base 고정. 단락 비율 ≥0.85 유지(코드 무관 산문 누락 방어). 토큰 비율은 **초기엔 느슨한 플레이스홀더 하한**(예: 0.5)과 **25% 절삭 합성 챕터에서 실패하는 자가 테스트**만 탑재 — 정밀 임계는 T2a-core-calibrate가 채움.
  - 완료기준: 합성 스텁으로 exit 0/1 + 절삭 자가 테스트 통과 + CI에서 T5 PR 자동 실행.
- **T2a-core-calibrate. 완결성 임계 실증 보정** (신규, W5-H1; blocked-by: **T5.0 머지** — 즉 Ch1이 실제 번역 corpus) — Ch1 실제 토큰 비율로 **섹션 아키타입별 μ/σ 산출**: manifest `code_ratio`로 **코드중심(≥30%)/산문중심 2계층 분리**, 각 계층 μ/σ 기록(W5-H3). 게이트는 `check_ratio.py`가 `code_ratio`로 계층 선택, **하한 `μ−2σ`·상한 `μ+3σ`**, `tolerance` 명명 상수.
  - **희소 계층 보정(W6-M1)**: Ch1은 산문 우세라 코드중심 계층 표본이 n≤1일 수 있음 → **manifest의 원문 영어 토큰 비율(T1 시점 산출 가능)을 코드중심 계층의 사전분포로 시드**하고 Ch1을 베이지안 1회 업데이트로 취급(σ=0/NaN로 게이트가 죽거나 폭주하는 것 방지). 계층별 최소 표본 미달 시 사전분포 폭을 유지.
  - **T5.1~N은 이 태스크에 blocked-by**(scaffold 아님) → 잘못 보정된 게이트로 팬아웃 방지.
- **T2a-term. 용어 게이트 스크립트** (신규; blocked-by: **T3a**) — `term_variant_scanner.py`(allowlist) + term-drift 게이트 배선. **정밀도 필터(W3-H8)**: (1) 최소 복합어 길이(3음절↑ 또는 2형태소↑), (2) 한국어 불용어·일반 산문 명사 제외 목록, (3) T3a 무해 복합어 네거티브 리스트.
  - **빈도 필터 이원화(W4-H2)**: 코퍼스 3회↑ 빈도 임계는 **PR 단위에서 false negative**(단일 챕터엔 신규 용어가 1~2회뿐)를 유발하므로 **§5.1 per-PR 게이트에서는 빈도 필터 미적용(≥1, 길이·불용어·네거티브만)**, "3회↑" 임계는 **§7 T9 전체사이트 스캔에서만** 적용. 또는 머지 누적 빈도 카운터에 임계 적용.
  - 완료기준: T3a term-mining 샘플에서 per-PR false-positive율·false-negative율이 임계 이하.
- **T3. 용어집 SSOT 초안** — 원서 Glossary(p421–436) + 색인 상위어로 영-한 대응표 작성. `terms.json` 스키마: `{en, ko, first_chapter, aliases[], definition_ko, definition_en}` — `first_chapter`는 병기 노출 챕터(M-6). **`definition_ko`는 원서 Glossary의 산문 정의를 한국어로 담음**(W4-H5) → 15p 정의가 자동 생성 Glossary에서 유실되지 않도록 보장.
- **T3a. 번역 전 term-mining pass + hotfix 프로토콜** (신규, H-1/M-9) — 전 챕터 원문을 스캔해 후보 용어를 사전 수집·정규화하여 `terms.json`에 병합 후 **freeze**. **형태소 분석 기반 기술 명사 추출기**로 `aliases[]` 후보 + T2a-term용 **무해 복합어 네거티브 리스트**를 사전 생성.
  - **freeze 후 hotfix 경로(W3-C1/H6, W5-H4 자동화)**: freeze는 무분별 append를 막을 뿐 **완전 동결이 아님**. 누락 용어 발견 시 **`terms-hotfix` PR**(aliases[]/신규 항목 추가). **인간을 크리티컬 패스에서 제거** — **alias/스키마 전용 변경**(기존 항목 `ko` 불변)은 자동 검증 CI(정밀도 필터·네거티브·스키마) 통과 시 `agent-gates-term`이 **자율 머지**. **신규 항목의 `ko`(신규 번역)가 포함된 hotfix는** 의미 검증이 필요하므로 **`@maintainer` 리뷰 필수**(W6-M2 — 자동검증은 구조만 볼 뿐 `ko` 의미 오류를 못 잡아 SSOT·자동생성 Glossary 오염 위험). 별도 상시 이슈 `T3a-hotfix-watch`가 봇 + 신규-ko 리뷰 큐를 T5 기간 유지.
  - **term-drift-waiver 재검사(W4-M1/W5-M3)**: `terms-hotfix` 자동 머지 시 **post-merge GitHub Actions**가 `term-drift-waiver` 커밋을 조회→해당 MDX에 term-drift 재실행→실패 시 **해당 챕터 번역 에이전트(agent-tr-{sec}, T5 기간 활성)에게 수정 PR 자동 할당**(종료된 agent-glossary에 의존 안 함). waiver 오픈 목록은 project board 추적.
  - **Glossary는 terms.json에서 생성(W3-H9)**: 사람용 Glossary 페이지를 T5가 자유 번역하지 않고 **`terms.json`의 `{en, ko, definition_ko}`에서 pre-build 스크립트로 자동 생성**(정의 단락 포함, W4-H5) → 두 SSOT 불일치 원천 제거. (T5 Glossary 서브에이전트 불필요.)
- **T4. 컴포넌트 라이브러리** — MDX 컴포넌트: 핵심요약 콜아웃, "원문 펼치기" details, `<Diagram id>` 래퍼, `<CrossRef id>`(교차참조), 챕터 네비 카드. **Prism 기반**으로 작성(T2 결정 준수).

> T3·T3a는 번역 선행조건이지만 초안·마이닝 자체는 독립 착수 가능. T5는 `terms.json` freeze + T2a 게이트 준비 후 시작.

---

## 3. Sequence — 의존성 있는 태스크 (순서 고정)

```
T1 ──┬────────────────────────────────────────────> T7(다이어그램 에셋) ──────────────┐
     ├─ T2a-core-scaffold(느슨한 게이트) ─┐                                            │
T3→T3a(freeze,hotfix 자동머지)─┬─ T2a-term ┤   ┌─ T9a-pre(구조 스크립트) ──────────────┤
T2 ──────────────────────────┤            ┼───┤                                      ▼
T4 ──────────────────────────┘            │   └> T5.0(Ch1+승인) → T2a-core-calibrate(Ch1 실측 μ/σ)
                                           │            └───────────────> T5.1~N ─┬─> T8 → T9 → T10
                                           │   (T2a-core-scaffold∥T3a 병렬)        └> T9a-post(실출력 하드닝)─┘
                                           └ §5.1 PR게이트: MDX컴파일+코드diff+완결성(계층별 μ/σ)+term-drift
```

- **T5.0. Ch1 기준번역본 생성 + 승인** (신규, V-1; blocked-by: T1, T3a, T4, T2a-core, T2a-term) — Chapter 1을 먼저 단독 번역→`docs/reference/chapter1-style-ref.mdx`. **나머지 모든 T5.x를 block**. **승인 프로토콜 명세(W3-C2/H3)**: 승인자=지정 GitHub `@maintainer`(§4 수용 기준에 handle 기재); 승인 아티팩트=해당 PR의 "Approved" 리뷰 + 브랜치 보호 1 required review; **24h SLA** — 미응답 시 프로젝트 리드 에스컬레이션; **폴백**: SLA 초과 시 스타일 의존도 낮은 섹션(부록·FAQ)은 미승인 Ch1을 임시 레퍼런스로 착수하되, 폴백 발동 시 **`T5.0-fix` 교정 태스크(owner=agent-tr-ch1, T8 blocked-by에 조건부 추가)**로 승인본 확정 후 해당 섹션 문체 재정렬 — 이것이 완료돼야 T8 기동(W4-M2).
- **T5.1~N. 챕터 번역 fan-out** (blocked-by: T5.0, **T2a-core-calibrate**, T1, T3a, T4, T2a-term) — 섹션 1개 = 서브에이전트 1개, 워크트리 격리. §5 규약. 각 PR은 §5.1 게이트 통과해야 머지. calibrate 완료 후 착수 → 보정된 완결성 게이트로 검증(W5-H1).
  - **T5 완료 신호(V-3)**: 마지막 PR 머지 후 `check_t5_coverage.py`가 manifest 섹션 ID ↔ main MDX 1:1 대조하여 exit 0일 때만 T5 부모 이슈 종료 → T8 기동. **`disposition`이 `omit-with-notice`(Index)이거나 auto-generate(Glossary)인 섹션은 대조 대상에서 제외**(W4-M6) — T5가 생성하지 않는 섹션이므로.
- **T7. 다이어그램 에셋 생성** (blocked-by: **T1**) — manifest 이미지 ID 기준 독립 에셋 생성만(V-2). T1 완료 즉시 T5와 병렬.
- **T9a-pre. QC 구조 스크립트** (신규; blocked-by: T2a-core, T2a-term) — **T5 출력이 불필요한** 스크립트를 완성: Glossary↔terms.json 동기화 검사(W3-H9), 교차참조·coverage 등. **T5와 병렬로 T8 이전에 완료** → T8의 실질적 선행조건.
- **T9a-post. QC 스크립트 실출력 하드닝** (신규; blocked-by: **T5(완료신호)**, W4-H1) — 변형 스캐너·문체 체커의 FP/FN 임계를 **T5 실제 출력 샘플**로 하드닝. T5 완료 후에만 가능하므로 **T8을 block하지 않고 T9만 block**(T8 통합과 병렬 진행). 경계(W3-H5): T2a-*=합성 스텁 통과, T9a-post=실출력 FP/FN 임계 이하.
- **T8. 사이트 통합** (blocked-by: T2, T5(완료신호), T7, **T9a-pre**(W4-H1)) — MDX 배치, `<Diagram id>`/`<CrossRef id>` 실제 에셋·앵커 치환, 사이드바(순서=manifest Part 구조) 확정, Pagefind 인덱싱.
- **T9. QC/일관성 검증** (blocked-by: T8, **T9a-pre, T9a-post**) — §7 스크립트 게이트 전항 통과.
- **T10. 배포** (blocked-by: T9) — `docusaurus build` + Pagefind 인덱스 + 정적 호스팅.

> **구 T6**은 T5 PR 게이트로 편입(§5.1); 스크립트 초안은 **T2a-core/term 소유**, 실사용 하드닝은 **T9a 소유**(경계=W3-H5).

---

## 4. GitHub 이슈 등록 계획 (CLAUDE.md Step 4)

태스크당 이슈 1개. 각 이슈에 **Goal/Acceptance · Owner · blocks/blocked-by** 명시.

| # | 이슈 | Owner | blocked-by | 수용 기준(요약) |
|---|---|---|---|---|
| T1 | 추출 파이프라인 & manifest | agent-extract | — | 섹션 실측 + manifest(ID·체크섬·para/token·이미지ID·교차참조·처리방침·MISSING) + 65 PNG |
| T2 | Docusaurus 스캐폴딩 | agent-scaffold | — | build 통과, Prism·Pagefind·Noto Sans KR Mermaid 동작 |
| T2a-core-scaffold | 게이트 스크립트(용어무관) & CI | agent-gates | T1 | 7종 스크립트 exit 0/1 + 절삭 자가테스트 + `:::` 필터 + T5 PR 자동 실행 |
| T2a-core-calibrate | 완결성 임계 실증 보정 | agent-gates | T5.0 | Ch1 실측으로 code_ratio 계층별 μ/σ 기록, tolerance 명명 상수 |
| T2a-term | 용어 게이트 스크립트 | agent-gates-term | T3a | `term_variant_scanner.py` + 정밀도 필터 + hotfix 자동 머지 봇 |
| T3 | 용어집 SSOT 초안 | agent-glossary | — | 영-한 표 + `terms.json`(first_chapter·aliases·**definition_ko** 포함) |
| T3a | term-mining & freeze + hotfix 프로토콜 | agent-termmine | T1,T3 | 후보 병합·freeze + `terms-hotfix` 자동검증·머지 절차 + definition_ko 해시 |
| T3a-hotfix-watch | hotfix 자동 머지 봇 유지 | agent-gates-term | T3a | T5 전 기간 자동검증·자율머지, `@maintainer`는 알림 전용 |
| T4 | MDX 컴포넌트 | agent-components | — | 콜아웃·details·Diagram·CrossRef·네비 동작 |
| T5.0 | Ch1 기준번역본 + 승인 | agent-tr-ch1 | T1,T3a,T4,T2a-core-scaffold,T2a-term | `@maintainer` 1 required review + 24h SLA·폴백 + `chapter1-style-ref.mdx` 머지 |
| T5.0-fix | (폴백 시) 문체 교정 패스 | agent-tr-ch1 | T5.0 | 폴백 미발동 시 skip-close; T8 blocked-by에 상시 포함 |
| T5.x | 챕터 번역 (섹션별 서브이슈) | agent-tr-{sec} | **T5.0**,**T2a-core-calibrate**,T1,T3a,T4,T2a-term | 본문 100% 이관, §5.1 게이트 통과 |
| T7 | 다이어그램 에셋 생성 | agent-diagrams | **T1** | 65개 ID별 Mermaid/PNG 에셋 + 한국어 캡션 |
| T9a-pre | QC 구조 스크립트(T5 무관) | agent-qc-scripts | T2a-core,T2a-term | Glossary 동기화·교차참조·coverage 스크립트, T5와 병렬 완료 |
| T9a-post | QC 스크립트 실출력 하드닝 | agent-qc-scripts | T5(완료신호) | 변형·문체 FP/FN 임계 이하(실출력 기준), T8과 병렬 |
| T8 | 사이트 통합 | agent-integrate | T2,T5(완료신호),T7,T9a-pre,**T5.0-fix** | placeholder 치환·사이드바·Pagefind |
| T9 | QC/검증 | agent-qc | T8,T9a-pre,**T9a-post** | §7 스크립트 게이트 전항 통과 |
| T10 | 배포 | agent-deploy | T9 | 프로덕션 빌드 배포 |

---

## 5. Fan-out 실행 규약 (CLAUDE.md Step 5 — 워크트리 병렬)

- 각 태스크는 `feature/<issue>-<slug>` 브랜치 + 전용 git worktree(`isolation: "worktree"`).
- 블로킹 의존성이 열려 있으면 착수 금지 — 머지 후 시작.
- **챕터 번역 서브에이전트 공통 프롬프트 규약** (일관성 = 최우선):
  1. **입력**: 해당 섹션 원문 + **freeze된 `terms.json`** + **Chapter 1 기준 번역본**(문체 레퍼런스, H-2) + manifest 섹션 레코드.
  2. **번역 규칙**: 자연스러운 한국어 **합쇼체(–습니다/합니다) 통일**. 핵심 기술용어는 `terms.json`의 `first_chapter`가 **본 챕터인 경우에만** `한국어(English)` 병기, 그 외 챕터는 한국어 단독(M-6). 고유명사·프레임워크명(LangChain, ADK 등) 원문 유지.
  3. **코드**: 코드 라인 **절대 불변**, 주석만 한국어 번역(선택). 언어 태그 정확히(` ```python `).
  4. **구조**: 원서 소제목·목록·표·**각주·사이드바·에피그래프 100% 보존**(W6 — 각주는 Docusaurus 각주 문법으로 이관, T1이 각주 수를 기록해 완결성 게이트가 검증). 챕터 상단 "이 장의 핵심" 3–5줄 콜아웃.
  5. **마커**: 이미지 위치에 `<Diagram id="img-p{페이지}-{idx}"/>`(manifest ID 그대로, 자체 생성 금지, M-2). 교차참조는 인라인 텍스트 대신 `<CrossRef id="..."/>`(M-7). **Index/색인 참조**는 표준 대체 문구로 치환("이 사이트의 검색 기능 이용", W3-M3).
  6. **MDX 안전(C-1)**: 산문 내 `<`, `>`, `{`, `}`는 반드시 이스케이프(`&lt;` `&gt;` `&#123;` `&#125;`) 또는 백틱 인라인 코드로 감쌈. JSX 컴포넌트를 쓰지 않는 순수 산문 챕터는 `.md`로 저장.
  7. **출력**: `docs/<part>/<section>.mdx`. 번역 중 `terms.json`에 없는 용어가 필요하면 **직접 append 금지 — 대신 `terms-hotfix` PR을 별도로 열어** 글로서리 오너 승인(24h SLA)을 받음(W3-C1). 해당 챕터 PR엔 `term-drift-waiver` 레이블로 임시 진행, hotfix 머지 후 게이트 재실행.
  8. **Glossary 섹션은 T5 대상 아님**: `terms.json`에서 자동 생성됨(W3-H9) — 번역 에이전트가 손대지 않음.

### 5.1 챕터 PR 머지 게이트 (구 T6 편입 — 스크립트는 T2a-core/term 소유)
각 T5 PR은 아래를 통과해야 머지 가능:
- **MDX 컴파일 체크**: `@mdx-js/mdx`로 해당 파일 단독 컴파일 성공(C-1 조기 검출). ※단독 컴파일은 링크/admonition 등 사이트 전역 오류는 못 잡으므로, T9 전역 `docusaurus build`가 최종 방어선.
- **코드 무결성 diff**: 원문 코드 블록 대비 코드 라인 변경 0(주석 제외).
- **완결성 이중 게이트 (M-12/V-5/W4-H3/W5-H1·H3)**: 단락비율 ≥ 0.85 **AND** 토큰비율(tiktoken cl100k_base)이 **섹션 아키타입별 보정 구간**(하한 `μ−2σ`, 상한 `μ+3σ` — 한국어 확장 감안) 내. 절대 0.75 아님. 임계는 **T2a-core-calibrate가 Ch1 실측으로 채우기 전까지 플레이스홀더**이며, T5.1~N은 calibrate 완료 후 착수.
- **term-drift 게이트 (V-6/W4-H2, per-PR)**: `terms.json`(표준형+aliases)에 없는 한국어 기술 명사 후보 발견 시 실패. **per-PR에서는 빈도 필터 미적용(≥1)**, 길이·불용어·네거티브 리스트로만 오탐 억제(단일 챕터 신규 용어 누락 방지). `term-drift-waiver` 레이블 시 hotfix 대기로 1회 통과 → post-merge 재검사(§2 T3a).

---

## 6. 다이어그램 처리 판단 기준 (T7)

이미지별 의사결정(manifest ID 단위):
1. **플로우/시퀀스/상태/클래스/ER 구조인가?** → Mermaid 재생성(한국어 라벨, 라이트·다크).
2. **복잡 아키텍처·스크린샷·비정형 그래픽인가?** → 원본 PNG 재활용 + 한국어 캡션 + alt.
3. **재활용 시 개선 여지?** → 캡션/주석 보강, 필요 시 웹검색으로 대체 도식 확보 후 검토.
- **의미 정확성 확인(M-13)**: Mermaid 재생성 시 원본 PNG와 side-by-side로 **노드 수·엣지 수·방향 일치** 확인. 불일치 시 PNG 폴백으로 자동 강등 또는 사람 리뷰 표시.
- 모든 다이어그램: 캡션·alt 한국어 필수, 원본 페이지 번호 주석 보존(추적성).
- 산출은 ID 기반 독립 에셋 — T8이 `<Diagram id>` placeholder에 연결.

---

## 7. QC / 일관성 검증 — 스크립트 게이트 (T9)

각 항목은 **실행 스크립트로 기계 검증**(수동 눈검사 금지). 하나라도 실패 시 CI exit≠0 → 배포 차단.

- [ ] **누락 0건 (`check_coverage.py`, H-5)**: manifest 섹션 ID ↔ 생성 MDX 1:1 대조. `MISSING`(Appendix F)은 **스텁 존재 + 안내 문구 존재** 확인(W3-M1), Index는 미이관으로 대조 제외(§0 V-9). 불일치 시 exit 1.
- [ ] **용어 변형 스캐너 (H-6/V-6/W4-H2, 전체사이트, blocking)**: 전 MDX에서 형태소로 한국어 기술 명사 추출→`terms.json`에 없는 후보 발견 시 실패. **여기(전체 코퍼스)에서만 빈도 3회↑ 임계 적용** + 길이·불용어·네거티브 리스트. per-PR 게이트(§5.1)가 놓친 sparse 신조어를 코퍼스 누적으로 포착.
- [ ] **Glossary 동기화 (W3-H9/W4-M3/W5-M2)**: 빌드 산출 Glossary MDX를 **생성기와 코드를 공유하지 않는 독립 파서(최소 정규식)**로 재파싱해 `{en, ko, definition_ko}`가 `terms.json`과 일치하는지 검증. 추가로 T3a freeze 시 각 `definition_ko` 해시를 terms.json에 기록→파싱 결과와 해시 대조(공유 파서 버그 회피).
- [ ] **병기 규칙 (M-6)**: `first_chapter` 외 챕터에 병기형이 남아있지 않은지.
- [ ] **문체 (H-2/V-7/W5-H2/W6-M3)**: 종결어미 휴리스틱으로 합쇼체 이탈 flag. **비산문 줄 필터 선적용**: (1) fenced code block 내부 제외, (2) `#` 헤딩·`|` 표 셀·`<`/`>`로 시작하는 MDX 태그·`>` 인용 제외, (3) **`:::` 오프너부터 닫는 `:::`까지 어드모니션 블록 전체를 상태 추적해 제외**(오프너 한 줄이 아니라 본문 bullet·명사구·명령형까지 — 종결어미 없는 정상 내용의 오탐 방지), (4) 한글 없는 줄 제외. 필터 후에만 검사.
- [ ] **코드 무결성**: §5.1 PR 게이트 결과 집계 — 전 챕터 코드 diff 0.
- [ ] **완결성 비율 (M-12/V-5/W5-H1·H3)**: 전 챕터 **단락 비율 ≥ 0.85 AND 토큰 비율이 섹션 아키타입별 보정 구간**(하한 μ−2σ, 상한 μ+3σ; code_ratio로 계층 선택, T2a-core-calibrate 산출). 이탈 시 실패.
- [ ] **교차참조 무결성 (M-7/V-8/W3-M3)**: 아래 패턴 잔존 grep = 0 — 영문 `Figure\s+\d+\.\d+`·`Table\s+\d+\.\d+`·`Appendix\s+[A-G]`, 한국어 `그림\s*\d`·`표\s*\d`·`부록\s*[A-G]`·`섹션\s*\d`, **원서 Index 참조**(`\bIndex\b`; `색인`은 "색인 대신 검색" 안내 문구를 화이트리스트 제외, W5). `<CrossRef>` 앵커 대상 실재 확인.
- [ ] **링크 무결성**: 깨진 내부 링크 0.
- [ ] **빌드**: `docusaurus build` **에러 0**(무해한 경고는 화이트리스트로 관리 — "경고 0"은 비현실적), Pagefind 인덱스 생성 + 한국어 쿼리 결과 반환 확인.
- [ ] **렌더링 (H-3)**: 한글 Mermaid 스크린샷에 tofu(□) 없음, 다크/라이트·반응형.
- [ ] **다이어그램 65개** 전부 게시(Mermaid or PNG), 캡션·의미 대조(§6) 완료.

---

## 8. 리스크 & 완화

| 리스크 | 완화 |
|---|---|
| 병렬 번역 용어 불일치 | T3a freeze SSOT + §5 규약 + §7 변형 스캐너(blocking) |
| 병렬 번역 문체 drift | 합쇼체 고정 + Chapter 1 기준번역본 + §7 종결어미 검사 |
| MDX 특수문자 빌드 실패 | §5 규약6 이스케이프 + §5.1 챕터별 컴파일 게이트 |
| 콘텐츠 누락(Appendix F 등) | T1 TOC↔본문 교차검증 + `MISSING` 스텁 + §7 coverage 스크립트 |
| Mermaid 한글 tofu | T2 Noto Sans KR 폰트 + §7 스크린샷 검사 |
| Mermaid 의미 오류 | §6 side-by-side 노드/엣지 대조, PNG 폴백 |
| Docusaurus ≠ Vite | 사용자 승인. MDX 자산은 향후 Vite 이관 시 재사용 가능 |
| Docling/Marker 등 리서치 기각 도구 | 미채용. 검증된 PyMuPDF 경량 추출로 확정 |
| 병렬성 붕괴(Ch1 직렬화) | T5.0을 명시적 선행 태스크로 분리(V-1) — Ch1 승인 후 33개 병렬 |
| 게이트 스크립트 오너 부재 | T2a(게이트)·T9a(QC) 태스크 신설, T5 착수 전 완료(V-4) |
| 내용 누락이 게이트 통과 | 단락+토큰 이중 비율 게이트(V-5) |
| Index 죽은 링크 | Index 미이관, Pagefind 대체(V-9); 산문 내 Index 참조는 검색 안내로 치환(W3-M3) |
| term-drift 게이트 데드락/오탐 | hotfix PR(24h SLA)+waiver 레이블(W3-C1) + 정밀도 필터(W3-H8) |
| T5.0 인간 승인 무기한 대기 | `@maintainer`·24h SLA·SLA초과 폴백(W3-C2/H3) |
| 크리티컬 패스 연장 | T2a-core를 T3a와 병렬화(W3-H1/H2) |
| 스크립트 간 계약 드리프트 | manifest para/token 의미 + tiktoken 고정(W3-H6/H7), T2a↔T9a 경계 명시(W3-H5) |
| Glossary 이중 SSOT | terms.json에서 Glossary 자동 생성 + 동기화 검사(W3-H9) |

---

## 9. 다음 액션

승인 시 진행:
1. **T1·T2·T3·T4 이슈 생성 후 병렬 fan-out**(워크트리).
2. T1 완료 → **T2a-core-scaffold**(느슨한 게이트) 착수, **T7** 병렬 착수(V-2). T1·T3 머지 → **T3a freeze + hotfix 자동머지**.
3. T3a 완료 → **T2a-term** + **T3a-hotfix-watch**(자동 머지 봇) 개시. scaffold·term 완료 → **T9a-pre**.
4. T3a·T1·T4·T2a-core-scaffold·T2a-term 완료 → **T5.0 Ch1** 생성 + `@maintainer` 승인(24h; 초과 시 폴백+T5.0-fix).
5. T5.0 머지 → **T2a-core-calibrate**(Ch1 실측 μ/σ 계층별 보정) → 완료 후 **T5.1~N fan-out**(§5.1 게이트; 누락 용어는 `terms-hotfix` 자동검증·머지) → `check_t5_coverage.py` exit 0으로 T5 완료 → **T9a-post** 하드닝(T8 병렬).
6. T5(완료)·T7·T2·T9a-pre·T5.0-fix → **T8 통합** → (T9a-post 후) **T9 게이트** → **T10 배포**.

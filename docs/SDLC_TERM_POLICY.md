# SDLC 백서 번역 용어 순화 정책

"적극적 순화 + 영문 병기 강화" 방침. Adversarial Reviewer가 10/10 판정 시 이 정책을 기준으로 삼습니다.

## 원칙
1. **어설픈 음차·직역은 자연스러운 한국어로 순화**한다. 영어 단어를 소리 나는 대로 옮긴 것(애드하크), 문맥을 무시한 사전적 직역(악기, 빈 슬레이트)이 대상.
2. **핵심 기술 개념어는 최초 1회 `한국어(English)` 병기**를 적극 삽입한다.
3. **업계에서 이미 굳어진 관례어는 유지**한다. 억지 순화가 오히려 어색하면 관례어 우선.
4. `terms_sdlc.json`의 표준 번역어를 반드시 따른다.

## 순화 사전 (반드시 교정)
| 원문/현재 음차 | 순화 (병기) |
|---|---|
| ad-hoc / 애드하크 | 즉흥적 / 임기응변식 (ad-hoc) |
| instrument(악기) | 도구 / 악기처럼 다루는 대상 → 문맥상 "정교한 도구" |
| blank slate(빈 슬레이트) | 백지 상태 (blank slate) |
| framing(프레이밍) | 규정 / 관점 / 정의 방식 |
| frontier model(프런티어) | 최첨단 모델 (frontier model) |
| payload(페이로드) | 입력 데이터 / 전달 데이터 (payload) — 문맥상 "모델에 전달되는 정보 뭉치" |
| boilerplate(보일러플레이트) | 상용구 코드 (boilerplate) |
| spot-check(스팟 체크) | 표본 점검 / 부분 점검 |
| on-call rotation(온콜 로테이션) | 온콜 당번 체계 / 대기 근무 로테이션 |
| drift(드리프트/표류) | (에이전트가) 벗어남 / 이탈 (drift) — 첫 등장 병기 |
| force multiplier(역량 배수기) | 힘을 몇 배로 키우는 도구 / 증폭기 |
| autonomy ladder(자율성 사다리) | 자율성 등급 사다리 → "자율성 순위" |
| generalist(제너럴리스트) | 범용 에이전트 (generalist) |
| few-shot(퓨샷) | 퓨샷(few-shot) — 병기 유지 (관례어) |
| craft(장인정신) | 장인의 기술 / 진정한 기예 → 문맥상 유지 가능하나 "숙련된 기술" 권장 |

## 관례어 (유지 — 순화 금지)
하네스(harness), 오케스트레이션/오케스트레이터, 트레이드오프(trade-off), 워크플로우(workflow),
메모리, 토큰, 프롬프트, 컨텍스트, 스킬, 런타임(runtime), 스캐폴딩(scaffolding),
리팩터링(refactoring), 샌드박스(sandbox), 관측성(observability), 커맨드라인(command-line),
게이트(gate), 파이프라인(pipeline), 세션(session), 이식성(portability).

## 표현 다듬기 (직역투 → 자연스러운 한국어)
- "일급/1급 아키텍처 결정" → "가장 우선하는 아키텍처 결정" 또는 "일급(first-class) 아키텍처 결정" (병기)
- "발판" (scaffolding 의미일 때) → "발판(scaffolding)" 첫 등장 병기, 이후 "발판"
- "근거 있는 보고서" (grounded) → "출처에 근거한 보고서"
- "규율 있는 접근" → "체계적이고 절제된 접근" 또는 "규율 잡힌 접근"
- "인계 프로토콜" (handoff) → "인수인계 규약 (handoff protocol)"
- "계측" (metering) → "측정 / 계측(metering)"
- "빈 슬레이트에서 시작" → "백지 상태에서 시작"

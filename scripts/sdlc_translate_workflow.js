export const meta = {
  name: 'sdlc-translate',
  description: 'Translate the 10 remaining SDLC-paper sections to Korean 합쇼체 MDX, then adversarially verify each',
  phases: [
    { title: 'Translate' },
    { title: 'Verify' },
  ],
};

const REPO = '/Users/a420132/workspace/agentic_design_patterns';

// Shared rules embedded in every translator + verifier prompt so all agents agree.
const RULES = `
번역 규약 (모든 섹션 공통):
1. 문체: 자연스러운 한국어 **합쇼체(–습니다/–합니다)**로 통일. 원문의 의미를 하나도 빠뜨리지 말 것(모든 문단·불릿·표·각주 100% 이관).
2. 기술용어 병기: terms_sdlc.json에 있는 용어는 **이 섹션이 first_chapter인 경우에만** \`한국어(English)\` 형식으로 최초 1회 병기, 그 외에는 한국어 단독. 고유명사·제품명(Claude Code, Cursor, Codex, GitHub Copilot, Jules, Gemini, ADK, MCP, A2A, AGENTS.md, CLAUDE.md 등)은 원문 유지.
3. terms_sdlc.json의 표준 번역어를 반드시 사용(예: vibe coding→바이브 코딩, agentic engineering→에이전틱 엔지니어링, harness→하네스, conductor→지휘자, orchestrator→오케스트레이터). 사전에 없는 새 기술용어가 필요하면 자연스러운 한국어+영문 병기로 처리.
4. 코드/스니펫/명령어(uvx, agents-cli 등)와 URL은 **원문 그대로**. 코드 블록은 \`\`\`bash 등 언어 태그를 붙여 보존.
5. 그림 위치: 원문에 "Figure N: ..." 또는 스니펫 캡션이 나오는 자리에 해당 <Diagram id="..." /> placeholder를 넣을 것(캡션 텍스트는 쓰지 말 것 — 통합 스크립트가 한국어 캡션을 채움). 어떤 그림 id가 이 섹션에 속하는지는 아래 figures 목록 참조.
6. MDX 안전: 산문 속 <, >, {, } 는 백틱 인라인 코드로 감싸거나 이스케이프. 부등호가 든 화살표(예: think -> act)는 백틱으로 감쌀 것. 원문의 곧은 따옴표는 유지하되 JSX를 깨지 않도록 주의.
7. 소제목(##/###)은 원문의 하위 헤딩 구조를 그대로 반영. 최상위 제목은 # 하나.
8. 각주는 Docusaurus 각주 문법([^1] ... [^1]: 내용)으로 이관. 미주(endnotes) 섹션이 있으므로 본문 각주는 간략히 출처만 적고 "전체 출처는 미주 참조"로 연결해도 됨.
`;

const TRANSLATION_SCHEMA = {
  type: 'object',
  properties: {
    section_id: { type: 'string' },
    file_written: { type: 'string', description: 'absolute path written' },
    heading_count: { type: 'number' },
    diagram_ids_placed: { type: 'array', items: { type: 'string' } },
    notes: { type: 'string', description: 'any terminology decisions or difficulties' },
  },
  required: ['section_id', 'file_written', 'diagram_ids_placed'],
};

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    section_id: { type: 'string' },
    complete: { type: 'boolean', description: 'true if no source content is missing' },
    style_ok: { type: 'boolean', description: 'true if consistently 합쇼체 in prose' },
    terminology_ok: { type: 'boolean', description: 'true if terms match terms_sdlc.json standard forms' },
    diagrams_ok: { type: 'boolean', description: 'true if all expected <Diagram> placeholders present and correct' },
    mdx_safe: { type: 'boolean', description: 'true if no unescaped <>{} that would break MDX' },
    issues: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
          description: { type: 'string' },
        },
        required: ['severity', 'description'],
      },
    },
  },
  required: ['section_id', 'complete', 'style_ok', 'terminology_ok', 'diagrams_ok', 'mdx_safe', 'issues'],
};

// One spec per section to translate (introduction already done as style baseline).
const SECTIONS = [
  { id: 'syntax-to-intent', title: '구문에서 의도로: 에이전트와 바이브 코딩', pos: 3,
    figures: [
      { id: 'fig-p10-0', where: 'Figure 2: The Agent Loop 캡션 자리 (Mermaid — 에이전트 루프)' },
      { id: 'fig-p14-0', where: 'Figure 3: The Vibe Coding to Agentic Engineering Spectrum 캡션 자리' },
    ],
    note: 'Table 1(스펙트럼 비교표)은 마크다운 표로 완전히 번역할 것 — 3열(바이브 코딩 / 구조화된 AI 보조 코딩 / 에이전틱 엔지니어링), 6행(의도 명세·검증·코드베이스 이해·오류 처리·적절한 범위·리스크 프로파일). "Applied Tip" 콜아웃은 :::tip 로.' },
  { id: 'context-engineering', title: '컨텍스트 엔지니어링: 진짜 핵심 역량', pos: 4,
    figures: [{ id: 'fig-p17-0', where: 'Figure 4: Context Engineering — Static vs. Dynamic 캡션 자리' }],
    note: '여섯 가지 컨텍스트 유형 불릿(Instructions/Knowledge/Memory/Examples/Tools/Guardrails)을 정확히 이관. AGENTS.md/CLAUDE.md/GEMINI.md 파일명 원문 유지.' },
  { id: 'new-sdlc', title: '새로운 소프트웨어 개발 수명주기', pos: 5,
    figures: [
      { id: 'fig-p20-0', where: 'Figure 5: Traditional SDLC vs. AI-Driven SDLC 캡션 자리' },
      { id: 'fig-p25-0', where: 'Figure 6: The Factory Model 캡션 자리' },
    ],
    note: '하위 헤딩 많음: "The traditional SDLC under pressure", "How AI transforms each phase"(그 아래 Requirements and planning / Design and architecture / Implementation / Testing and quality assurance / Code review and deployment / Maintenance and evolution), "The factory model". 헤딩 레벨을 원문 위계대로. "A note on pace of change" 문단 유지. 공장 모델 불릿 5개 이관.' },
  { id: 'harness-engineering', title: '하네스 엔지니어링: 모델을 둘러싼 것', pos: 6,
    figures: [
      { id: 'fig-p26-0', where: '"A useful equation:" 다음의 Agent = Model + Harness 등식 자리' },
      { id: 'fig-p27-0', where: 'Figure 7: Harness Anatomy 캡션 자리' },
    ],
    note: `하위 헤딩: "What's in the harness"(불릿 6개: Instructions and Rule Files/Tools/Sandboxes/Orchestration logic/Guardrails or Hooks/Observability), "Harness in SDLC"(번호 항목 1~4: Configuring/Running/Feedback Loop/Observing the Harness). "Agent = Model + Harness" 등식은 fig-p26-0 placeholder로.` },
  { id: 'developer-role', title: '진화하는 개발자의 역할: 지휘자와 오케스트레이터', pos: 7,
    figures: [{ id: 'fig-p32-0', where: 'Figure 8: Conductor vs. Orchestrator 캡션 자리' }],
    note: '하위 헤딩: "The conductor: hands-on, real-time direction", "The orchestrator: async, multi-agent delegation"(그 아래 Specification/Decomposition/Evaluation/System design 불릿), "The 80% problem". 제품명(Copilot/Cursor/Windsurf/Jules/Claude Code) 원문 유지.' },
  { id: 'coding-agents', title: '실무에서의 코딩 에이전트', pos: 8,
    figures: [],
    note: `하위 헤딩: "Where coding agents fit in the developer's day"(In the editor/In the terminal/In the background 3분류), "Vibe Coding Production-ready Agents". **Snippet 1 코드 블록**(# One-time setup / uvx google-agents-cli setup / > Build a support agent... 등)은 반드시 bash 코드 블록으로 원문 그대로 보존하고, "Snippet 1: Agents CLI Setup and Build." 캡션은 코드 블록 위에 굵은 글씨나 콜아웃으로. agents-cli 명령들(create/playground/eval/deploy)은 인라인 코드로.` },
  { id: 'economics', title: 'AI 개발의 경제학', pos: 9,
    figures: [{ id: 'fig-p40-0', where: 'Figure 9: The Economics of AI Development 캡션 자리' }],
    note: '하위 헤딩: "The Hidden Debt of Vibe Coding (Low CapEx, High OpEx)", "The Investment of Agentic Engineering (High CapEx, Low OpEx)", "Context Engineering as a Financial Lever", "Scaling Efficiency via Dynamic Context and Skills", "Intelligent Model Routing". CapEx/OpEx/TCO 병기.' },
  { id: 'where-to-start', title: '어디서부터 시작할 것인가', pos: 10,
    figures: [],
    note: '하위 헤딩 3개: "For individual developers"(번호 1~6), "For engineering leaders"(번호 1~5), "For organizations"(번호 1~5). 각 번호 항목의 제목(굵게)과 설명을 모두 이관. 번호 목록 유지.' },
  { id: 'conclusion', title: '결론: 새로운 인터페이스로서의 의도', pos: 11,
    figures: [],
    note: `"Three principles stand out as durable:" 아래 번호 3항목(Structure scales, vibes don't / AI amplifies your engineering culture / The human role is evolving, not diminishing) 이관. 마지막 문장 "Generation is solved. Verification, judgment, and direction are the new craft." 인상적으로 번역.` },
  { id: 'endnotes', title: '미주', pos: 12,
    figures: [],
    note: '32개 미주(citation) 목록. 번호와 URL은 원문 그대로 유지. 출판사/저자명은 원문 유지, 제목은 원문(영문) 유지하되 필요 시 괄호로 간단한 한국어 설명 가능. 번호 목록(1. 2. ...)으로. KeyPoints 콜아웃 없이 간단한 안내문 + 목록만.' },
];

phase('Translate');

const results = await pipeline(
  SECTIONS,
  // Stage 1: translate + write file
  (sec) => agent(
    `당신은 Google 백서 "The New SDLC With Vibe Coding"의 한국어 번역 전문가입니다.

담당 섹션: ${sec.id} (제목: "${sec.title}", sidebar_position: ${sec.pos})

먼저 다음 파일들을 Read로 읽으세요:
1. 원문: ${REPO}/assets/sdlc/sections/${sec.id}.txt
2. 용어 SSOT: ${REPO}/terms_sdlc.json
3. 문체 기준 번역본(이 스타일을 그대로 따를 것): ${REPO}/site/sdlc-docs/introduction.mdx

${RULES}

이 섹션의 그림 목록(figures):
${sec.figures.length ? sec.figures.map(f => `  - <Diagram id="${f.id}" /> → ${f.where}`).join('\n') : '  (없음)'}

섹션별 추가 지침:
${sec.note}

작성 규칙:
- 파일 맨 위 frontmatter:
  ---
  id: ${sec.id}
  title: ${sec.title}
  sidebar_label: (짧은 라벨)
  sidebar_position: ${sec.pos}
  description: "(한 줄 요약)"
  ---
- frontmatter 다음 줄에 컴포넌트 import: 그림이 있으면 \`import { KeyPoints, Diagram } from '@site/src/components';\`, 없으면 \`import { KeyPoints } from '@site/src/components';\` (endnotes 섹션은 KeyPoints도 생략 가능).
- import 다음에 <KeyPoints items={[...]} /> 콜아웃(핵심 3~5줄, 큰따옴표 문자열 배열). endnotes 섹션은 생략.
- 그 다음 "# ${sec.title}" 제목과 본문.
- <Diagram> placeholder는 위 figures 목록의 id를 정확히 사용, 원문 캡션 위치에 배치.

완성된 MDX를 Write 도구로 다음 경로에 저장하세요: ${REPO}/site/sdlc-docs/${sec.id}.mdx

저장 후 결과를 구조화해 반환하세요.`,
    { label: `tr:${sec.id}`, phase: 'Translate', schema: TRANSLATION_SCHEMA }
  ),
  // Stage 2: adversarial verify
  (tr, sec) => agent(
    `당신은 번역 품질 검증관입니다. 섹션 "${sec.id}"의 한국어 번역을 원문과 대조해 적대적으로 검증하세요.

다음을 Read로 읽으세요:
1. 원문: ${REPO}/assets/sdlc/sections/${sec.id}.txt
2. 번역본: ${REPO}/site/sdlc-docs/${sec.id}.mdx
3. 용어 SSOT: ${REPO}/terms_sdlc.json

검증 항목:
- complete: 원문의 모든 문단·불릿·표 행·번호 항목·각주가 빠짐없이 번역되었는가? (누락 = high 이슈)
- style_ok: 산문이 일관되게 합쇼체(–습니다/–합니다)인가? (반말·해요체 혼입 = 이슈)
- terminology_ok: 핵심 용어가 terms_sdlc.json 표준형과 일치하는가? 병기 규칙(first_chapter에서만 최초 1회)을 지켰는가?
- diagrams_ok: 이 섹션에 배정된 <Diagram> placeholder가 올바른 id로 모두 있는가? 기대 id: ${sec.figures.map(f=>f.id).join(', ') || '(없음)'}
- mdx_safe: 이스케이프되지 않은 <, >, {, } 로 MDX 빌드가 깨질 위험이 없는가? (특히 화살표 -> 나 부등호)
- 코드/스니펫/URL이 원문 그대로 보존되었는가? (변경 = high 이슈)

발견한 문제를 issues 배열에 severity와 함께 기록하세요. 문제가 없으면 빈 배열. 각 불리언 필드를 정직하게 판정하세요.`,
    { label: `vrf:${sec.id}`, phase: 'Verify', schema: VERDICT_SCHEMA }
  )
);

return results.filter(Boolean);

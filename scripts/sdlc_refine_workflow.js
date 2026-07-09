export const meta = {
  name: 'sdlc-refine',
  description: 'Refine SDLC translations to eliminate awkward transliterations; adversarial reviewer scores 0-10 until 10/10 (max 30 loops per section)',
  phases: [
    { title: 'Refine' },
  ],
};

const REPO = '/Users/a420132/workspace/agentic_design_patterns';
const MAX_LOOPS = 30;

// All translated section files (intro.mdx is a landing page, also refine it).
const FILES = [
  'intro', 'introduction', 'syntax-to-intent', 'context-engineering', 'new-sdlc',
  'harness-engineering', 'developer-role', 'coding-agents', 'economics',
  'where-to-start', 'conclusion', 'endnotes',
];

const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    score: { type: 'number', description: '0-10 총점. 10은 어설픈 음차/직역이 전무하고 자연스러운 한국어인 상태.' },
    verdict: { type: 'string', enum: ['PASS', 'FAIL'], description: 'score===10 이면 PASS, 아니면 FAIL' },
    issues: {
      type: 'array',
      description: '남아 있는 어설픈 음차·직역·부자연스러운 표현. 없으면 빈 배열.',
      items: {
        type: 'object',
        properties: {
          severity: { type: 'string', enum: ['high', 'medium', 'low'] },
          quote: { type: 'string', description: '문제가 된 원문 구절(그대로 인용)' },
          problem: { type: 'string', description: '왜 어설픈지' },
          suggestion: { type: 'string', description: '권장 순화안' },
        },
        required: ['severity', 'quote', 'problem', 'suggestion'],
      },
    },
  },
  required: ['score', 'verdict', 'issues'],
};

const REVISE_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    changed: { type: 'boolean', description: '실제로 파일을 수정했으면 true' },
    change_summary: { type: 'string', description: '적용한 교정 요약' },
  },
  required: ['file', 'changed'],
};

const POLICY_REF = `
반드시 먼저 Read: ${REPO}/docs/SDLC_TERM_POLICY.md (순화 정책) 와 ${REPO}/terms_sdlc.json (표준 용어).

정책 핵심:
- 어설픈 음차/직역은 자연스러운 한국어로 순화한다. 예: 애드하크→즉흥적/임기응변식(ad-hoc), 악기→(정교한) 도구, 빈 슬레이트→백지 상태(blank slate), 프레이밍→규정/관점, 프런티어 모델→최첨단 모델(frontier model), 페이로드→입력 데이터/전달 정보(payload), 보일러플레이트→상용구 코드(boilerplate), 스팟 체크→표본 점검, 온콜 로테이션→대기 근무 당번, 역량 배수기→힘을 몇 배로 키우는 도구, 자율성 사다리→자율성 순위, 일급/1급→가장 우선하는(또는 일급(first-class)).
- 핵심 개념어는 최초 1회 한국어(English) 병기를 적극 삽입.
- 관례어는 유지: 하네스, 오케스트레이션, 트레이드오프, 워크플로우, 메모리, 토큰, 프롬프트, 컨텍스트, 스킬, 런타임, 스캐폴딩, 리팩터링, 샌드박스, 관측성, 커맨드라인, 게이트, 파이프라인, 세션, 이식성, 퓨샷.
- 합쇼체 유지. 코드/스니펫/URL/제품명/frontmatter의 id·sidebar_position 불변. MDX 안전(<,>,{,} 이스케이프 또는 백틱). figure/figcaption·Diagram 유지.
- 원문 의미를 왜곡하지 말 것. 순화는 표현만 바꾸고 내용은 보존.
`;

phase('Refine');

const results = await pipeline(
  FILES,
  async (fileId) => {
    const path = `${REPO}/site/sdlc-docs/${fileId}.mdx`;
    let lastScore = -1;
    let lastReview = null;
    const history = [];

    for (let loop = 1; loop <= MAX_LOOPS; loop++) {
      // 1) Adversarial review
      const review = await agent(
        `당신은 매우 까다로운 한국어 기술번역 적대적 검수관입니다. 다음 MDX 문서를 0~10점으로 채점하세요.

${POLICY_REF}

검수 대상 파일을 Read: ${path}

채점 기준(10점 = 완벽):
- 어설픈 음차(영어 소리만 옮긴 것)나 문맥 무시 직역이 하나라도 있으면 9점 이하.
- 정책 순화 사전의 대상 표현이 교정되지 않은 채 남아 있으면 감점.
- 부자연스러운 번역투("~을 필요로 합니다"의 남발, 어색한 피동 등)가 두드러지면 감점.
- 병기 규칙 위반, 합쇼체 이탈, 의미 왜곡은 high 이슈.
- 단, 정책이 "유지"로 지정한 관례어를 순화하라고 요구하지 말 것(그건 이슈 아님).

가혹하게 보되 공정하게. 진짜 문제만 issues에 담고, 정말 흠잡을 데 없으면 score=10, verdict=PASS, issues=[].
이번이 ${loop}번째 검수입니다.${lastReview ? ' 직전 검수에서 지적된 사항이 제대로 반영됐는지 특히 확인하세요.' : ''}`,
        { label: `review:${fileId}#${loop}`, phase: 'Refine', schema: REVIEW_SCHEMA }
      );

      history.push({ loop, score: review?.score ?? null, issues: (review?.issues || []).length });
      lastScore = review?.score ?? -1;
      lastReview = review;

      if (review && review.verdict === 'PASS' && review.score === 10) {
        return { file: fileId, final_score: 10, loops: loop, history };
      }

      // 2) Revise per the review's issues
      const issuesText = (review?.issues || [])
        .map((it, i) => `${i + 1}. [${it.severity}] 구절: "${it.quote}"\n   문제: ${it.problem}\n   권장: ${it.suggestion}`)
        .join('\n');

      await agent(
        `당신은 한국어 기술번역 교정 전문가입니다. 아래 문서를 순화 정책에 맞게 교정하세요.

${POLICY_REF}

교정 대상 파일을 Read: ${path}

적대적 검수관이 이번 라운드(${loop}회차, 현재 점수 ${lastScore}/10)에 지적한 문제들:
${issuesText || '(구체 이슈 미기재 — 정책 순화 사전 전체를 문서에 적용해 어설픈 음차/직역을 모두 제거하세요.)'}

지적 사항을 모두 반영해 Edit 또는 Write로 파일을 직접 수정하세요. 지적되지 않았더라도 정책상 명백히 어설픈 표현이 보이면 함께 고치세요.
frontmatter의 id/sidebar_position, 코드 블록, URL, 제품명, <figure>/<Diagram>은 절대 건드리지 마세요.
수정을 마치면 결과를 반환하세요.`,
        { label: `revise:${fileId}#${loop}`, phase: 'Refine', schema: REVISE_SCHEMA }
      );
    }

    return { file: fileId, final_score: lastScore, loops: MAX_LOOPS, history, note: 'reached MAX_LOOPS without 10/10' };
  }
);

return results.filter(Boolean);

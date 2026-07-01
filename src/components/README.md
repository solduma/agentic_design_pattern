# MDX 컴포넌트 라이브러리

Agentic Design Patterns 한국어 문서 사이트(Docusaurus 3 + Prism)에서 사용하는 커스텀 React/MDX 컴포넌트입니다.

## 설치 및 임포트

각 컴포넌트는 독립적으로 임포트하거나 배럴 익스포트(`index.ts`)를 통해 가져올 수 있습니다.

```tsx
// 개별 임포트
import KeyPoints from '@site/src/components/KeyPoints';
import OriginalText from '@site/src/components/OriginalText';
import Diagram from '@site/src/components/Diagram';
import CrossRef from '@site/src/components/CrossRef';
import ChapterNav from '@site/src/components/ChapterNav';

// 또는 배럴 임포트
import { KeyPoints, OriginalText, Diagram, CrossRef, ChapterNav } from '@site/src/components';
```

MDX 파일에서 전역 컴포넌트로 등록하려면 `src/theme/MDXComponents.tsx`에 추가합니다:

```tsx
// src/theme/MDXComponents.tsx
import MDXComponents from '@theme-original/MDXComponents';
import KeyPoints from '@site/src/components/KeyPoints';
import OriginalText from '@site/src/components/OriginalText';
import Diagram from '@site/src/components/Diagram';
import CrossRef from '@site/src/components/CrossRef';
import ChapterNav from '@site/src/components/ChapterNav';

export default {
  ...MDXComponents,
  KeyPoints,
  OriginalText,
  Diagram,
  CrossRef,
  ChapterNav,
};
```

---

## 컴포넌트 목록

### 1. KeyPoints — 이 장의 핵심 콜아웃

챕터 상단에 핵심 내용을 강조하는 콜아웃 박스입니다.

**Props**

| prop | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `items` | `string[]` | — | 핵심 포인트 문자열 배열 |
| `title` | `string` | `"이 장의 핵심"` | 헤딩 텍스트 |
| `children` | `ReactNode` | — | `items` 미제공 시 사용 |

**사용 예시**

```mdx
import KeyPoints from '@site/src/components/KeyPoints';

<KeyPoints
  items={[
    "프롬프트 체이닝은 복잡한 작업을 단계별로 분해합니다.",
    "각 LLM 호출은 이전 단계의 출력을 입력으로 받습니다.",
    "게이트 조건을 추가하면 불필요한 처리를 건너뛸 수 있습니다.",
  ]}
/>
```

```mdx
<!-- children 방식 -->
<KeyPoints title="핵심 요약">
  - 에이전트는 도구를 통해 외부 시스템과 상호작용합니다.
  - 멀티 에이전트 시스템은 병렬 처리가 가능합니다.
</KeyPoints>
```

---

### 2. OriginalText — 원문 펼치기

한국어 번역 아래에 원문(영문)을 접을 수 있게 보여주는 `<details>` 요소입니다.

**Props**

| prop | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `title` | `string` | `"원문 펼치기"` | 접힌 상태에서 보이는 토글 텍스트 |
| `children` | `ReactNode` | (필수) | 원문 영문 내용 |

**사용 예시**

```mdx
import OriginalText from '@site/src/components/OriginalText';

<OriginalText>
  Prompt chaining decomposes a task into a sequence of steps, where each
  LLM call processes the output of the previous one. You can also add
  programmatic checks (see "gate" in the diagram below) on outputs.
</OriginalText>
```

```mdx
<OriginalText title="Original (English)">
  The agent uses tools to interact with external systems, enabling
  retrieval, code execution, and API calls.
</OriginalText>
```

---

### 3. Diagram — 다이어그램 래퍼

manifest 이미지 ID 기반 figure 요소입니다. `src` 제공 시 이미지를 렌더하고, 없으면 T8 통합을 위한 플레이스홀더를 표시합니다.

**ID 포맷:** `img-p{페이지번호}-{인덱스}` (예: `img-p51-0`)

**Props**

| prop | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `id` | `string` | (필수) | manifest 전역 고유 이미지 ID |
| `src` | `string` | — | 이미지 URL (PNG/SVG). 없으면 플레이스홀더 |
| `caption` | `string` | — | 한국어 캡션 (figcaption) |
| `alt` | `string` | — | 이미지 접근성 alt 텍스트 |
| `children` | `ReactNode` | — | Mermaid 컴포넌트 등 커스텀 콘텐츠 슬롯 |

**사용 예시**

```mdx
import Diagram from '@site/src/components/Diagram';

{/* PNG 이미지 */}
<Diagram
  id="img-p51-0"
  src="/img/diagrams/img-p51-0.png"
  caption="그림 3.1 — 프롬프트 체이닝 흐름도"
  alt="프롬프트 체이닝: LLM 단계별 입출력 다이어그램"
/>

{/* T8 통합 전 플레이스홀더 (src 없음) */}
<Diagram id="img-p51-0" caption="그림 3.1 — 프롬프트 체이닝 흐름도" />
```

```mdx
{/* Mermaid 슬롯 (children으로 전달) */}
import Mermaid from '@theme/Mermaid';

<Diagram id="img-p51-0" caption="그림 3.1 — 시퀀스 다이어그램">
  <Mermaid
    value={`sequenceDiagram
    사용자->>LLM: 프롬프트
    LLM->>도구: 도구 호출
    도구-->>LLM: 결과
    LLM-->>사용자: 최종 응답`}
  />
</Diagram>
```

---

### 4. CrossRef — 인라인 교차 참조

manifest 교차 참조 레지스트리 ID 기반 인라인 링크입니다. `href`가 있으면 앵커 링크, 없으면 T8 후처리를 위해 `data-xref-id` 속성을 가진 span을 렌더합니다.

**Props**

| prop | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `id` | `string` | (필수) | 교차 참조 레지스트리 ID |
| `label` | `string` | (필수) | 표시할 텍스트 |
| `href` | `string` | — | 해석된 앵커 또는 경로. 없으면 미연결 span |

**사용 예시**

```mdx
import CrossRef from '@site/src/components/CrossRef';

{/* 해결된 교차 참조 */}
자세한 내용은 <CrossRef id="sec-prompt-chaining" label="프롬프트 체이닝" href="/docs/part1/chapter1#prompt-chaining" />을 참조하십시오.

{/* 아직 미연결 — T8이 href 삽입 */}
아래 <CrossRef id="img-p51-0" label="그림 3.1" />에서 흐름을 확인하십시오.

{/* 부록 참조 */}
<CrossRef id="appendix-a" label="부록 A — 용어집" href="/docs/appendix/appendix-a" />
```

---

### 5. ChapterNav — 챕터 이동 카드

챕터 하단의 이전/다음 챕터 네비게이션 카드입니다. `prev`, `next` 중 하나만 제공할 수 있습니다.

**Props**

| prop | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `prev` | `{ title: string; href: string }` | — | 이전 챕터 정보 |
| `next` | `{ title: string; href: string }` | — | 다음 챕터 정보 |

**사용 예시**

```mdx
import ChapterNav from '@site/src/components/ChapterNav';

{/* 전체 네비 */}
<ChapterNav
  prev={{ title: "1장 — 프롬프트 체이닝", href: "/docs/part1/chapter1" }}
  next={{ title: "3장 — 라우팅", href: "/docs/part1/chapter3" }}
/>

{/* 첫 챕터 — prev 없음 */}
<ChapterNav
  next={{ title: "2장 — 병렬화", href: "/docs/part1/chapter2" }}
/>

{/* 마지막 챕터 — next 없음 */}
<ChapterNav
  prev={{ title: "20장 — 탐색적 에이전트", href: "/docs/part4/chapter20" }}
/>
```

---

## 다크 모드

모든 컴포넌트는 Docusaurus의 `[data-theme='dark']` 셀렉터를 통해 다크 모드를 지원합니다. 추가 설정 없이 사이트 테마 토글과 자동으로 연동됩니다.

## 타입체크

컴포넌트는 표준 React + TypeScript로 작성되어 있습니다. 독립 타입체크:

```bash
npx tsc --noEmit --jsx react-jsx --strict \
  src/components/KeyPoints.tsx \
  src/components/OriginalText.tsx \
  src/components/Diagram.tsx \
  src/components/CrossRef.tsx \
  src/components/ChapterNav.tsx
```

또는 Docusaurus 사이트 루트에서:

```bash
npx tsc --noEmit
```

## Prism 하이라이팅

본 컴포넌트 라이브러리는 **Prism** 기반으로 작성되었습니다(Shiki 미사용). 이는 `PLAN.md §0` 결정 및 T2 스캐폴딩 설정과 일치합니다.

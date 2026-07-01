# Contributing to Agentic Design Patterns Docs

## Binding Decisions

### Code Syntax Highlighting: Prism (NOT Shiki)

**Decision:** This project uses **Prism** for code syntax highlighting, which is the Docusaurus default via `prism-react-renderer`.

**Rationale (PLAN.md §0, M-11):**
- Prism ships with Docusaurus and requires zero additional configuration.
- Shiki requires extra setup steps (theme config, WASM loading) that would add friction for chapter translation agents (T5) without meaningful user-visible benefit.
- This decision was finalized in the adversarial review (M-11) to eliminate ambiguity for parallel translation subagents.

**Implementation:** `docusaurus.config.js` `themeConfig.prism` — `prismThemes.github` (light) and `prismThemes.dracula` (dark).

**Do NOT switch to Shiki** without updating this file, `PLAN.md §0`, and all chapter MDX files that depend on Prism language identifiers.

---

### Search: Pagefind (NOT Algolia)

**Decision:** This project uses **Pagefind** for full-text search.

**Rationale (PLAN.md §0, M-10):**
- Pagefind has built-in CJK n-gram tokenization — Korean search works out of the box.
- Algolia requires manual Korean morpheme analyzer configuration.
- Pagefind is serverless and runs entirely from the static build output.

**Implementation:** `pagefind` devDependency; `npm run build` = `docusaurus build && pagefind --site build`. Search UI at `/search`.

---

### Korean Mermaid Labels: Noto Sans KR

**Decision:** Mermaid diagrams use `fontFamily: "'Noto Sans KR', sans-serif"` to prevent Korean text from rendering as tofu (□).

**Implementation:**
- `docusaurus.config.js` `themeConfig.mermaid.options.fontFamily`
- `src/css/custom.css` `@import` from Google Fonts

---

### i18n: Single Korean locale

**Decision:** `defaultLocale: 'ko'`, `locales: ['ko']`.

This sets `<html lang="ko">` for correct CJK rendering. It is NOT a multi-locale translation pipeline — the entire site is written in Korean.

# QC Report — T9: 일관성 검증 (Issue #88)

**Date:** 2026-07-01  
**Branch:** `feature/88-qc`  
**Scope:** Full site under `site/docs/` (36 MDX files, 33 translatable sections)

---

## Gate Summary Table

| # | Gate | Status | Detail |
|---|------|--------|--------|
| 1 | Coverage (check_coverage.py) | **PASS** | 35 sections matched; `intro.mdx` whitelisted as benign landing page; `appendix-f` stub present with notice text |
| 2 | Code Integrity (check_code_integrity.py) | **PASS** | 23 sections checked (those with assets/code_blocks/*.json); all pass after fixing mermaid-block exclusion |
| 3 | Completeness Ratio (check_ratio.py) | **PARTIAL FAIL** | 32/33 pass; **ch08 FAIL** (token_ratio=0.657, band=[0.977, 3.294]) — real content gap |
| 4 | Term Variant Scanner | **PASS (minor)** | No systematic drift; 3 single-occurrence variants (`프롬프트 연쇄`×1, `기억 관리`×1, `파인 튜닝`×1); `라우터` 22× is legitimate |
| 5 | Bilingual Gloss Rule | **FAIL** | 35 violations — `한국어(English)` bilingual form reappears in later chapters after `first_chapter` |
| 6 | Style (style_checker.py) | **PASS** | 0 violations after fixing Korean syllabic regex (`됩니다`, `십시오` etc.) |
| 7 | Cross-Reference (xref_checker.py) | **FAIL** | 43 violations: 42× local `그림 N` figure refs; 1× `Appendix A` raw HTML link in frameworks-intro.mdx |
| 8 | Glossary Sync | **PASS** | 404/405 terms found in glossary; 1 miss (`Zero-Shot, One-Shot, & Few-Shot Prompting` → HTML-encoded `&amp;`) |
| 9 | Build + Links | **PASS** | `docusaurus build` 0 errors, Pagefind index built (40 pages, Korean), 0 broken internal links |
| 10 | Diagrams (65 IDs) | **FAIL** | Only 21/65 diagram IDs referenced in MDX; 47 unreferenced; 3 referenced IDs not in index |

---

## Script Fixes Applied (T9a-post)

The following gate scripts required corrections before producing meaningful results:

| Script | Fix | Reason |
|--------|-----|--------|
| `check_coverage.py` | Fixed `os.listdir()` → `glob.glob(..., recursive=True)` for `mdx_dir` argument; added `BENIGN_EXTRAS = {"intro", "chapter1-style-ref"}` whitelist | Script scanned flat dir, missing MDX files in subdirectories |
| `check_code_integrity.py` | Excluded `mermaid`/`mmd` fenced blocks from integrity comparison | Korean Mermaid diagrams in MDX were flagged as "EXTRA" code lines (they are translated diagram additions, not original code) |
| `check_ratio.py` | Fixed `get_thresholds()` to handle dict-typed `strata` (was iterating dict as list); added `token_ratio_max` enforcement; switched to manifest `token_count` as baseline | Stratum parsing crashed with `AttributeError`; original `.txt` files include code blocks that inflate baseline token count |
| `style_checker.py` | Fixed `HAPSYO_END_RE` from `[ㅂ습합입]니다` → `[가-힣]니다\|십시오\|십니까`; changed checker to only flag known informal endings (야/아/네요/에요/etc.) | Original regex matched single jamo chars, not syllabic blocks — `됩니다`, `됩니다`, `십시오` all failed to match |
| `xref_checker.py` | Added `SKIP_LINE_PATTERNS` to skip `#` headings, frontmatter `title:`/`sidebar_label:`, `<figcaption>`, appendix-f stub notice, nav list items; expanded `WHITELIST_STRINGS` | Heading and frontmatter lines were flagged as xref violations; glossary metadata lines (`첫 등장:`) incorrectly caught |
| `calibrate_ratio.py` + `ratio_thresholds.json` | Recalibrated from all 33 translated sections using manifest `token_count` as prose baseline; updated thresholds: prose μ=1.904, σ=0.463, lower=0.977, upper=3.294 | Prior calibration (Ch1-only) gave inconsistent baseline; now using full-corpus calibration per T9a-post instruction |

---

## Findings by Severity

### HIGH

| ID | Section | Gate | Finding |
|----|---------|------|---------|
| H-1 | ch08 | Completeness Ratio | **token_ratio=0.657** (lower bound 0.977) — translated MDX has ~34% fewer prose tokens than original (4,954 vs 9,124 reference tokens). Probable content truncation. Requires content review and re-translation of missing sections. |
| H-2 | multiple (47/65) | Diagrams | **47 of 65 diagram IDs from `assets/diagrams/index.json` are not referenced** in any MDX file. Only 21 are referenced via `<img src="/img/diagrams/img-pXX-Y.png">`. The `<Diagram id>` component was never used; many diagram assets were never embedded. |

### MEDIUM

| ID | Location | Gate | Finding |
|----|----------|------|---------|
| M-1 | 35 occurrences across chapters | Bilingual Gloss | Bilingual form `한국어(English)` reappears in chapters after `first_chapter`. Top offenders: `계획 수립(Planning)` (3×), `라우팅(Routing)` (4×), `병렬화(Parallelization)` (2×), `반성적 검토(Reflection)` (1×). |
| M-2 | 42 occurrences across ch17, ch19, ch21, appendix-a/b/d | XRef | Local `그림 N` figure references in prose text — should use `<Diagram>` component with manifest IDs per §5 규약5. These are within-section references, not cross-section, but violate the spec pattern rule. |
| M-3 | `frameworks-intro.mdx:66` | XRef | Raw `<a href="#appendix-a">Appendix A: Advanced Prompting Techniques</a>` — should be `<CrossRef id="appendix-a"/>` per spec. |
| M-4 | 3 referenced IDs | Diagrams | `img-p266-0`, `img-p271-0`, `img-p282-0` referenced in MDX but absent from `assets/diagrams/index.json`. |

### LOW / INFO

| ID | Finding |
|----|---------|
| L-1 | `glossary` has `disposition: translate` in manifest but was auto-generated from `terms.json`. Manifest should be updated to `disposition: auto-generate` to match actual process. |
| L-2 | Term variant: 1× `프롬프트 연쇄`, 1× `기억 관리`, 1× `파인 튜닝` — single-occurrence informal variants; not systematic drift. |
| L-3 | `Zero-Shot, One-Shot, & Few-Shot Prompting` not detected in glossary term search because `&` is HTML-encoded as `&amp;` in glossary MDX. Functionally correct but breaks exact-match check. |
| L-4 | Pagefind note: "doesn't support stemming for ko" — expected, not a failure. |

---

## Detailed Gate Results

### Gate 1: Coverage

```
[check_coverage] PASS: 35 sections, all have MDX files.
```
- Whitelisted: `intro.mdx` (site landing page), `chapter1-style-ref.mdx` (style reference artifact)  
- `appendix-f`: MISSING status with stub + notice text present ✓  
- `index`: excluded (disposition = omit-with-notice) ✓  
- `glossary`: auto-generated, present ✓

### Gate 2: Code Integrity

All 23 sections with code_blocks assets pass.

### Gate 3: Completeness Ratio

Calibration: μ=1.904, σ=0.463 (n=33, all sections excl. glossary), lower=0.977, upper=3.294.

| Fail | token_ratio | Band |
|------|-------------|------|
| ch08 | 0.657 | [0.977, 3.294] |

All other 32 sections within band.

### Gate 4: Term Variant Scanner

Full corpus scan (freq ≥ 3). No systematic Korean technical noun drift detected. Minor single-occurrence variants noted (INFO level).

### Gate 5: Bilingual Gloss

35 violations: `한국어(English)` form appearing in chapters after the term's `first_chapter`. The most frequent are `계획 수립(Planning)` and `라우팅(Routing)`. These should use Korean-only form in later chapters.

### Gate 6: Style

```
[style_checker] PASS: checked 36 file(s), 0 violations.
```
After fixing Korean syllabic regex and switching to informal-ending detection.

### Gate 7: Cross-Reference

43 violations:
- 42× `그림 N` references in appendices/chapters (local figure numbers — spec requires `<Diagram>` components)
- 1× bare `Appendix A` in HTML anchor in `frameworks-intro.mdx`

### Gate 8: Glossary Sync

404/405 terms present in glossary MDX. One HTML-encoding edge case (`&amp;`).

### Gate 9: Build + Links

```
[SUCCESS] Generated static files in "build".
Pagefind: Indexed 1 language (ko), 40 pages, 19,767 words.
```
0 errors, 0 broken internal links.

### Gate 10: Diagrams

- Index total: 65
- Referenced in MDX: 21
- Unreferenced (in index, not in MDX): 47
- Extra (in MDX, not in index): 3 (`img-p266-0`, `img-p271-0`, `img-p282-0`)

---

## Overall Verdict

**NO-GO for deployment.**

Blocking issues:
1. **H-1 (ch08)**: Content completeness failure — ~34% of prose content missing vs original.
2. **H-2 (Diagrams)**: 72% of documented diagrams (47/65) not embedded in the site.

Non-blocking but should be addressed before production:
- M-1: 35 bilingual gloss violations (MEDIUM)
- M-2: 42 local `그림 N` references (MEDIUM, spec violation)
- M-3: 1 raw Appendix link (MEDIUM)

---

*Generated by agent-qc (T9: QC / 일관성 검증) on 2026-07-01*

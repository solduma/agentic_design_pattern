# Hotfix Protocol for `terms.json` — `terms-hotfix` PRs

This document defines the review and merge policy for changes to
`terms.json` after the `terms-freeze-v1` tag.

---

## Overview

After `terms-freeze-v1`, all changes to `terms.json` must go through a
`terms-hotfix` PR. Two tracks exist, with different review requirements:

| Change type | Review required | Auto-merge eligible |
|---|---|---|
| Alias / schema-only change | None (CI-gated) | Yes — if CI passes |
| New `ko` translation | @maintainer review | No |
| New term entry (new `en`) | @maintainer review | No |
| Definition update (`definition_ko` / `definition_en`) | @maintainer review | No |

---

## Track A — Alias / Schema-only Changes (Auto-merge)

### What qualifies
- Adding or editing `aliases[]` entries for existing terms
- Fixing `first_chapter` metadata
- Correcting `definition_ko_sha1` when the underlying definition hasn't changed
- Fixing formatting (whitespace, punctuation) in `definition_ko` or `definition_en`
  when the content meaning is unchanged

### CI gates (all must pass for auto-merge)

1. **Schema validation** (`scripts/gen_glossary.py --check`)
   - Valid JSON
   - All required fields present (`en`, `ko`, `first_chapter`, `aliases`,
     `definition_ko`, `definition_en`)
   - No duplicate `en` keys

2. **Precision filter** — `scripts/validate_terms.py --precision`
   - No term with `ko == ""` that previously had a translation
   - No `definition_ko_sha1` mismatch for terms whose `definition_ko` was
     previously non-empty

3. **Negative list check** — `scripts/validate_terms.py --negative`
   - No term in `assets/negative_terms.txt` appears as a new `en` or `ko` entry
     (negative-list terms must never become glossary entries)

4. **Diff scope check** (CI enforced)
   - PR diff touches **only** `terms.json`; if any other file changes, CI
     rejects auto-merge and requires @maintainer approval

### PR labelling
Label the PR with `terms-hotfix-alias`. CI reads this label to activate the
auto-merge path.

---

## Track B — New `ko` Translation or New Term (Maintainer Review)

### What qualifies
- Adding a new `ko` value to a term that currently has `ko == ""`
- Adding a brand-new term entry (new `en`)
- Changing `definition_ko` in a way that alters meaning

### Review process
1. Open a PR with label `terms-hotfix-translation`.
2. Request review from `@maintainer`.
3. Maintainer verifies:
   - Translation accuracy and consistency with existing terms
   - `definition_ko` matches the `definition_ko_sha1` (run
     `scripts/gen_glossary.py --check` locally)
   - The new term is not on the negative list (`assets/negative_terms.txt`)
4. Maintainer approves and merges.

### Post-merge waiver re-check

After a Track B hotfix merges, the **term-drift scanner** re-runs automatically
against all waiver-labelled merged MDX files:

1. CI detects the merge of a `terms-hotfix-translation` PR.
2. For each MDX file that carries a `# term-drift-waiver:` annotation
   (meaning it was previously exempted from drift warnings for that term), the
   scanner re-evaluates the file against the updated `terms.json`.
3. If drift is detected (the MDX uses an old or variant translation), the
   scanner auto-opens a fix PR and assigns it to the **chapter agent** that
   owns that MDX file.
4. The chapter agent resolves the drift in a normal implementation PR.

---

## Running Validation Locally

```bash
# Check schema + SHA1 + duplicate detection
python3 scripts/gen_glossary.py --check

# Run full precision + negative-list checks
python3 scripts/validate_terms.py

# Generate glossary preview
python3 scripts/gen_glossary.py --output /tmp/glossary-preview.mdx
```

---

## Freeze Tag

The current freeze baseline is tagged **`terms-freeze-v1`**.

To inspect what changed since the freeze:

```bash
git diff terms-freeze-v1 -- terms.json
```

To create a new freeze after a large batch of approved hotfixes:

```bash
git tag -a terms-freeze-v2 -m "Second term freeze after Q3 hotfixes"
git push origin terms-freeze-v2
```

---

## Glossary Generation

The Glossary MDX page at `docs/glossary.mdx` is regenerated from `terms.json`
as part of the Docusaurus pre-build step. Run it manually with:

```bash
python3 scripts/gen_glossary.py
```

The generated file is committed to the repo; do not edit `docs/glossary.mdx`
directly — changes will be overwritten on the next build.

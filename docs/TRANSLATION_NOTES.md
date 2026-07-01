# Translation Notes for Translators

## Code Blocks — Paste Verbatim

For every section that contains code, the original verbatim code blocks have
been extracted to:

```
assets/code_blocks/<section_id>.json
```

Each file is a JSON array of objects:

```json
[
  { "lang": "python", "code": "<verbatim code string>" },
  ...
]
```

### Rule: Do NOT translate code tokens

When writing the translated MDX for a section, **paste code exactly as it
appears in `assets/code_blocks/<section_id>.json`**.

- **You MAY translate**: comments (`# …`, `// …`, `/* … */`) inside code blocks.
- **You MUST NOT change**: variable names, function names, operators, string
  literals that are not user-facing messages, import paths, or any other
  non-comment tokens.

### How to copy a code block into your MDX

1. Open `assets/code_blocks/<section_id>.json`.
2. For each object in the array, create a fenced block in your MDX:

   ````mdx
   ```python
   <paste the value of "code" here>
   ```
   ````

3. You may translate the comments inside the fence, but leave all other lines
   untouched.

### Integrity gate

The CI gate `scripts/gates/check_code_integrity.py` will run automatically on
your PR. It compares the non-comment lines in your MDX code blocks against the
reference in `assets/code_blocks/<section_id>.json`. Any mismatch will fail the
check. The gate auto-passes for sections that have no `code_blocks` JSON file
(i.e., sections with no code).

To run the check locally:

```bash
python3 scripts/gates/check_code_integrity.py <section_id> path/to/translated.mdx
```

Example:

```bash
python3 scripts/gates/check_code_integrity.py ch02 src/pages/ko/ch02.mdx
```

Exit 0 = pass, non-zero = fail (diff printed to stderr).

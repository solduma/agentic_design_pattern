#!/usr/bin/env python3
"""
check_code_integrity.py <section_id> <mdx_file>

Compare code-block lines in the translated MDX against the original verbatim
code blocks in assets/code_blocks/<section_id>.json (produced by scripts/extract_code.py).

Rules:
  - If no code_blocks JSON file exists for a section → auto-pass (section has no code).
  - Non-blank, non-comment lines extracted from fenced blocks in the MDX must
    match those from the reference JSON exactly (order-insensitive set match).
  - Comment lines (# // /* * <!--) may differ (translators may translate comments).

Exit 0 on pass, non-zero on any code-line diff.
"""
import sys
import os
import re
import json

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CODE_BLOCKS_DIR = os.path.join(REPO_ROOT, "assets", "code_blocks")

FENCED_CODE_RE = re.compile(r"(`{3,})([\w]*)\n(.*?)\1", re.DOTALL)
COMMENT_LINE_RE = re.compile(r"^\s*(#|//|/\*|\*|<!--)")

# Languages that are diagram/markup additions (not original code) — excluded from integrity check
EXCLUDED_LANGS = {"mermaid", "mmd"}


def extract_mdx_code_lines(text: str) -> list[str]:
    """Return all lines from fenced code blocks in an MDX file, excluding diagram blocks."""
    lines = []
    for match in FENCED_CODE_RE.findall(text):
        # match is (fence_chars, lang_tag, content)
        lang = match[1].lower().strip() if len(match) >= 2 else ""
        block = match[2] if len(match) >= 3 else match[1]
        if lang in EXCLUDED_LANGS:
            continue  # skip translated diagram blocks — not original code
        lines.extend(block.splitlines())
    return lines


def is_comment(line: str) -> bool:
    return bool(COMMENT_LINE_RE.match(line)) or line.strip().startswith("//")


def code_only_lines(lines: list[str]) -> list[str]:
    """Return non-blank, non-comment lines (rstripped)."""
    return [l.rstrip() for l in lines if l.strip() and not is_comment(l)]


def load_reference_lines(section_id: str) -> list[str] | None:
    """
    Load code lines from assets/code_blocks/<section_id>.json.
    Returns None if file does not exist (auto-pass).
    Returns [] if file exists but is empty (no code expected).
    """
    json_path = os.path.join(CODE_BLOCKS_DIR, f"{section_id}.json")
    if not os.path.isfile(json_path):
        return None  # auto-pass
    blocks = json.loads(open(json_path, encoding="utf-8").read())
    lines = []
    for block in blocks:
        lines.extend(block["code"].splitlines())
    return lines


def check_code_integrity(section_id: str, mdx_file: str) -> int:
    ref_raw = load_reference_lines(section_id)
    if ref_raw is None:
        print(f"[code_integrity] PASS (no reference): {section_id}")
        return 0

    if not os.path.isfile(mdx_file):
        print(f"ERROR: MDX file not found: {mdx_file}", file=sys.stderr)
        return 1

    mdx_text = open(mdx_file, encoding="utf-8").read()

    ref_lines = code_only_lines(ref_raw)
    mdx_lines = code_only_lines(extract_mdx_code_lines(mdx_text))

    # Use set comparison (order-insensitive; duplicates count)
    ref_set = set(ref_lines)
    mdx_set = set(mdx_lines)

    if ref_set == mdx_set:
        print(f"[code_integrity] PASS: {section_id}")
        return 0

    # If MDX has no code at all, it's a clear fail
    if not mdx_lines and ref_lines:
        print(
            f"[code_integrity] FAIL: {section_id} — MDX has no code blocks "
            f"but reference has {len(ref_lines)} non-comment lines",
            file=sys.stderr,
        )
        return 1

    # Diff report
    print(f"[code_integrity] FAIL: {section_id} — code lines differ", file=sys.stderr)
    max_show = 10
    shown = 0
    for line in ref_set - mdx_set:
        if shown >= max_show:
            break
        print(f"  MISSING from MDX: {line!r}", file=sys.stderr)
        shown += 1
    for line in mdx_set - ref_set:
        if shown >= max_show:
            break
        print(f"  EXTRA in MDX:     {line!r}", file=sys.stderr)
        shown += 1
    return 1


def self_test():
    testdata = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdata")
    os.makedirs(testdata, exist_ok=True)

    # Write a synthetic code_blocks JSON for a test section
    ref_json = os.path.join(testdata, "ch_selftest.json")
    with open(ref_json, "w") as f:
        json.dump(
            [{"lang": "python", "code": "x = 1\ny = 2\n# this is a comment\nz = 3"}],
            f,
        )

    # Good MDX: same non-comment code, comment may differ
    good_mdx = os.path.join(testdata, "ch_selftest_good.mdx")
    with open(good_mdx, "w") as f:
        f.write(
            "# Test\n\n번역된 텍스트\n\n"
            "```python\n"
            "x = 1\n"
            "y = 2\n"
            "# 이것은 주석입니다\n"  # translated comment — OK
            "z = 3\n"
            "```\n"
        )

    # Bad MDX: changed code line
    bad_mdx = os.path.join(testdata, "ch_selftest_bad.mdx")
    with open(bad_mdx, "w") as f:
        f.write(
            "# Test\n\n번역된 텍스트\n\n"
            "```python\n"
            "x = 999\n"  # wrong!
            "y = 2\n"
            "z = 3\n"
            "```\n"
        )

    # No-code section (no JSON file) → auto-pass
    nocode_mdx = os.path.join(testdata, "ch_selftest_nocode.mdx")
    with open(nocode_mdx, "w") as f:
        f.write("# Test\n\nSome text without code\n")

    # Temporarily override CODE_BLOCKS_DIR
    mod = sys.modules[__name__]
    orig_dir = mod.CODE_BLOCKS_DIR
    mod.CODE_BLOCKS_DIR = testdata

    rc_good = check_code_integrity("ch_selftest", good_mdx)
    rc_bad = check_code_integrity("ch_selftest", bad_mdx)
    rc_nocode = check_code_integrity("ch_selftest_noexist", nocode_mdx)

    mod.CODE_BLOCKS_DIR = orig_dir

    ok = rc_good == 0 and rc_bad != 0 and rc_nocode == 0
    print(
        f"[check_code_integrity] self-test {'PASS' if ok else 'FAIL'} "
        f"(good={rc_good}, bad={rc_bad}, nocode={rc_nocode})"
    )
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <section_id> <mdx_file>", file=sys.stderr)
        sys.exit(1)
    sys.exit(check_code_integrity(sys.argv[1], sys.argv[2]))

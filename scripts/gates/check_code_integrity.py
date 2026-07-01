#!/usr/bin/env python3
"""
check_code_integrity.py <section_id> <mdx_file>
Compare code-block lines in the translated MDX against the original code blocks
in assets/sections/<section_id>.txt.
Code lines (non-comment) must be unchanged; comment lines may differ.
Exit 0 on pass, non-zero on any code-line diff.
"""
import sys
import os
import re

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SECTIONS_DIR = os.path.join(REPO_ROOT, "assets", "sections")

FENCED_CODE_RE = re.compile(r"```[\w]*\n(.*?)```", re.DOTALL)
COMMENT_LINE_RE = re.compile(r"^\s*(#|//|/\*|\*|<!--)")


def extract_code_blocks(text: str) -> list[str]:
    """Return list of lines from all fenced code blocks."""
    lines = []
    for block in FENCED_CODE_RE.findall(text):
        for line in block.splitlines():
            lines.append(line)
    return lines


def is_comment(line: str) -> bool:
    return bool(COMMENT_LINE_RE.match(line)) or line.strip().startswith("//")


def code_only_lines(lines: list[str]) -> list[str]:
    """Return non-blank, non-comment lines (stripped)."""
    return [l.rstrip() for l in lines if l.strip() and not is_comment(l)]


def check_code_integrity(section_id: str, mdx_file: str) -> int:
    orig_path = os.path.join(SECTIONS_DIR, f"{section_id}.txt")
    if not os.path.isfile(orig_path):
        print(f"WARN: original section not found: {orig_path} — skipping check", file=sys.stderr)
        return 0

    if not os.path.isfile(mdx_file):
        print(f"ERROR: MDX file not found: {mdx_file}", file=sys.stderr)
        return 1

    orig_text = open(orig_path, encoding="utf-8").read()
    mdx_text = open(mdx_file, encoding="utf-8").read()

    orig_lines = code_only_lines(extract_code_blocks(orig_text))
    mdx_lines = code_only_lines(extract_code_blocks(mdx_text))

    if orig_lines == mdx_lines:
        print(f"[code_integrity] PASS: {section_id}")
        return 0

    # Diff report
    print(f"[code_integrity] FAIL: {section_id} — code lines differ", file=sys.stderr)
    max_show = 10
    shown = 0
    orig_set = set(orig_lines)
    mdx_set = set(mdx_lines)
    for line in orig_set - mdx_set:
        if shown >= max_show:
            break
        print(f"  MISSING from MDX: {line!r}", file=sys.stderr)
        shown += 1
    for line in mdx_set - orig_set:
        if shown >= max_show:
            break
        print(f"  EXTRA in MDX:     {line!r}", file=sys.stderr)
        shown += 1
    return 1


def self_test():
    testdata = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testdata")

    # Write synthetic section
    orig_txt = os.path.join(testdata, "ch_test.txt")
    with open(orig_txt, "w") as f:
        f.write("Some text\n\n```python\nx = 1\ny = 2\n```\n")

    # Good MDX: same code
    good_mdx = os.path.join(testdata, "ch_test_good.mdx")
    with open(good_mdx, "w") as f:
        f.write("# Test\n\n번역된 텍스트\n\n```python\nx = 1\ny = 2\n```\n")

    # Bad MDX: changed code
    bad_mdx = os.path.join(testdata, "ch_test_bad.mdx")
    with open(bad_mdx, "w") as f:
        f.write("# Test\n\n번역된 텍스트\n\n```python\nx = 999\ny = 2\n```\n")

    # Temporarily override SECTIONS_DIR
    import importlib, types
    mod = sys.modules[__name__]
    orig_dir = mod.SECTIONS_DIR
    mod.SECTIONS_DIR = testdata

    rc_good = check_code_integrity("ch_test", good_mdx)
    rc_bad = check_code_integrity("ch_test", bad_mdx)

    mod.SECTIONS_DIR = orig_dir

    ok = rc_good == 0 and rc_bad != 0
    print(f"[check_code_integrity] self-test {'PASS' if ok else 'FAIL'} "
          f"(good={rc_good}, bad={rc_bad})")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <section_id> <mdx_file>", file=sys.stderr)
        sys.exit(1)
    sys.exit(check_code_integrity(sys.argv[1], sys.argv[2]))

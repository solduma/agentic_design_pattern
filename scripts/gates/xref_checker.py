#!/usr/bin/env python3
"""
xref_checker.py <mdx_file> [<mdx_file>...]
Grep for forbidden cross-reference patterns; also verify <CrossRef> targets exist.

Forbidden patterns (must be 0 occurrences):
  Figure\\s+\\d+\\.\\d+
  Table\\s+\\d+\\.\\d+
  Appendix\\s+[A-G]
  그림\\s*\\d
  표\\s*\\d
  부록\\s*[A-G]
  섹션\\s*\\d
  bare `Index` (not inside whitelisted notice)

Whitelist: "색인 대신 검색" notice string (anywhere it appears).

CrossRef targets: <CrossRef id="xxx"> must point to a known section in manifest.
Exit 0 on pass, 1 on any violation.
"""
import sys
import os
import re
import json
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
MANIFEST_PATH = os.path.join(REPO_ROOT, "assets", "manifest.json")

FORBIDDEN_PATTERNS = [
    (re.compile(r"Figure\s+\d+\.\d+"), "Figure N.N reference"),
    (re.compile(r"Table\s+\d+\.\d+"), "Table N.N reference"),
    (re.compile(r"Appendix\s+[A-G]\b"), "Appendix X reference"),
    (re.compile(r"그림\s*\d"), "그림 N reference"),
    (re.compile(r"표\s*\d"), "표 N reference"),
    (re.compile(r"부록\s*[A-G]\b"), "부록 X reference"),
    (re.compile(r"섹션\s*\d"), "섹션 N reference"),
    (re.compile(r"\bIndex\b"), "bare Index reference"),
]

WHITELIST_STRINGS = [
    "색인 대신 검색",
]

CROSSREF_RE = re.compile(r'<CrossRef\s+id=["\']([^"\']+)["\']')


def load_known_ids() -> set[str]:
    if not os.path.isfile(MANIFEST_PATH):
        return set()
    with open(MANIFEST_PATH) as f:
        data = json.load(f)
    return {s["id"] for s in data.get("sections", [])}


def line_is_whitelisted(line: str) -> bool:
    return any(w in line for w in WHITELIST_STRINGS)


def check_file(path: str, known_ids: set[str]) -> list[str]:
    violations = []
    lines = open(path, encoding="utf-8").readlines()
    for lineno, line in enumerate(lines, 1):
        if line_is_whitelisted(line):
            continue
        for pattern, label in FORBIDDEN_PATTERNS:
            if pattern.search(line):
                violations.append(
                    f"{path}:{lineno}: forbidden {label}: {line.rstrip()!r}"
                )

    # Check CrossRef targets
    text = "".join(lines)
    for m in CROSSREF_RE.finditer(text):
        target = m.group(1)
        if known_ids and target not in known_ids:
            lineno = text[: m.start()].count("\n") + 1
            violations.append(
                f"{path}:{lineno}: <CrossRef id={target!r}> — target not in manifest"
            )

    return violations


def xref_check(files: list[str]) -> int:
    known_ids = load_known_ids()
    all_violations = []
    for f in files:
        if not os.path.isfile(f):
            print(f"WARN: file not found: {f}", file=sys.stderr)
            continue
        all_violations.extend(check_file(f, known_ids))

    if all_violations:
        print(f"[xref_checker] FAIL: {len(all_violations)} violation(s):", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        return 1

    print(f"[xref_checker] PASS: checked {len(files)} file(s), 0 violations.")
    return 0


def self_test():
    testdata = os.path.join(SCRIPT_DIR, "testdata")

    # Good file: no forbidden patterns
    good = os.path.join(testdata, "xref_good.mdx")
    with open(good, "w") as f:
        f.write("# 테스트\n\n에이전트 패턴에 대한 설명입니다.\n\n색인 대신 검색을 사용하세요.\n")

    # Bad file: contains Figure 1.2
    bad = os.path.join(testdata, "xref_bad.mdx")
    with open(bad, "w") as f:
        f.write("# 테스트\n\n그림 1은 다음과 같습니다. Figure 1.2 참조.\n")

    # Bad CrossRef
    bad_xref = os.path.join(testdata, "xref_bad_crossref.mdx")
    with open(bad_xref, "w") as f:
        f.write('# 테스트\n\n<CrossRef id="nonexistent-section" />\n')

    known_ids = load_known_ids()

    rc_good = xref_check([good])
    rc_bad = xref_check([bad])
    rc_xref = xref_check([bad_xref]) if known_ids else 0  # skip if no manifest

    ok = rc_good == 0 and rc_bad != 0
    print(f"[xref_checker] self-test {'PASS' if ok else 'FAIL'} "
          f"(good={rc_good}, bad={rc_bad}, bad_xref={rc_xref})")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <mdx_file> [<mdx_file>...]", file=sys.stderr)
        sys.exit(1)
    sys.exit(xref_check(sys.argv[1:]))

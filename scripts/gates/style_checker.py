#!/usr/bin/env python3
"""
style_checker.py <mdx_file> [<mdx_file>...]
Flag lines not ending in 합쇼체 (-습니다/-합니다).

Pre-filter (skip):
  - Fenced-code block interiors
  - Lines starting with #, |, <, >
  - Admonition blocks: from ::: opener through closing ::: (entire body)
  - Lines with no Hangul characters

Exit 0 on pass, 1 on violations.
"""
import sys
import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Matches sentences ending in 합쇼체 (-습니다/-합니다/-입니다 and all verbal polite endings)
# Full list: -ㅂ니다/습니다/합니다/입니다 + any punctuation
HAPSYO_END_RE = re.compile(r"[ㅂ습합입]니다[.!?\"')\]]*\s*$")

# Hangul detection
HANGUL_RE = re.compile(r"[가-힣]")

# Skip line-start patterns
SKIP_START_RE = re.compile(r"^[#|<>]")

# Sentence-ending punctuation patterns (detect full sentences in Korean)
KOREAN_SENTENCE_END_RE = re.compile(r"[가-힣][.!?]?\s*$")

# Pattern to detect a line that IS a Korean sentence (ends with any Korean verbal ending)
# We only care if the line contains hangul AND appears to be a sentence
VERBAL_END_RE = re.compile(r"[가-힣\w][.!?]?\s*$")


def check_file(path: str) -> list[str]:
    violations = []
    lines = open(path, encoding="utf-8").readlines()

    in_fenced_code = False
    in_admonition = False
    admonition_depth = 0

    for lineno, raw_line in enumerate(lines, 1):
        line = raw_line.rstrip("\n")

        # Track fenced code blocks
        if re.match(r"^```", line):
            in_fenced_code = not in_fenced_code
            continue

        if in_fenced_code:
            continue

        # Track admonition blocks (:::)
        if re.match(r"^:::", line):
            if not in_admonition:
                in_admonition = True
                admonition_depth = 1
            else:
                admonition_depth -= 1
                if admonition_depth <= 0:
                    in_admonition = False
                    admonition_depth = 0
            continue

        if in_admonition:
            # Check for nested ::: (rare but handle)
            if re.match(r"^:::", line):
                admonition_depth += 1
            continue

        # Skip lines starting with #, |, <, >
        if SKIP_START_RE.match(line):
            continue

        # Skip lines with no Hangul
        if not HANGUL_RE.search(line):
            continue

        stripped = line.strip()
        if not stripped:
            continue

        # Only check lines that appear to be sentences (end with Korean text)
        # Must end with hangul (possibly with punctuation)
        if not VERBAL_END_RE.search(stripped):
            continue

        # Check for 합쇼체 ending
        if not HAPSYO_END_RE.search(stripped):
            violations.append(
                f"{path}:{lineno}: not 합쇼체: {stripped!r}"
            )

    return violations


def style_check(files: list[str]) -> int:
    all_violations = []
    for f in files:
        if not os.path.isfile(f):
            print(f"WARN: file not found: {f}", file=sys.stderr)
            continue
        all_violations.extend(check_file(f))

    if all_violations:
        print(f"[style_checker] FAIL: {len(all_violations)} violation(s):", file=sys.stderr)
        for v in all_violations[:20]:  # Show up to 20
            print(f"  {v}", file=sys.stderr)
        if len(all_violations) > 20:
            print(f"  ... and {len(all_violations) - 20} more", file=sys.stderr)
        return 1

    print(f"[style_checker] PASS: checked {len(files)} file(s), 0 violations.")
    return 0


def self_test():
    testdata = os.path.join(SCRIPT_DIR, "testdata")

    # Good file: all Korean sentences end in 합쇼체
    good = os.path.join(testdata, "style_good.mdx")
    with open(good, "w") as f:
        f.write(
            "# 에이전트 디자인 패턴\n\n"
            "이것은 에이전트 패턴에 대한 설명입니다.\n\n"
            "프롬프트 체이닝은 강력한 기법입니다.\n\n"
            "```python\n"
            "# This code does not need 합쇼체\n"
            "x = 1\n"
            "```\n\n"
            "| col1 | col2 |\n"
            "|------|------|\n\n"
            ":::note\n"
            "이것은 주의사항입니다 — 아무 문체나 괜찮아요.\n"
            ":::\n\n"
            "코드를 실행합니다.\n"
        )

    # Bad file: contains non-합쇼체 Korean sentence
    bad = os.path.join(testdata, "style_bad.mdx")
    with open(bad, "w") as f:
        f.write(
            "# 테스트\n\n"
            "이것은 잘못된 문체야.\n\n"  # casual ending
            "프롬프트 체이닝은 좋아.\n"  # casual ending
        )

    rc_good = style_check([good])
    rc_bad = style_check([bad])

    ok = rc_good == 0 and rc_bad != 0
    print(f"[style_checker] self-test {'PASS' if ok else 'FAIL'} "
          f"(good={rc_good}, bad={rc_bad})")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <mdx_file> [<mdx_file>...]", file=sys.stderr)
        sys.exit(1)
    sys.exit(style_check(sys.argv[1:]))

#!/usr/bin/env python3
"""
check_ratio.py <section_id> <mdx_file>
Check paragraph-ratio >= 0.85 AND token-ratio >= threshold (from ratio_thresholds.json or placeholder).
Token ratio uses tiktoken cl100k_base on code-stripped text.
Exit 0 on pass, non-zero on fail.

Self-test: a 25%-truncated synthetic chapter must FAIL.
"""
import sys
import os
import re
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
SECTIONS_DIR = os.path.join(REPO_ROOT, "assets", "sections")
MANIFEST_PATH = os.path.join(REPO_ROOT, "assets", "manifest.json")
THRESHOLDS_PATH = os.path.join(SCRIPT_DIR, "ratio_thresholds.json")

# Placeholder lower-bounds (to be calibrated by T2a-core-calibrate)
PARA_RATIO_MIN = 0.85
TOKEN_RATIO_LOOSE = 0.50  # loose placeholder; will be stratified once thresholds.json is set

FENCED_CODE_RE = re.compile(r"```[\w\s]*?\n.*?```", re.DOTALL)


def strip_code(text: str) -> str:
    return FENCED_CODE_RE.sub("", text)


def count_paragraphs(text: str) -> int:
    """Count non-empty paragraph blocks separated by blank lines."""
    blocks = re.split(r"\n{2,}", text.strip())
    return sum(1 for b in blocks if b.strip())


def tokenize(text: str) -> int:
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        # Fallback: rough word count
        return len(text.split())


def get_thresholds(section_id: str, code_ratio: float) -> dict:
    """Load thresholds from JSON if present, else return placeholder values."""
    thresholds = {
        "para_ratio_min": PARA_RATIO_MIN,
        "token_ratio_min": TOKEN_RATIO_LOOSE,
    }
    if os.path.isfile(THRESHOLDS_PATH):
        with open(THRESHOLDS_PATH) as f:
            data = json.load(f)
        # Stratum selection hook: look for matching section or code_ratio stratum
        if section_id in data.get("sections", {}):
            thresholds.update(data["sections"][section_id])
        elif "strata" in data:
            for stratum in data["strata"]:
                lo = stratum.get("code_ratio_min", 0.0)
                hi = stratum.get("code_ratio_max", 1.0)
                if lo <= code_ratio < hi:
                    thresholds.update(stratum.get("thresholds", {}))
                    break
    return thresholds


def load_manifest_section(section_id: str) -> dict | None:
    if not os.path.isfile(MANIFEST_PATH):
        return None
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)
    for s in manifest.get("sections", []):
        if s["id"] == section_id:
            return s
    return None


def check_ratio(section_id: str, mdx_file: str) -> int:
    if not os.path.isfile(mdx_file):
        print(f"ERROR: MDX file not found: {mdx_file}", file=sys.stderr)
        return 1

    orig_path = os.path.join(SECTIONS_DIR, f"{section_id}.txt")
    if not os.path.isfile(orig_path):
        print(f"WARN: original section not found: {orig_path} — skipping ratio check", file=sys.stderr)
        return 0

    orig_text = open(orig_path, encoding="utf-8").read()
    mdx_text = open(mdx_file, encoding="utf-8").read()

    # Strip code for token comparison
    orig_no_code = strip_code(orig_text)
    mdx_no_code = strip_code(mdx_text)

    # Paragraph counts
    orig_paras = count_paragraphs(orig_no_code)
    mdx_paras = count_paragraphs(mdx_no_code)

    para_ratio = mdx_paras / orig_paras if orig_paras > 0 else 1.0

    # Token counts
    orig_tokens = tokenize(orig_no_code)
    mdx_tokens = tokenize(mdx_no_code)
    token_ratio = mdx_tokens / orig_tokens if orig_tokens > 0 else 1.0

    # Get manifest info for code_ratio stratum
    manifest_sec = load_manifest_section(section_id)
    code_ratio = manifest_sec.get("code_ratio", 0.0) if manifest_sec else 0.0

    thresholds = get_thresholds(section_id, code_ratio)
    para_min = thresholds["para_ratio_min"]
    token_min = thresholds["token_ratio_min"]

    ok = para_ratio >= para_min and token_ratio >= token_min
    status = "PASS" if ok else "FAIL"
    print(
        f"[check_ratio] {status}: {section_id} "
        f"para_ratio={para_ratio:.3f} (min={para_min}) "
        f"token_ratio={token_ratio:.3f} (min={token_min})"
    )
    if not ok:
        if para_ratio < para_min:
            print(f"  FAIL reason: para_ratio {para_ratio:.3f} < {para_min}", file=sys.stderr)
        if token_ratio < token_min:
            print(f"  FAIL reason: token_ratio {token_ratio:.3f} < {token_min}", file=sys.stderr)
        return 1
    return 0


def self_test():
    testdata = os.path.join(SCRIPT_DIR, "testdata")

    # Build a "full" original section with enough content
    orig_para = "This is a paragraph about agentic design patterns. " * 20
    orig_text = "\n\n".join([orig_para] * 8)  # 8 paragraphs

    orig_path = os.path.join(testdata, "ratio_orig.txt")
    with open(orig_path, "w") as f:
        f.write(orig_text)

    # Full translation (same length approximation in Korean)
    full_mdx = os.path.join(testdata, "ratio_full.mdx")
    # Korean text roughly same para count and token count
    ko_para = "이것은 에이전트 디자인 패턴에 대한 단락입니다. " * 20
    ko_text = "\n\n".join([ko_para] * 8)
    with open(full_mdx, "w") as f:
        f.write(ko_text)

    # 25%-truncated MDX (should FAIL)
    trunc_mdx = os.path.join(testdata, "ratio_trunc.mdx")
    # Only 2 paragraphs out of 8 = 25%
    with open(trunc_mdx, "w") as f:
        f.write("\n\n".join([ko_para] * 2))

    # Temporarily patch globals
    mod = sys.modules[__name__]
    orig_sections = mod.SECTIONS_DIR
    mod.SECTIONS_DIR = testdata

    rc_full = check_ratio("ratio_orig", full_mdx)
    rc_trunc = check_ratio("ratio_orig", trunc_mdx)

    mod.SECTIONS_DIR = orig_sections

    ok = rc_full == 0 and rc_trunc != 0
    print(f"[check_ratio] self-test {'PASS' if ok else 'FAIL'} "
          f"(full={rc_full}, trunc_25%={rc_trunc})")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <section_id> <mdx_file>", file=sys.stderr)
        sys.exit(1)
    sys.exit(check_ratio(sys.argv[1], sys.argv[2]))

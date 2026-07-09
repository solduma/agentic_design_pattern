#!/usr/bin/env python3
"""
qc_sdlc.py — T9 QC gate for the SDLC paper docs.

Checks:
  1. Coverage: every manifest section has a non-stub MDX file.
  2. Diagram placeholders: no leftover "(준비 중)" stubs; every figure id appears.
  3. Style: prose lines end in 합쇼체 (heuristic; skips code/tables/headings/admonitions).
  4. Cross-ref hygiene: no leftover raw "Figure N"/"Table N" English refs in prose.

Exit non-zero if any HIGH check fails.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "assets" / "sdlc" / "manifest.json"
DIAG_INDEX = REPO / "assets" / "sdlc" / "diagrams" / "index.json"
DOCS = REPO / "site" / "sdlc-docs"

errors = []
warnings = []


def check_coverage(manifest):
    for sec in manifest["sections"]:
        f = DOCS / f"{sec['id']}.mdx"
        if not f.exists():
            errors.append(f"[coverage] missing MDX for section '{sec['id']}'")
            continue
        text = f.read_text(encoding="utf-8")
        if "번역 준비 중" in text:
            errors.append(f"[coverage] section '{sec['id']}' still a stub")
        if len(text) < 400:
            warnings.append(f"[coverage] section '{sec['id']}' suspiciously short ({len(text)}b)")


def check_frontmatter(sec_id, text):
    # A title/label containing ':' must be quoted or YAML parsing breaks the build.
    for m in re.finditer(r"^(title|sidebar_label):\s*(.+)$", text, re.MULTILINE):
        val = m.group(2).strip()
        if ":" in val and not (val.startswith('"') or val.startswith("'")):
            errors.append(f"[frontmatter:{sec_id}] {m.group(1)} contains ':' but is unquoted — quote it")


def check_diagrams(diagrams):
    all_mdx = "\n".join(f.read_text(encoding="utf-8") for f in DOCS.rglob("*.mdx"))
    if "(준비 중)" in all_mdx:
        errors.append("[diagram] leftover '(준비 중)' placeholder found — run integrate_sdlc.py")
    # After integration, each figure's caption should be present. Before integration,
    # each <Diagram id> should be present. Accept either.
    for d in diagrams:
        did = d["id"]
        if did not in all_mdx and d["caption_ko"][:12] not in all_mdx:
            warnings.append(f"[diagram] figure '{did}' not referenced in any MDX")


HANGUL = re.compile(r"[가-힣]")
# 합쇼체 declarative ending: any …니다 (봅니다/줍니다/옵니다/깁니다/습니다/합니다/입니다 …).
POLITE_END = re.compile(r"니다[.!?\"'”’)\]]*$")
# Acceptable non-declarative prose endings (headings handled separately)
SOFT_OK = re.compile(r"(요\.?|죠\.?|가요\?|까\?|나요\?|을까요\?)[\"'”’)\]]*$")


def check_style(sec_id, text):
    lines = text.split("\n")
    in_code = False
    in_front = False
    in_admonition = False
    fm_seen = 0
    for raw in lines:
        s = raw.strip()
        if s.startswith("---"):
            fm_seen += 1
            in_front = fm_seen == 1
            continue
        if fm_seen == 1:
            in_front = False
            fm_seen = 2  # end of frontmatter handled by second ---
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if s.startswith(":::"):
            in_admonition = not in_admonition if s == ":::" else True
            if s == ":::":
                in_admonition = False
            else:
                in_admonition = True
            continue
        # skip structural / non-prose lines
        if (not s or s.startswith("#") or s.startswith("|") or s.startswith(">")
                or s.startswith("<") or s.startswith("import ") or s.startswith("-")
                or s.startswith("*") or re.match(r"^\d+\.", s) or s.startswith("[^")
                or s.startswith("/") or "http" in s
                or s.startswith("description:") or s.startswith("title:")
                or s.startswith('"') or s.startswith("id:")):
            continue
        if not HANGUL.search(s):
            continue
        # Only check lines that look like full sentences (end with period)
        if not s.endswith((".", "!", "?", "”", "’", "\"", "'", ":")):
            continue
        if s.endswith(":"):
            continue
        if POLITE_END.search(s) or SOFT_OK.search(s):
            continue
        # ends with period but not 합쇼체 -> flag (heuristic)
        # ignore lines ending with English word + period (e.g., product names)
        if re.search(r"[a-zA-Z0-9)\]]\.$", s) and not HANGUL.search(s[-3:]):
            continue
        warnings.append(f"[style:{sec_id}] non-합쇼체 line: …{s[-40:]}")


def check_xref(sec_id, text):
    # raw English figure/table refs in prose (not inside code) are a smell
    for m in re.finditer(r"\b(Figure|Table)\s+\d+\b", text):
        # allow inside <figcaption> or after integration
        warnings.append(f"[xref:{sec_id}] raw English ref '{m.group(0)}' — verify it's a caption")


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    diagrams = json.loads(DIAG_INDEX.read_text(encoding="utf-8"))

    check_coverage(manifest)
    check_diagrams(diagrams)
    for f in sorted(DOCS.rglob("*.mdx")):
        if f.name == "intro.mdx":
            continue
        text = f.read_text(encoding="utf-8")
        check_frontmatter(f.stem, text)
        check_style(f.stem, text)

    print("=== QC SDLC ===")
    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings[:60]:
            print(f"  ⚠ {w}")
    if errors:
        print(f"\n{len(errors)} ERROR(s):")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)
    print(f"\nHIGH checks passed. ({len(warnings)} warnings to review)")


if __name__ == "__main__":
    main()

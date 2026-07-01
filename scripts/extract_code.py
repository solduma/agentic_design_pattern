#!/usr/bin/env python3
"""
extract_code.py — Extract verbatim code blocks from PDF sections.

For each section in assets/manifest.json that has code_ratio > 0,
detects code regions using font/heuristic analysis and emits:
  assets/code_blocks/{section_id}.json

Each JSON file is a list of:
  { "lang": "python|bash|json|text|...", "code": "<verbatim>" }

Usage:
  python3 scripts/extract_code.py               # all sections with code
  python3 scripts/extract_code.py ch02 ch05     # specific sections
  python3 scripts/extract_code.py --all         # force all (even code_ratio==0)
"""

import sys
import os
import json
import re
from pathlib import Path

try:
    import fitz  # pymupdf
except ImportError:
    sys.exit("pymupdf not installed — run: python3 -m pip install pymupdf --break-system-packages")

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "assets" / "manifest.json"
PDF_PATH = REPO_ROOT / "pdf" / "Agentic_Design_Patterns.pdf"
CODE_BLOCKS_DIR = REPO_ROOT / "assets" / "code_blocks"

# Minimum code_ratio to attempt extraction (skip near-zero sections)
CODE_RATIO_THRESHOLD = 0.005

# Heuristics: lines that strongly indicate code
CODE_LEADER_RE = re.compile(
    r"^\s*("
    r"import |from |def |class |async def |return |if |elif |else:|for |while |try:|except|with |"
    r"@\w|print\(|raise |yield |lambda |pass$|break$|continue$|"
    r"\$\s|%pip|%matplotlib|pip install|pip3 |python3? |"
    r'"\w.*":\s*[{\["\d]|'   # JSON key-value
    r"{\s*$|\[\s*$|}\s*,?\s*$|\]\s*,?\s*$|"  # JSON/dict braces
    r"#!|#!/|"  # shebang
    r"curl |wget |git |docker |kubectl |npm |yarn |poetry |"
    r"model\s*=|agent\s*=|client\s*=|response\s*=|result\s*=|output\s*=|"
    r'"""$|""".*"""$|'  # docstrings
    r"[a-zA-Z_]\w*\([^)]*\)\s*:|"  # function def body
    r"[a-zA-Z_]\w*\s*=\s*.+"  # assignment
    r")"
)

# Fonts that are typically monospace/code
MONOSPACE_FONT_HINTS = {
    "courier", "mono", "consol", "code", "inconsolata",
    "sourcecodepro", "source code", "roboto mono", "droid sans mono",
    "menlo", "monaco", "fira", "hack", "jetbrains", "cascadia",
    "anonymous", "ubuntu mono", "dejavusans mono",
}


def is_monospace_font(font_name: str) -> bool:
    name = font_name.lower()
    return any(h in name for h in MONOSPACE_FONT_HINTS)


def looks_like_code_line(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if CODE_LEADER_RE.match(stripped):
        return True
    # Indented (4+ spaces or tab) non-prose
    if re.match(r"^(\t|    )", text) and not re.match(r"^\s{4,}[A-Z]", text):
        return True
    return False


def detect_lang(lines: list[str]) -> str:
    joined = "\n".join(lines)
    if any(re.search(r"^\s*(import |from |def |class |async def )", l) for l in lines):
        return "python"
    if any(re.search(r"^\s*(\$|pip |pip3 |python3? |curl |wget |git |docker )", l) for l in lines):
        return "bash"
    if re.search(r'^\s*\{', joined) and re.search(r'":\s*', joined):
        return "json"
    if any(re.search(r"^\w+:", l) for l in lines) and any(
        re.search(r"^\s+-\s+", l) for l in lines
    ):
        return "yaml"
    return "text"


def extract_code_blocks_from_pages(doc: fitz.Document, page_range: list) -> list[dict]:
    """
    Extract code blocks from the given 1-based page range.
    Returns list of {"lang": ..., "code": ...}.
    """
    start_page, end_page = page_range
    if start_page is None or end_page is None:
        return []

    # Collect all spans with their font info and bbox, per page
    code_runs: list[str] = []  # accumulator of current code run lines
    all_blocks: list[dict] = []

    def flush_run():
        nonlocal code_runs
        if not code_runs:
            return
        # Filter: must have >= 2 non-blank lines to be a real block
        non_blank = [l for l in code_runs if l.strip()]
        if len(non_blank) >= 1:
            lang = detect_lang(code_runs)
            code = "\n".join(code_runs).strip()
            all_blocks.append({"lang": lang, "code": code})
        code_runs = []

    for page_num in range(start_page - 1, end_page):  # 0-indexed
        if page_num >= len(doc):
            break
        page = doc[page_num]

        # Use dict extraction to get font-level span info
        page_dict = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)

        page_lines: list[tuple[bool, str]] = []  # (is_code, text)

        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:  # type 0 = text
                continue
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                line_text = "".join(s.get("text", "") for s in spans)
                # Check if any span is monospace
                has_mono = any(is_monospace_font(s.get("font", "")) for s in spans)
                # Or check by heuristic
                heuristic_code = looks_like_code_line(line_text)
                page_lines.append((has_mono or heuristic_code, line_text))

        # Group consecutive code lines into blocks, allowing up to 1 blank line gap
        in_code = False
        blank_gap = 0
        current_run: list[str] = []

        for is_code, text in page_lines:
            if is_code:
                if blank_gap > 0 and current_run:
                    # Add the blank lines back into the run
                    current_run.extend([""] * blank_gap)
                blank_gap = 0
                in_code = True
                current_run.append(text)
            elif not text.strip():
                if in_code:
                    blank_gap += 1
                    if blank_gap > 2:
                        # End of block
                        if current_run:
                            non_blank = [l for l in current_run if l.strip()]
                            if len(non_blank) >= 1:
                                lang = detect_lang(current_run)
                                code = "\n".join(current_run).strip()
                                all_blocks.append({"lang": lang, "code": code})
                            current_run = []
                        in_code = False
                        blank_gap = 0
            else:
                if in_code:
                    # Non-code, non-blank: end the current code run
                    if current_run:
                        non_blank = [l for l in current_run if l.strip()]
                        if len(non_blank) >= 1:
                            lang = detect_lang(current_run)
                            code = "\n".join(current_run).strip()
                            all_blocks.append({"lang": lang, "code": code})
                        current_run = []
                    in_code = False
                    blank_gap = 0

        # Flush any remaining run at end of page
        if current_run:
            non_blank = [l for l in current_run if l.strip()]
            if len(non_blank) >= 1:
                lang = detect_lang(current_run)
                code = "\n".join(current_run).strip()
                all_blocks.append({"lang": lang, "code": code})

    # Merge adjacent blocks of same lang that are likely part of the same snippet
    merged = merge_adjacent_blocks(all_blocks)
    return merged


def merge_adjacent_blocks(blocks: list[dict]) -> list[dict]:
    """Merge consecutive blocks of the same language that are small (< 5 lines each)."""
    if not blocks:
        return blocks
    result = [blocks[0]]
    for b in blocks[1:]:
        prev = result[-1]
        # Merge if same lang and both small
        if (prev["lang"] == b["lang"] and
                len(prev["code"].splitlines()) < 8 and
                len(b["code"].splitlines()) < 8):
            result[-1] = {"lang": prev["lang"], "code": prev["code"] + "\n" + b["code"]}
        else:
            result.append(b)
    return result


def process_section(doc: fitz.Document, section: dict, output_dir: Path) -> int:
    """Extract and write code blocks for one section. Returns block count."""
    sid = section["id"]
    page_range = section.get("page_range", [None, None])
    blocks = extract_code_blocks_from_pages(doc, page_range)
    out_path = output_dir / f"{sid}.json"
    if blocks:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(blocks, f, ensure_ascii=False, indent=2)
    else:
        # Write empty array for sections that had code_ratio > 0 but nothing detected
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump([], f)
    return len(blocks)


def main():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    sections = manifest["sections"]

    force_all = "--all" in sys.argv
    requested = [a for a in sys.argv[1:] if not a.startswith("--")]

    CODE_BLOCKS_DIR.mkdir(parents=True, exist_ok=True)

    if not PDF_PATH.exists():
        sys.exit(f"PDF not found: {PDF_PATH}")

    doc = fitz.open(str(PDF_PATH))
    print(f"Opened PDF: {PDF_PATH.name} ({len(doc)} pages)")

    total_blocks = 0
    sections_with_code = 0

    for sec in sections:
        sid = sec["id"]
        code_ratio = sec.get("code_ratio", 0.0)
        page_range = sec.get("page_range", [None, None])

        # Skip sections with no page range (MISSING)
        if page_range[0] is None:
            continue

        if requested:
            if sid not in requested:
                continue
        elif not force_all and code_ratio < CODE_RATIO_THRESHOLD:
            continue

        n = process_section(doc, sec, CODE_BLOCKS_DIR)
        status = f"{n} blocks" if n > 0 else "0 blocks (empty)"
        print(f"  {sid:20s}  ratio={code_ratio:.3f}  -> {status}")
        if n > 0:
            sections_with_code += 1
            total_blocks += n

    doc.close()
    print(f"\nDone. {sections_with_code} sections with code, {total_blocks} total blocks.")
    print(f"Output: {CODE_BLOCKS_DIR}")


if __name__ == "__main__":
    main()

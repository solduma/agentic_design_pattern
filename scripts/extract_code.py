#!/usr/bin/env python3
"""
extract_code.py — Extract verbatim code blocks from PDF sections using monospace font detection.

For each section in assets/manifest.json with code_ratio > threshold, detects code
regions by identifying monospace font spans via pymupdf page.get_text("dict").
Emits: assets/code_blocks/{section_id}.json
  = [{ "lang": "python|bash|json|text|...", "code": "<verbatim>" }]

Strategy:
  - Use page.get_text("dict") (no extra flags) to get span-level font info.
  - A line is CODE if ANY non-empty span on that line uses a monospace font
    (font name contains 'Mono', 'Courier', 'Consol', 'Menlo', 'Code',
    'Fixed', 'Terminal', 'Inconsolata', 'Hack', 'Fira', 'JetBrains',
    'Cascadia', 'Anonymous', 'DejaVu', 'Source Code').
  - Consecutive code lines (with up to 2 intervening blank lines) form one block.
  - NO heuristic line-content matching — font is the sole signal.

Usage:
  python3 scripts/extract_code.py               # all sections with code_ratio > threshold
  python3 scripts/extract_code.py ch02 ch05     # specific sections only
  python3 scripts/extract_code.py --all         # all sections including zero-ratio ones
"""

import sys
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

CODE_RATIO_THRESHOLD = 0.005

# Monospace font name fragments (case-insensitive substring match)
MONOSPACE_HINTS = (
    "mono", "courier", "consol", "menlo", "monaco",
    "code", "fixed", "terminal", "inconsolata", "hack",
    "fira", "jetbrain", "cascadia", "anonymous", "dejavu",
    "sourcecodepro", "source code",
)


def is_monospace(font_name: str) -> bool:
    name = font_name.lower()
    return any(h in name for h in MONOSPACE_HINTS)


def detect_lang(lines: list[str]) -> str:
    """Heuristically determine language from code content."""
    joined = "\n".join(lines)
    # Python indicators (check all lines, not just first)
    if re.search(r"(^|\n)\s*(import |from \w+ import|def |class |async def )", joined):
        return "python"
    # Python assignments / calls that are clear Python
    if re.search(r"(^|\n)\s*\w+ = \w|\w+\(", joined) and re.search(r"#", joined):
        return "python"  # Python-style comment + assignments
    # Bash
    if re.search(r"(^|\n)\s*(\$\s?|pip3? |python3? |curl |wget |git |docker |npm |poetry )", joined):
        return "bash"
    # JSON
    stripped = joined.strip()
    if (stripped.startswith("{") or stripped.startswith("[")) and re.search(r'":\s*', joined):
        return "json"
    # YAML
    if (re.search(r"(^|\n)\w[\w\s-]*:\s*", joined)
            and re.search(r"(^|\n)\s+-\s+", joined)):
        return "yaml"
    return "text"


def extract_code_blocks_from_pages(doc: fitz.Document, page_range: list) -> list[dict]:
    """
    Extract code blocks from 1-based page_range using monospace font detection only.
    Returns list of {"lang": ..., "code": ...}.
    """
    start_page, end_page = page_range
    if start_page is None or end_page is None:
        return []

    all_blocks: list[dict] = []
    current_run: list[str] = []
    blank_gap: int = 0

    def flush():
        nonlocal current_run, blank_gap
        # Strip trailing blank lines
        while current_run and not current_run[-1].strip():
            current_run.pop()
        if current_run:
            lang = detect_lang(current_run)
            all_blocks.append({"lang": lang, "code": "\n".join(current_run)})
        current_run = []
        blank_gap = 0

    for page_num in range(start_page - 1, end_page):  # convert to 0-indexed
        if page_num >= len(doc):
            break
        page = doc[page_num]

        # get_text("dict") without extra flags gives correct font names
        page_dict = page.get_text("dict")

        # Collect (y0, is_code, text) for all lines on this page
        line_records: list[tuple[float, bool, str]] = []

        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                line_text = "".join(s.get("text", "") for s in spans)
                # Code = any non-empty span is monospace
                has_mono = any(
                    is_monospace(s.get("font", ""))
                    for s in spans
                    if s.get("text", "").strip()
                )
                y0 = line.get("bbox", (0, 0, 0, 0))[1]
                line_records.append((y0, has_mono, line_text))

        # Sort by vertical position to ensure reading order
        line_records.sort(key=lambda r: r[0])

        for _y0, is_code, text in line_records:
            if is_code:
                # Re-include any held blank lines into the current run
                if blank_gap > 0 and current_run:
                    current_run.extend([""] * blank_gap)
                blank_gap = 0
                current_run.append(text.rstrip())
            elif not text.strip():
                if current_run:
                    blank_gap += 1
                    if blank_gap > 2:
                        flush()
            else:
                # Prose line — end any open code block
                if current_run or blank_gap:
                    flush()

        # Flush at page boundary (code rarely spans pages in this PDF)
        flush()

    flush()  # final safety flush
    return all_blocks


def process_section(doc: fitz.Document, section: dict, output_dir: Path) -> int:
    """Extract and write code blocks for one section. Returns block count."""
    sid = section["id"]
    page_range = section.get("page_range", [None, None])
    blocks = extract_code_blocks_from_pages(doc, page_range)
    out_path = output_dir / f"{sid}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(blocks, f, ensure_ascii=False, indent=2)
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

        if page_range[0] is None:
            continue

        if requested:
            if sid not in requested:
                continue
        elif not force_all and code_ratio < CODE_RATIO_THRESHOLD:
            continue

        n = process_section(doc, sec, CODE_BLOCKS_DIR)
        status = f"{n} blocks" if n > 0 else "0 blocks"
        print(f"  {sid:20s}  ratio={code_ratio:.3f}  -> {status}")
        if n > 0:
            sections_with_code += 1
            total_blocks += n

    doc.close()
    print(f"\nDone. {sections_with_code} sections with code, {total_blocks} total blocks.")
    print(f"Output: {CODE_BLOCKS_DIR}")


if __name__ == "__main__":
    main()

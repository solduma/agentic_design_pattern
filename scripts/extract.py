#!/usr/bin/env python3
"""
extract.py — T1: Extraction pipeline & manifest.json

Produces:
  assets/manifest.json         — per-section metadata
  assets/images/               — 65 PNGs (img-p{page}-{idx})
  assets/sections/             — per-section raw text + code blocks
  assets/stubs/                — stub MDX for MISSING sections

manifest.json schema notes (W3-H6 contract):
  para_count   = text blocks separated by ≥1 blank line, EXCLUDING code blocks
  token_count  = pure-text tokens (code removed) via tiktoken cl100k_base
  code_ratio   = code tokens ÷ total tokens (all tokens before code removal)
  footnote_count = count of footnote-like paragraphs (^[digit] or superscript patterns)
"""

import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

try:
    import fitz  # pymupdf
except ImportError:
    sys.exit("ERROR: pymupdf not installed. Run: python3 -m pip install pymupdf --break-system-packages")

try:
    import tiktoken
    ENC = tiktoken.get_encoding("cl100k_base")
except ImportError:
    sys.exit("ERROR: tiktoken not installed. Run: python3 -m pip install tiktoken --break-system-packages")


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = REPO_ROOT / "pdf" / "Agentic_Design_Patterns.pdf"
ASSETS_DIR = REPO_ROOT / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
SECTIONS_DIR = ASSETS_DIR / "sections"
STUBS_DIR = ASSETS_DIR / "stubs"
MANIFEST_PATH = ASSETS_DIR / "manifest.json"

for d in [ASSETS_DIR, IMAGES_DIR, SECTIONS_DIR, STUBS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Section definitions — EMPIRICALLY derived from PDF structure inspection
# Each entry: (id, title, start_page, end_page, disposition)
# Pages are 1-indexed, end_page is INCLUSIVE.
# disposition whitelist: only "index" may be omit-with-notice.
# ---------------------------------------------------------------------------
SECTIONS = [
    # Front matter
    ("foreword",        "Foreword",                                    7,   9,   "translate"),
    ("preface",         "Preface",                                    10,  13,  "translate"),
    ("frameworks-intro","Frameworks Introduction",                    14,  22,  "translate"),

    # Part 1 — Chapters 1–7
    ("ch01", "Chapter 1: Prompt Chaining",                           23,  35,  "translate"),
    ("ch02", "Chapter 2: Routing",                                   36,  49,  "translate"),
    ("ch03", "Chapter 3: Parallelization",                           50,  64,  "translate"),
    ("ch04", "Chapter 4: Reflection",                                65,  78,  "translate"),
    ("ch05", "Chapter 5: Tool Use (Function Calling)",               79,  99,  "translate"),
    ("ch06", "Chapter 6: Planning",                                 100, 112,  "translate"),
    ("ch07", "Chapter 7: Multi-Agent Collaboration",                113, 131,  "translate"),

    # Part 2 — Chapters 8–9
    ("ch08", "Chapter 8: Memory Management",                        132, 153,  "translate"),
    ("ch09", "Chapter 9: Learning and Adaptation",                  154, 166,  "translate"),

    # Part 3 — Chapters 10–13
    ("ch10", "Chapter 10: Model Context Protocol",                  167, 182,  "translate"),
    ("ch11", "Chapter 11: Goal Setting and Monitoring",             183, 195,  "translate"),
    ("ch12", "Chapter 12: Exception Handling",                      196, 203,  "translate"),
    ("ch13", "Chapter 13: Human-in-the-Loop",                      204, 212,  "translate"),

    # Part 4 — Chapters 14–21
    ("ch14", "Chapter 14: Knowledge Retrieval (RAG)",               213, 230,  "translate"),
    ("ch15", "Chapter 15: Inter-Agent Communication",               231, 245,  "translate"),
    ("ch16", "Chapter 16: Resource-Aware Optimization",             246, 261,  "translate"),
    ("ch17", "Chapter 17: Reasoning Techniques",                    262, 285,  "translate"),
    ("ch18", "Chapter 18: Guardrails/Safety Patterns",              286, 305,  "translate"),
    ("ch19", "Chapter 19: Evaluation and Monitoring",               306, 324,  "translate"),
    ("ch20", "Chapter 20: Prioritization",                          325, 334,  "translate"),
    ("ch21", "Chapter 21: Exploration and Discovery",               335, 348,  "translate"),

    # Appendices A–E (present in body)
    ("appendix-a", "Appendix A: Advanced Prompting Techniques",     349, 377,  "translate"),
    ("appendix-b", "Appendix B: AI Agentic Interactions",           378, 384,  "translate"),
    ("appendix-c", "Appendix C: Quick Overview of Agentic Frameworks", 385, 392, "translate"),
    ("appendix-d", "Appendix D: Building an Agent with ADK",        393, 398,  "translate"),
    ("appendix-e", "Appendix E: AI Agents on the CLI",              399, 403,  "translate"),

    # Appendix F — MISSING (TOC only, no body)
    ("appendix-f", "Appendix F",                                    None, None, "translate"),

    # Appendix G — present TWICE (p404-409 and p410-415, different MD5)
    # We handle this specially: extract both, diff, adopt union
    ("appendix-g", "Appendix G: Coding Agents",                     404, 415,  "translate"),

    # Back matter
    ("conclusion", "Conclusion",                                    416, 420,  "translate"),
    ("glossary",   "Glossary",                                      421, 436,  "translate"),
    # Index: omit-with-notice (Pagefind replacement — V-9 decision)
    ("index",      "Index of Terms",                                437, 444,  "omit-with-notice"),
    # Gemini reasoning transcript (p445-448): FAQ sub-page — translate (W3-H10)
    ("gemini-transcript", "Gemini Reasoning Transcript (FAQ sub-page)", 445, 448, "translate"),
    # FAQ
    ("faq",        "Frequently Asked Questions",                    477, 482,  "translate"),
]

# Verify omit-with-notice whitelist — only "index" is permitted
OMIT_WITH_NOTICE_WHITELIST = {"index"}
for sec_id, _, _, _, disp in SECTIONS:
    if disp == "omit-with-notice" and sec_id not in OMIT_WITH_NOTICE_WHITELIST:
        raise ValueError(
            f"VALIDATION ERROR: section '{sec_id}' has disposition 'omit-with-notice' "
            f"but is not in the whitelist {OMIT_WITH_NOTICE_WHITELIST}. "
            f"Only 'index' may be omitted. Fix the SECTIONS table."
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def page_text(doc: fitz.Document, page_num: int) -> str:
    """Extract text from a 1-indexed page."""
    return doc[page_num - 1].get_text("text")


def section_raw_text(doc: fitz.Document, start: int, end: int) -> str:
    """Concatenate raw text for pages start..end (1-indexed, inclusive)."""
    parts = []
    for p in range(start, end + 1):
        parts.append(page_text(doc, p))
    return "\n".join(parts)


CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")

# Heuristic code-block detector for plain text (no markdown fences in PDF text)
# We identify blocks that look like code: lines starting with whitespace + typical keywords
INDENT_CODE_LINE = re.compile(
    r"^[ \t]{2,}(?:def |class |import |from |if |for |while |return |print\(|#.*|\"\"\"|\{|\}|//|/\*|\*.*)"
)

def extract_code_blocks(text: str) -> list[str]:
    """
    Extract code-like blocks from raw PDF text.
    Strategy: fenced ``` blocks first; then runs of lines that look like code (indented
    or starting with common code keywords). Returns list of code block strings.
    """
    blocks = []
    # Markdown-style (rare in PDF output but catch it)
    for m in CODE_BLOCK_RE.finditer(text):
        blocks.append(m.group(0))
    if blocks:
        return blocks

    # Heuristic: consecutive indented / code-looking lines
    lines = text.split("\n")
    in_block = False
    current: list[str] = []
    for line in lines:
        is_code_line = (
            INDENT_CODE_LINE.match(line)
            or (len(line) > 0 and line[0] in (" ", "\t") and len(line.strip()) > 0)
        )
        if is_code_line:
            in_block = True
            current.append(line)
        else:
            if in_block and len(current) >= 3:
                blocks.append("\n".join(current))
            current = []
            in_block = False
    if in_block and len(current) >= 3:
        blocks.append("\n".join(current))
    return blocks


def remove_code_blocks(text: str) -> str:
    """Remove code blocks (fenced and heuristic) from text, returning prose only."""
    # Remove fenced code blocks
    text = CODE_BLOCK_RE.sub("", text)
    # Remove inline code
    text = INLINE_CODE_RE.sub("", text)

    # Remove heuristic code blocks (indented runs ≥3 lines)
    lines = text.split("\n")
    result_lines = []
    run_start = None
    run: list[tuple[int, str]] = []

    def flush_run(run, result_lines, run_start):
        if len(run) >= 3:
            pass  # drop code run
        else:
            for _, ln in run:
                result_lines.append(ln)

    for i, line in enumerate(lines):
        is_code_line = (
            INDENT_CODE_LINE.match(line)
            or (len(line) > 0 and line[0] in (" ", "\t") and len(line.strip()) > 0)
        )
        if is_code_line:
            run.append((i, line))
        else:
            flush_run(run, result_lines, run_start)
            run = []
            run_start = None
            result_lines.append(line)
    flush_run(run, result_lines, None)

    return "\n".join(result_lines)


def count_paragraphs(text: str) -> int:
    """
    Count paragraphs = text blocks separated by ≥1 blank line.
    Code blocks are excluded BEFORE counting.
    W3-H6: para_count = text blocks (non-code) separated by ≥1 blank line.
    """
    prose = remove_code_blocks(text)
    # Split on one or more blank lines
    blocks = re.split(r"\n\s*\n+", prose)
    # Count non-empty blocks
    return sum(1 for b in blocks if b.strip())


def count_tokens(text: str) -> tuple[int, int, float]:
    """
    Returns (prose_tokens, total_tokens, code_ratio).
    - prose_tokens: tiktoken cl100k_base on text with code removed
    - total_tokens: tiktoken on full text
    - code_ratio: code_tokens / total_tokens (0 if total=0)
    W3-H6: token_count = prose_tokens, code_ratio = code_tokens/total_tokens
    """
    total_tokens = len(ENC.encode(text)) if text.strip() else 0
    prose_text = remove_code_blocks(text)
    prose_tokens = len(ENC.encode(prose_text)) if prose_text.strip() else 0
    code_tokens = max(0, total_tokens - prose_tokens)
    code_ratio = code_tokens / total_tokens if total_tokens > 0 else 0.0
    return prose_tokens, total_tokens, code_ratio


FOOTNOTE_RE = re.compile(
    r"(?:^|\n)\s*(?:\[\d+\]|\d+\s*[\.\)]\s|\^\d+|†|‡|§)\s*.{5,}",
    re.MULTILINE,
)

def count_footnotes(text: str) -> int:
    """Heuristic footnote detection."""
    return len(FOOTNOTE_RE.findall(text))


def md5_text(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def slugify(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[\s]+", "-", s.strip())
    return s


# ---------------------------------------------------------------------------
# Image extraction
# ---------------------------------------------------------------------------

def extract_images(doc: fitz.Document) -> list[dict]:
    """
    Extract all images to assets/images/ as PNG.
    Returns image registry list.
    """
    registry = []
    global_idx = 0
    seen_xrefs: set[int] = set()

    for page_num in range(1, len(doc) + 1):
        page = doc[page_num - 1]
        images = page.get_images(full=True)
        page_idx = 0
        for img_info in images:
            xref = img_info[0]
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)

            img_id = f"img-p{page_num}-{page_idx}"
            out_path = IMAGES_DIR / f"{img_id}.png"

            try:
                base_image = doc.extract_image(xref)
                img_bytes = base_image["image"]
                img_ext = base_image.get("ext", "png")

                if img_ext.lower() == "png":
                    out_path.write_bytes(img_bytes)
                else:
                    # Convert to PNG via pixmap
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n > 4:  # CMYK etc
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    pix.save(str(out_path))

                # Try to find caption near image on page
                caption = _find_image_caption(page, page_num, page_idx)

                registry.append({
                    "id": img_id,
                    "page": page_num,
                    "page_idx": page_idx,
                    "section_id": None,  # filled in after section assignment
                    "caption": caption,
                    "filename": out_path.name,
                    "width": base_image.get("width", 0),
                    "height": base_image.get("height", 0),
                })
                global_idx += 1
                page_idx += 1
            except Exception as e:
                print(f"  WARNING: could not extract image xref={xref} p{page_num}: {e}")

    return registry


def _find_image_caption(page: fitz.Page, page_num: int, img_idx: int) -> str:
    """Try to find a caption for an image by looking for 'Fig' text near images."""
    text = page.get_text("text")
    # Look for figure caption patterns
    fig_patterns = [
        r"(?:Fig\.?\s*\d+[.:][^\n]{5,80})",
        r"(?:Figure\s*\d+[.:][^\n]{5,80})",
        r"(?:Fig\s+\d+[^\n]{5,80})",
    ]
    for pat in fig_patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(0).strip()
    return ""


# ---------------------------------------------------------------------------
# Cross-reference registry
# ---------------------------------------------------------------------------

def build_xref_registry(sections: list[dict]) -> list[dict]:
    """
    Build cross-reference registry: figure numbers / section titles → anchor slugs.
    """
    registry = []
    # Section title anchors
    for sec in sections:
        slug = slugify(sec["id"])
        registry.append({
            "type": "section",
            "id": sec["id"],
            "title": sec["title"],
            "anchor_slug": slug,
            "page_range": sec.get("page_range"),
        })
    # Figure/table refs from images
    return registry


# ---------------------------------------------------------------------------
# Appendix G duplicate handling
# ---------------------------------------------------------------------------

def handle_appendix_g_duplicate(doc: fitz.Document) -> tuple[str, str, int, dict]:
    """
    Appendix G appears at p404-409 AND p410-420(ish).
    Extract both, compute MD5s, diff, adopt union (later pages as canonical).
    Returns (text_first, text_second, delta_bytes, diff_info).
    """
    # First occurrence: p404-409
    text_first = section_raw_text(doc, 404, 409)
    # Second occurrence: p410-415 (Conclusion starts p416)
    text_second = section_raw_text(doc, 410, 415)

    md5_first = md5_text(text_first)
    md5_second = md5_text(text_second)

    delta_bytes = 0
    diff_lines = []

    if md5_first != md5_second:
        # Compute diff
        import difflib
        lines_first = text_first.splitlines(keepends=True)
        lines_second = text_second.splitlines(keepends=True)
        diff = list(difflib.unified_diff(
            lines_first, lines_second,
            fromfile="appendix-g-p404-409",
            tofile="appendix-g-p410-420",
            lineterm=""
        ))
        diff_text = "".join(diff)
        delta_bytes = len(diff_text.encode("utf-8"))
        diff_lines = diff[:50]  # first 50 diff lines for record

    return text_first, text_second, delta_bytes, {
        "md5_first": md5_first,
        "md5_second": md5_second,
        "diff_lines_sample": diff_lines,
        "adopted": "second" if md5_first != md5_second else "first",
    }


# ---------------------------------------------------------------------------
# Stub MDX generators
# ---------------------------------------------------------------------------

def make_missing_stub(sec_id: str, title: str, note: str = "") -> str:
    """Generate a stub MDX for a MISSING section (e.g., Appendix F)."""
    return f"""---
id: {sec_id}
title: "{title}"
status: MISSING
---

import Admonition from '@theme/Admonition';

# {title}

<Admonition type="caution" title="이 부록은 원본 PDF에서 확인되지 않았습니다">
  이 부록({title})은 원본 PDF의 목차(Table of Contents)에는 등재되어 있으나,
  본문에서 해당 내용이 확인되지 않았습니다. 원본 파일에 본문이 누락된 것으로 판단됩니다.
  {note}
</Admonition>
"""


def make_manual_review_callout(sec_id: str, title: str, delta_bytes: int) -> str:
    """Generate a ⚠️ 수동 검토 필요 callout for DUPLICATE sections with differing MD5."""
    return f"""
:::warning ⚠️ 수동 검토 필요
이 섹션({title})은 원본 PDF에 두 번 수록되어 있으며, 두 복사본 간에
{delta_bytes} 바이트의 차이가 발견되었습니다.
후반부 내용을 정본으로 채택하였으나, 전반부에만 존재하는 내용이 있을 수 있습니다.
번역 전 두 버전을 비교하여 고유 콘텐츠가 누락되지 않도록 확인하십시오.
:::
"""


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def run_extraction():
    print(f"Opening PDF: {PDF_PATH}")
    doc = fitz.open(str(PDF_PATH))
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")

    # --- Extract all images first ---
    print("\nExtracting images...")
    image_registry = extract_images(doc)
    print(f"  Extracted {len(image_registry)} images")

    # --- Handle Appendix G duplicate ---
    print("\nHandling Appendix G duplicate...")
    appg_text_first, appg_text_second, appg_delta, appg_diff_info = handle_appendix_g_duplicate(doc)
    print(f"  Appendix G: md5_first={appg_diff_info['md5_first'][:8]} "
          f"md5_second={appg_diff_info['md5_second'][:8]} "
          f"delta_bytes={appg_delta} adopted={appg_diff_info['adopted']}")

    # --- Process each section ---
    print("\nProcessing sections...")
    manifest_sections = []

    for sec_id, title, start_page, end_page, disposition in SECTIONS:
        print(f"  [{sec_id}] {title[:50]}", end=" ... ")

        # Determine status
        if start_page is None:
            status = "MISSING"
            raw_text = ""
            page_range = [None, None]
        elif sec_id == "appendix-g":
            # Special: duplicate handling
            # First occurrence: p404-409, second occurrence: p410-415
            # Conclusion starts p416 (separate section)
            status = "DUPLICATE"
            # Adopt second occurrence as canonical (later = more likely authoritative)
            if appg_diff_info["adopted"] == "second":
                raw_text = appg_text_second
            else:
                raw_text = appg_text_first
            page_range = [404, 415]
        elif sec_id == "conclusion":
            # Conclusion is at p416-420, immediately after Appendix G second occurrence
            # Let's use conclusion-specific pages
            raw_text = section_raw_text(doc, start_page, end_page)
            page_range = [start_page, end_page]
            status = "ok"
        else:
            raw_text = section_raw_text(doc, start_page, end_page)
            page_range = [start_page, end_page]
            status = "ok"

        # Checksum
        checksum = md5_text(raw_text) if raw_text else ""

        # Counts
        if raw_text:
            para_count = count_paragraphs(raw_text)
            token_count, total_tokens, code_ratio = count_tokens(raw_text)
            footnote_count = count_footnotes(raw_text)
        else:
            para_count = 0
            token_count = 0
            total_tokens = 0
            code_ratio = 0.0
            footnote_count = 0

        # Assign images to this section
        if start_page and end_page:
            for img in image_registry:
                if start_page <= img["page"] <= end_page and img["section_id"] is None:
                    img["section_id"] = sec_id

        # Build record
        record = {
            "id": sec_id,
            "title": title,
            "page_range": page_range,
            "checksum": checksum,
            "para_count": para_count,
            "token_count": token_count,
            "total_tokens": total_tokens,
            "code_ratio": round(code_ratio, 4),
            "footnote_count": footnote_count,
            "status": status,
            "disposition": disposition,
            "anchor_slug": slugify(sec_id),
        }

        # Extra fields for DUPLICATE
        if status == "DUPLICATE" and sec_id == "appendix-g":
            record["duplicate_delta_bytes"] = appg_delta
            record["duplicate_info"] = appg_diff_info
            if appg_delta > 0:
                record["manual_review_required"] = True

        manifest_sections.append(record)

        # Save raw text to assets/sections/
        if raw_text:
            code_blocks = extract_code_blocks(raw_text)
            section_out = SECTIONS_DIR / f"{sec_id}.txt"
            with open(section_out, "w", encoding="utf-8") as f:
                f.write(f"=== SECTION: {title} (pages {page_range[0]}–{page_range[1]}) ===\n\n")
                f.write(raw_text)
                if code_blocks:
                    f.write("\n\n=== CODE BLOCKS EXTRACTED ===\n")
                    for i, cb in enumerate(code_blocks):
                        f.write(f"\n--- Code block {i+1} ---\n")
                        f.write(cb)
                        f.write("\n")

        # Generate stubs for special cases
        if status == "MISSING":
            stub_path = STUBS_DIR / f"{sec_id}.mdx"
            stub_content = make_missing_stub(sec_id, title)
            stub_path.write_text(stub_content, encoding="utf-8")
            print(f"MISSING (stub written)")
        elif status == "DUPLICATE" and appg_delta > 0:
            callout_path = STUBS_DIR / f"{sec_id}-review-callout.mdx"
            callout_path.write_text(
                make_manual_review_callout(sec_id, title, appg_delta),
                encoding="utf-8"
            )
            print(f"DUPLICATE (delta={appg_delta}b, callout written)")
        else:
            print(f"{status} (para={para_count}, tokens={token_count}, code_ratio={code_ratio:.2f})")

    # Validate omit-with-notice whitelist in final manifest
    for rec in manifest_sections:
        if rec["disposition"] == "omit-with-notice" and rec["id"] not in OMIT_WITH_NOTICE_WHITELIST:
            raise ValueError(
                f"MANIFEST VALIDATION ERROR: '{rec['id']}' has omit-with-notice "
                f"but is not whitelisted. Only 'index' is permitted."
            )

    # --- Build cross-reference registry ---
    xref_registry = build_xref_registry(manifest_sections)

    # Assign any unassigned images (e.g., in duplicate zones)
    for img in image_registry:
        if img["section_id"] is None:
            # Assign to nearest section by page
            for rec in manifest_sections:
                pr = rec.get("page_range", [None, None])
                if pr[0] and pr[1] and pr[0] <= img["page"] <= pr[1]:
                    img["section_id"] = rec["id"]
                    break

    # --- Assemble manifest ---
    manifest = {
        "_schema_notes": {
            "para_count": "Text blocks separated by >=1 blank line, EXCLUDING code blocks (W3-H6)",
            "token_count": "Pure-text tokens (code removed) via tiktoken cl100k_base (W3-H6)",
            "total_tokens": "All tokens including code via tiktoken cl100k_base",
            "code_ratio": "code_tokens / total_tokens; code_tokens = total_tokens - token_count",
            "footnote_count": "Heuristic footnote paragraph count (W6 completeness gate)",
            "status": "ok | MISSING | DUPLICATE",
            "disposition": "translate | keep-english | omit-with-notice (only 'index' may be omit-with-notice)",
            "tokenizer": "tiktoken cl100k_base (fixed, W3-H7)",
        },
        "pdf_total_pages": total_pages,
        "empirical_section_count": len(manifest_sections),
        "image_count": len(image_registry),
        "sections": manifest_sections,
        "images": image_registry,
        "xref_registry": xref_registry,
        "appendix_g_duplicate": {
            "first_occurrence_pages": [404, 409],
            "second_occurrence_pages": [410, 415],
            **appg_diff_info,
            "delta_bytes": appg_delta,
        },
    }

    # --- Validate manifest ---
    missing_secs = [s["id"] for s in manifest_sections if s["status"] == "MISSING"]
    duplicate_secs = [s["id"] for s in manifest_sections if s["status"] == "DUPLICATE"]
    print(f"\n=== Manifest Summary ===")
    print(f"  Total sections: {len(manifest_sections)}")
    print(f"  MISSING: {missing_secs}")
    print(f"  DUPLICATE: {duplicate_secs}")
    print(f"  Images: {len(image_registry)}")
    print(f"  omit-with-notice: {[s['id'] for s in manifest_sections if s['disposition']=='omit-with-notice']}")

    if "appendix-f" not in missing_secs:
        print("  ERROR: appendix-f should be MISSING!")

    if len(image_registry) != 65:
        print(f"  WARNING: Expected 65 images, got {len(image_registry)}")

    # --- Write manifest.json ---
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"\nManifest written to: {MANIFEST_PATH}")
    print(f"Images in: {IMAGES_DIR}")
    print(f"Sections in: {SECTIONS_DIR}")
    print(f"Stubs in: {STUBS_DIR}")

    # Final validation
    assert len(image_registry) == 65, f"Expected 65 images, got {len(image_registry)}"
    assert "appendix-f" in missing_secs, "appendix-f must be MISSING"
    assert "appendix-g" in duplicate_secs, "appendix-g must be DUPLICATE"

    # Validate JSON is parseable
    with open(MANIFEST_PATH) as f:
        parsed = json.load(f)
    assert parsed["empirical_section_count"] == len(manifest_sections)
    print(f"\nAll validations passed.")
    print(f"Empirical section count: {len(manifest_sections)}")


if __name__ == "__main__":
    run_extraction()

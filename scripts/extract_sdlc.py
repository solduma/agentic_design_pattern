#!/usr/bin/env python3
"""
extract_sdlc.py — T1: Extraction pipeline & manifest for "The New SDLC With Vibe Coding".

Single 51-page Google whitepaper (Addy Osmani, Shubham Saboo, Sokratis Kartakis, May 2026).
Unlike the 21-chapter ADP book, this is one paper split into top-level sections by heading.

Produces:
  assets/sdlc/manifest.json    — per-section metadata + image/xref registries
  assets/sdlc/sections/        — per-section raw text + code blocks (translator input)
  assets/sdlc/images/          — figure PNGs (decorative crystals excluded)

manifest schema notes (mirrors ADP W3-H6 contract):
  para_count   = text blocks separated by >=1 blank line, EXCLUDING code blocks
  token_count  = pure-text tokens (code removed) via tiktoken cl100k_base
  code_ratio   = code_tokens / total_tokens
"""

import hashlib
import json
import re
import sys
from pathlib import Path

try:
    import fitz  # pymupdf
except ImportError:
    sys.exit("ERROR: pymupdf not installed. Run: python3 -m pip install pymupdf")

try:
    import tiktoken
    ENC = tiktoken.get_encoding("cl100k_base")
except ImportError:
    sys.exit("ERROR: tiktoken not installed. Run: python3 -m pip install tiktoken")


REPO_ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = REPO_ROOT / "pdf" / "ai_sdlc.pdf"
ASSETS_DIR = REPO_ROOT / "assets" / "sdlc"
IMAGES_DIR = ASSETS_DIR / "images"
SECTIONS_DIR = ASSETS_DIR / "sections"
MANIFEST_PATH = ASSETS_DIR / "manifest.json"

for d in [ASSETS_DIR, IMAGES_DIR, SECTIONS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Section definitions — derived from size-24 headings in reading order.
# Each entry: (id, ko_title, start_page, start_marker)
# The section ends where the next section's marker begins.
# start_marker is matched against the concatenated text at/after start_page.
# ---------------------------------------------------------------------------
SECTIONS = [
    ("introduction",        "서론",                             6,  "Introduction"),
    ("syntax-to-intent",    "구문에서 의도로: 에이전트와 바이브 코딩", 10, "The shift from syntax to intent"),
    ("context-engineering", "컨텍스트 엔지니어링: 진짜 핵심 역량",    15, "Context engineering: the real skill"),
    ("new-sdlc",            "새로운 소프트웨어 개발 수명주기",        19, "The new software development life cycle"),
    ("harness-engineering", "하네스 엔지니어링: 모델을 둘러싼 것",     26, "Harness Engineering: What surrounds"),
    ("developer-role",      "진화하는 개발자의 역할: 지휘자와 오케스트레이터", 31, "The developer's evolving role:"),
    ("coding-agents",       "실무에서의 코딩 에이전트",              35, "Coding agents in practice"),
    ("economics",           "AI 개발의 경제학",                   39, "The Economics of AI Development"),
    ("where-to-start",      "어디서부터 시작할 것인가",              43, "Where to start"),
    ("conclusion",          "결론: 새로운 인터페이스로서의 의도",      47, "Conclusion: Intent as the new Interface"),
    ("endnotes",            "미주",                             49, "Endnotes"),
]

# Figure images to keep (page -> figure caption). Decorative crystals are excluded.
# xref sizes confirmed via inspection: figures are the large ~1950px-wide jpx/png objects.
FIGURE_PAGES = {8, 10, 14, 17, 20, 25, 26, 27, 32, 40}
# Decorative image xrefs (cover / corner crystals / tiny icons) — never registered.
DECORATIVE_XREFS = {578, 6, 359, 143}

RUNNING_HEADER = "The new SDLC with vibe coding"


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def clean_page_text(raw: str, page_num: int) -> str:
    """Strip running header, 'May 2026' footer, and bare page-number lines."""
    lines = raw.split("\n")
    out = []
    for ln in lines:
        s = ln.strip()
        if s == RUNNING_HEADER:
            continue
        if s == "May 2026":
            continue
        if s == str(page_num):
            continue
        out.append(ln)
    return "\n".join(out)


CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.MULTILINE)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
INDENT_CODE_LINE = re.compile(
    r"^[ \t]{2,}(?:def |class |import |from |if |for |while |return |print\(|#.*|\"\"\"|\{|\}|//|/\*|\*.*|uvx |> |\$ )"
)


def extract_code_blocks(text: str) -> list[str]:
    blocks = [m.group(0) for m in CODE_BLOCK_RE.finditer(text)]
    if blocks:
        return blocks
    lines = text.split("\n")
    in_block, current = False, []
    for line in lines:
        is_code = INDENT_CODE_LINE.match(line) or (
            len(line) > 0 and line[0] in (" ", "\t") and len(line.strip()) > 0
        )
        if is_code:
            in_block = True
            current.append(line)
        else:
            if in_block and len(current) >= 3:
                blocks.append("\n".join(current))
            current, in_block = [], False
    if in_block and len(current) >= 3:
        blocks.append("\n".join(current))
    return blocks


def remove_code_blocks(text: str) -> str:
    text = CODE_BLOCK_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    lines = text.split("\n")
    result, run = [], []
    for line in lines:
        is_code = INDENT_CODE_LINE.match(line) or (
            len(line) > 0 and line[0] in (" ", "\t") and len(line.strip()) > 0
        )
        if is_code:
            run.append(line)
        else:
            if len(run) < 3:
                result.extend(run)
            run = []
            result.append(line)
    if len(run) < 3:
        result.extend(run)
    return "\n".join(result)


def count_paragraphs(text: str) -> int:
    prose = remove_code_blocks(text)
    blocks = re.split(r"\n\s*\n+", prose)
    return sum(1 for b in blocks if b.strip())


def count_tokens(text: str) -> tuple[int, int, float]:
    total = len(ENC.encode(text)) if text.strip() else 0
    prose = remove_code_blocks(text)
    prose_tokens = len(ENC.encode(prose)) if prose.strip() else 0
    code_tokens = max(0, total - prose_tokens)
    ratio = code_tokens / total if total > 0 else 0.0
    return prose_tokens, total, ratio


def md5_text(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Image extraction (figures only)
# ---------------------------------------------------------------------------

def extract_figures(doc: fitz.Document) -> list[dict]:
    registry = []
    seen = set()
    for page_num in range(1, len(doc) + 1):
        if page_num not in FIGURE_PAGES:
            continue
        page = doc[page_num - 1]
        page_text = page.get_text("text")
        idx = 0
        for info in page.get_images(full=True):
            xref = info[0]
            if xref in DECORATIVE_XREFS or xref in seen:
                continue
            seen.add(xref)
            base = doc.extract_image(xref)
            w, h = base.get("width", 0), base.get("height", 0)
            # Skip anything too small to be a figure (decorative icons).
            if w < 400 or h < 200:
                continue
            img_id = f"fig-p{page_num}-{idx}"
            out_path = IMAGES_DIR / f"{img_id}.png"
            if base.get("ext", "png").lower() == "png":
                out_path.write_bytes(base["image"])
            else:
                pix = fitz.Pixmap(doc, xref)
                if pix.n > 4:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                pix.save(str(out_path))
            caption = find_caption(page_text)
            registry.append({
                "id": img_id,
                "page": page_num,
                "section_id": None,
                "caption_en": caption,
                "filename": out_path.name,
                "width": w,
                "height": h,
            })
            idx += 1
    return registry


def find_caption(text: str) -> str:
    m = re.search(r"(?:Figure|Fig\.?)\s*\d+[.:][^\n]{3,120}", text)
    if m:
        return re.sub(r"\s+", " ", m.group(0)).strip()
    m = re.search(r"Snippet\s*\d+[.:][^\n]{3,120}", text)
    if m:
        return re.sub(r"\s+", " ", m.group(0)).strip()
    return ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run():
    print(f"Opening PDF: {PDF_PATH}")
    doc = fitz.open(str(PDF_PATH))
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")

    # Concatenated cleaned text with page offsets for heading-based slicing.
    page_texts = [clean_page_text(doc[i].get_text("text"), i + 1) for i in range(total_pages)]
    marker = "\nPAGE\n"  # sentinel between pages
    page_start_offset = {}
    buf = []
    pos = 0
    for i, t in enumerate(page_texts):
        page_start_offset[i + 1] = pos
        buf.append(t)
        pos += len(t)
        buf.append(marker)
        pos += len(marker)
    full = "".join(buf)

    # Find each section's start char-offset (first occurrence at/after its start_page).
    starts = []
    for sec_id, ko_title, start_page, mk in SECTIONS:
        search_from = page_start_offset[start_page]
        off = full.find(mk, search_from)
        if off == -1:
            raise ValueError(f"Section marker not found: {sec_id} :: {mk!r}")
        starts.append((sec_id, ko_title, start_page, mk, off))
    # Ensure monotonic increasing offsets (sanity).
    for a, b in zip(starts, starts[1:]):
        if b[4] <= a[4]:
            raise ValueError(f"Non-monotonic section offset: {a[0]} -> {b[0]}")

    figures = extract_figures(doc)
    print(f"Extracted {len(figures)} figure images")

    manifest_sections = []
    xref_registry = []
    for i, (sec_id, ko_title, start_page, mk, off) in enumerate(starts):
        end = starts[i + 1][4] if i + 1 < len(starts) else len(full)
        seg = full[off:end].replace(marker, "\n")
        seg = seg.strip()
        # end_page = last page whose offset <= end
        end_page = start_page
        for pg, o in page_start_offset.items():
            if o < end:
                end_page = max(end_page, pg)
        # assign figures on pages within [start_page, end_page]
        for fig in figures:
            if fig["section_id"] is None and start_page <= fig["page"] <= end_page:
                fig["section_id"] = sec_id

        para = count_paragraphs(seg)
        tok, total_tok, code_ratio = count_tokens(seg)
        rec = {
            "id": sec_id,
            "title_ko": ko_title,
            "title_en": mk,
            "page_range": [start_page, end_page],
            "checksum": md5_text(seg),
            "para_count": para,
            "token_count": tok,
            "total_tokens": total_tok,
            "code_ratio": round(code_ratio, 4),
            "status": "ok",
            "disposition": "translate",
            "anchor_slug": sec_id,
        }
        manifest_sections.append(rec)
        xref_registry.append({"id": sec_id, "anchor_slug": sec_id, "title": ko_title})

        (SECTIONS_DIR / f"{sec_id}.txt").write_text(
            f"=== SECTION: {ko_title} / {mk} (pages {start_page}-{end_page}) ===\n\n{seg}\n",
            encoding="utf-8",
        )
        print(f"  [{sec_id}] p{start_page}-{end_page} para={para} tok={tok} code={code_ratio:.2f}")

    # Any figure not assigned -> nearest by page
    for fig in figures:
        if fig["section_id"] is None:
            for rec in manifest_sections:
                lo, hi = rec["page_range"]
                if lo <= fig["page"] <= hi:
                    fig["section_id"] = rec["id"]
                    break

    manifest = {
        "_schema_notes": {
            "para_count": "Text blocks separated by >=1 blank line, EXCLUDING code blocks",
            "token_count": "Pure-text tokens (code removed) via tiktoken cl100k_base",
            "code_ratio": "code_tokens / total_tokens",
            "tokenizer": "tiktoken cl100k_base",
        },
        "source_pdf": "pdf/ai_sdlc.pdf",
        "title": "The New SDLC With Vibe Coding",
        "authors": ["Addy Osmani", "Shubham Saboo", "Sokratis Kartakis"],
        "publisher": "Google",
        "date": "May 2026",
        "pdf_total_pages": total_pages,
        "section_count": len(manifest_sections),
        "figure_count": len(figures),
        "sections": manifest_sections,
        "figures": figures,
        "xref_registry": xref_registry,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n=== Summary ===")
    print(f"  sections: {len(manifest_sections)}  figures: {len(figures)}")
    print(f"  manifest: {MANIFEST_PATH}")
    assert len(manifest_sections) == len(SECTIONS)
    print("All validations passed.")


if __name__ == "__main__":
    run()

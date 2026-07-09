#!/usr/bin/env python3
"""
integrate_sdlc.py — T8 integration for the SDLC paper docs.

1. Copy figure PNGs to site/static/img/sdlc/
2. Build site/src/sdlc-diagram-map.json (id -> mermaid content or PNG src + caption/alt)
3. Rewrite <Diagram id=.../> tags in site/sdlc-docs/**/*.mdx into <figure> markup.

Mirrors integrate_site.py but scoped to the SDLC docs instance.
"""
import json
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DIAG_INDEX = REPO / "assets" / "sdlc" / "diagrams" / "index.json"
SDLC_DOCS = REPO / "site" / "sdlc-docs"
STATIC_IMG = REPO / "site" / "static" / "img" / "sdlc"
DIAG_MAP_OUT = REPO / "site" / "src" / "sdlc-diagram-map.json"

STATIC_IMG.mkdir(parents=True, exist_ok=True)


def escape_caption(s: str) -> str:
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = s.replace("{", "&#123;").replace("}", "&#125;")
    return s


def build_diagram_map(diagrams):
    diag_map = {}
    mermaid_n = png_n = 0
    for d in diagrams:
        did = d["id"]
        if d["type"] == "mermaid":
            mmd = REPO / d["asset_path"]
            content = mmd.read_text(encoding="utf-8").strip() if mmd.exists() else "flowchart LR\n  A --> B"
            if not mmd.exists():
                print(f"  WARNING: missing mmd {mmd}", file=sys.stderr)
            diag_map[did] = {
                "type": "mermaid",
                "content": content,
                "caption_ko": d.get("caption_ko", ""),
                "alt_ko": d.get("alt_ko", ""),
            }
            mermaid_n += 1
        else:  # png
            src = REPO / d["asset_path"]
            dest = STATIC_IMG / src.name
            if src.exists():
                shutil.copy2(src, dest)
                png_n += 1
            else:
                print(f"  WARNING: missing PNG {src}", file=sys.stderr)
            diag_map[did] = {
                "type": "png",
                "src": f"/img/sdlc/{src.name}",
                "caption_ko": d.get("caption_ko", ""),
                "alt_ko": d.get("alt_ko", ""),
            }
    print(f"  diagram map: {mermaid_n} mermaid, {png_n} png")
    return diag_map


def make_mermaid(info):
    caption = escape_caption(info.get("caption_ko", ""))
    lines = ["<figure>", "", "```mermaid", info["content"], "```", ""]
    if caption:
        lines.append(f"<figcaption>{caption}</figcaption>")
    lines.append("</figure>")
    return "\n".join(lines)


def make_png(info):
    caption = escape_caption(info.get("caption_ko", ""))
    alt = escape_caption(info.get("alt_ko", ""))
    lines = ["<figure>", f'<img src="{info["src"]}" alt="{alt}" />']
    if caption:
        lines.append(f"<figcaption>{caption}</figcaption>")
    lines.append("</figure>")
    return "\n".join(lines)


DIAGRAM_RE = re.compile(r'<Diagram\s+((?:[^>]|\n)*?)/>', re.DOTALL)


def rewrite(content, diag_map):
    count = 0

    def repl(m):
        nonlocal count
        attrs = m.group(1)
        idm = re.search(r'id=["\']([^"\']+)["\']', attrs)
        if not idm:
            return m.group(0)
        did = idm.group(1)
        if did not in diag_map:
            return f'<figure><figcaption>다이어그램 {did} (준비 중)</figcaption></figure>'
        count += 1
        info = diag_map[did]
        return make_mermaid(info) if info["type"] == "mermaid" else make_png(info)

    return DIAGRAM_RE.sub(repl, content), count


def main():
    print("=== T8 SDLC Integration ===")
    diagrams = json.loads(DIAG_INDEX.read_text(encoding="utf-8"))
    diag_map = build_diagram_map(diagrams)
    DIAG_MAP_OUT.write_text(json.dumps(diag_map, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  wrote {DIAG_MAP_OUT}")

    total = 0
    for mdx in sorted(SDLC_DOCS.rglob("*.mdx")):
        content = mdx.read_text(encoding="utf-8")
        new, n = rewrite(content, diag_map)
        if new != content:
            mdx.write_text(new, encoding="utf-8")
            total += n
            print(f"  {mdx.name}: {n} diagrams rewritten")
    print(f"=== done: {total} diagram placeholders rewritten ===")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
integrate_site.py — T8 site integration script.

1. Copy PNG images to site/static/img/diagrams/
2. Generate site/src/diagram-map.json
3. Generate site/src/xref-map.json
4. Rewrite <Diagram .../> and <CrossRef .../> tags in all MDX files
"""
import json
import re
import shutil
import sys
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent
ASSETS = WORKSPACE / "assets"
SITE = WORKSPACE / "site"
DOCS = SITE / "docs"
DIAGRAMS_JSON = ASSETS / "diagrams" / "index.json"
MANIFEST_JSON = ASSETS / "manifest.json"
STATIC_DIAGRAMS = SITE / "static" / "img" / "diagrams"
SRC = SITE / "src"

STATIC_DIAGRAMS.mkdir(parents=True, exist_ok=True)


def load_diagram_index():
    with open(DIAGRAMS_JSON, encoding="utf-8") as f:
        return json.load(f)


def load_manifest():
    with open(MANIFEST_JSON, encoding="utf-8") as f:
        return json.load(f)


def build_diagram_map(diagrams):
    """Build diagram map and copy PNG files."""
    diag_map = {}
    mermaid_count = 0
    png_count = 0

    for d in diagrams:
        did = d["id"]
        if d["type"] == "mermaid":
            mmd_path = WORKSPACE / d["asset_path"]
            if mmd_path.exists():
                content = mmd_path.read_text(encoding="utf-8").strip()
            else:
                print(f"  WARNING: missing mmd file: {mmd_path}", file=sys.stderr)
                content = "graph LR\n  A --> B"
            diag_map[did] = {
                "type": "mermaid",
                "content": content,
                "caption_ko": d.get("caption_ko", ""),
                "alt_ko": d.get("alt_ko", ""),
            }
            mermaid_count += 1
        elif d["type"] == "png":
            src_path = WORKSPACE / d["asset_path"]
            filename = src_path.name
            dest_path = STATIC_DIAGRAMS / filename
            if src_path.exists():
                shutil.copy2(src_path, dest_path)
                png_count += 1
            else:
                print(f"  WARNING: missing PNG: {src_path}", file=sys.stderr)
            diag_map[did] = {
                "type": "png",
                "src": f"/img/diagrams/{filename}",
                "caption_ko": d.get("caption_ko", ""),
                "alt_ko": d.get("alt_ko", ""),
            }

    print(f"  Diagram map: {mermaid_count} mermaid, {png_count} PNG")
    return diag_map, mermaid_count, png_count


def build_xref_map(manifest):
    """Build xref map from manifest xref_registry."""
    xref_registry = manifest.get("xref_registry", [])
    xref_map = {}
    for entry in xref_registry:
        xid = entry["id"]
        xref_map[xid] = {
            "anchor_slug": entry.get("anchor_slug", xid),
            "title": entry.get("title", xid),
        }
    print(f"  XRef map: {len(xref_map)} entries")
    return xref_map


def escape_caption(s):
    """Escape characters that could break MDX."""
    # Replace < and > with HTML entities to avoid MDX issues
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    s = s.replace("{", "&#123;")
    s = s.replace("}", "&#125;")
    return s


def make_mermaid_replacement(diag_info, caption_override=None, alt_override=None):
    """Generate MDX for a mermaid diagram."""
    content = diag_info["content"]
    caption = caption_override or diag_info.get("caption_ko", "")
    alt = alt_override or diag_info.get("alt_ko", "")

    caption_esc = escape_caption(caption)

    lines = ["<figure>", "", "```mermaid"]
    lines.append(content)
    lines.append("```")
    lines.append("")
    if caption_esc:
        lines.append(f"<figcaption>{caption_esc}</figcaption>")
    lines.append("</figure>")
    return "\n".join(lines)


def make_png_replacement(diag_info, caption_override=None, alt_override=None):
    """Generate MDX for a PNG diagram."""
    src = diag_info["src"]
    caption = caption_override or diag_info.get("caption_ko", "")
    alt = alt_override or diag_info.get("alt_ko", "")

    caption_esc = escape_caption(caption)
    alt_esc = escape_caption(alt)

    lines = ["<figure>"]
    lines.append(f'<img src="{src}" alt="{alt_esc}" />')
    if caption_esc:
        lines.append(f"<figcaption>{caption_esc}</figcaption>")
    lines.append("</figure>")
    return "\n".join(lines)


def rewrite_diagrams(content, diag_map):
    """Rewrite <Diagram .../> tags in MDX content."""
    # Match multi-line Diagram tags
    pattern = re.compile(
        r'<Diagram\s+((?:[^>]|\n)*?)/>', re.DOTALL
    )
    count = 0

    def replace_diagram(m):
        nonlocal count
        attrs_str = m.group(1)
        # Extract id
        id_match = re.search(r'id=["\']([^"\']+)["\']', attrs_str)
        if not id_match:
            return m.group(0)  # keep as-is
        did = id_match.group(1)

        # Extract optional caption and alt overrides
        cap_match = re.search(r'caption=["\']([^"\']+)["\']', attrs_str)
        alt_match = re.search(r'alt=["\']([^"\']+)["\']', attrs_str)
        caption_override = cap_match.group(1) if cap_match else None
        alt_override = alt_match.group(1) if alt_match else None

        if did not in diag_map:
            # Unknown ID — render a placeholder
            return f'<figure><figcaption>다이어그램 {did} (준비 중)</figcaption></figure>'

        diag_info = diag_map[did]
        count += 1
        if diag_info["type"] == "mermaid":
            return make_mermaid_replacement(diag_info, caption_override, alt_override)
        else:
            return make_png_replacement(diag_info, caption_override, alt_override)

    new_content = pattern.sub(replace_diagram, content)
    return new_content, count


def rewrite_crossrefs(content, xref_map):
    """Rewrite <CrossRef .../> tags in MDX content."""
    pattern = re.compile(
        r'<CrossRef\s+((?:[^>]|\n)*?)/>', re.DOTALL
    )
    count = 0

    def replace_crossref(m):
        nonlocal count
        attrs_str = m.group(1)
        id_match = re.search(r'id=["\']([^"\']+)["\']', attrs_str)
        if not id_match:
            return m.group(0)

        xid = id_match.group(1)
        # label override
        label_match = re.search(r'label=["\']([^"\']+)["\']', attrs_str)

        if xid not in xref_map:
            label = label_match.group(1) if label_match else xid
            return f'<span>{label}</span>'

        info = xref_map[xid]
        anchor = info["anchor_slug"]
        title = info["title"]
        label = label_match.group(1) if label_match else title

        count += 1
        return f'<a href="#{anchor}">{label}</a>'

    new_content = pattern.sub(replace_crossref, content)
    return new_content, count


def process_mdx_files(diag_map, xref_map):
    """Rewrite all MDX files in site/docs/."""
    mdx_files = list(DOCS.rglob("*.mdx"))
    total_diag = 0
    total_xref = 0

    for mdx_path in sorted(mdx_files):
        content = mdx_path.read_text(encoding="utf-8")
        orig = content

        content, d_count = rewrite_diagrams(content, diag_map)
        content, x_count = rewrite_crossrefs(content, xref_map)

        if content != orig:
            mdx_path.write_text(content, encoding="utf-8")
            total_diag += d_count
            total_xref += x_count
            rel = mdx_path.relative_to(SITE)
            print(f"  Rewrote {rel}: {d_count} diagrams, {x_count} crossrefs")

    print(f"  Total: {total_diag} diagrams, {total_xref} crossrefs rewritten")
    return total_diag, total_xref


def main():
    print("=== T8 Site Integration ===")

    # 1. Load data
    diagrams = load_diagram_index()
    manifest = load_manifest()

    # 2. Build diagram map + copy PNGs
    print("\n[1] Building diagram map and copying PNGs...")
    diag_map, mermaid_count, png_count = build_diagram_map(diagrams)

    # 3. Write diagram-map.json
    print("\n[2] Writing diagram-map.json...")
    diag_map_path = SRC / "diagram-map.json"
    with open(diag_map_path, "w", encoding="utf-8") as f:
        json.dump(diag_map, f, ensure_ascii=False, indent=2)
    print(f"  Written: {diag_map_path}")

    # 4. Build xref map
    print("\n[3] Building xref map...")
    xref_map = build_xref_map(manifest)

    # Write xref-map.json
    xref_map_path = SRC / "xref-map.json"
    with open(xref_map_path, "w", encoding="utf-8") as f:
        json.dump(xref_map, f, ensure_ascii=False, indent=2)
    print(f"  Written: {xref_map_path}")

    # 5. Rewrite MDX files
    print("\n[4] Rewriting MDX files...")
    process_mdx_files(diag_map, xref_map)

    print(f"\n=== Done: {mermaid_count} mermaid + {png_count} PNG diagrams mapped ===")


if __name__ == "__main__":
    main()

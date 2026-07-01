#!/usr/bin/env python3
"""
gen_glossary.py — Pre-build script for generating the Glossary MDX page.

Reads terms.json and emits:
  - docs/glossary.mdx   (Korean Docusaurus page)

Usage:
    python3 scripts/gen_glossary.py

Options:
    --check   Run independent parser check only (no file write)
    --output  Override output path (default: docs/glossary.mdx)
"""
import argparse
import json
import re
import sys
from pathlib import Path

WORKTREE = Path(__file__).parent.parent
TERMS_JSON = WORKTREE / "terms.json"
DEFAULT_OUTPUT = WORKTREE / "docs" / "glossary.mdx"


def load_terms(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_terms(terms: list[dict]) -> list[str]:
    """Independent parser check: validate schema and consistency."""
    errors = []
    required_fields = {"en", "ko", "first_chapter", "aliases", "definition_ko", "definition_en"}
    seen_en = {}

    for i, t in enumerate(terms):
        missing = required_fields - set(t.keys())
        if missing:
            errors.append(f"Term[{i}] '{t.get('en', '?')}': missing fields {missing}")

        en = t.get("en", "")
        if not en:
            errors.append(f"Term[{i}]: empty 'en' field")
        en_lower = en.lower()
        if en_lower in seen_en:
            errors.append(f"Duplicate 'en': '{en}' (index {i} vs {seen_en[en_lower]})")
        seen_en[en_lower] = i

        if not isinstance(t.get("aliases", []), list):
            errors.append(f"Term[{i}] '{en}': 'aliases' must be a list")

        # If sha1 present, verify it matches definition_ko
        sha1 = t.get("definition_ko_sha1")
        if sha1:
            import hashlib
            expected = hashlib.sha1(t.get("definition_ko", "").encode("utf-8")).hexdigest()
            if sha1 != expected:
                errors.append(
                    f"Term[{i}] '{en}': definition_ko_sha1 mismatch "
                    f"(stored={sha1[:8]}… expected={expected[:8]}…)"
                )

    return errors


def escape_mdx(text: str) -> str:
    """Escape characters that would break MDX parsing."""
    # Escape < > { } in text content
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace("{", "&#123;")
    text = text.replace("}", "&#125;")
    return text


def generate_mdx(terms: list[dict]) -> str:
    """Generate Korean Glossary MDX content from terms list."""

    # Sort alphabetically by English term for consistent output
    sorted_terms = sorted(terms, key=lambda t: t["en"].lower())

    # Group by first letter for navigation
    groups: dict[str, list[dict]] = {}
    for t in sorted_terms:
        first = t["en"][0].upper() if t["en"] else "#"
        if not first.isalpha():
            first = "#"
        groups.setdefault(first, []).append(t)

    lines = [
        "---",
        "id: glossary",
        "title: 용어집",
        "sidebar_label: 용어집",
        "sidebar_position: 999",
        "description: Agentic Design Patterns 한국어 번역에 사용된 핵심 기술 용어 정의 모음.",
        "---",
        "",
        "# 용어집 (Glossary)",
        "",
        "> 이 페이지는 **[terms.json](https://github.com/solduma/agentic_design_pattern/blob/main/terms.json)**에서 자동 생성됩니다.",
        "> 용어 추가/수정은 terms.json 을 수정한 뒤 PR을 열어 주세요 (docs/HOTFIX.md 참고).",
        "",
        "## 빠른 탐색",
        "",
    ]

    # Quick navigation links
    nav_links = " · ".join(f"[{letter}](#{letter.lower()})" for letter in sorted(groups.keys()))
    lines.append(nav_links)
    lines.append("")

    # Term entries by letter group
    for letter in sorted(groups.keys()):
        lines.append(f"## {letter} {{#{letter.lower()}}}")
        lines.append("")

        for t in groups[letter]:
            en = escape_mdx(t["en"])
            ko = escape_mdx(t.get("ko", ""))
            definition_ko = escape_mdx(t.get("definition_ko", ""))
            definition_en = escape_mdx(t.get("definition_en", ""))
            aliases = t.get("aliases", [])
            first_chapter = escape_mdx(t.get("first_chapter", ""))

            # Term heading: English (Korean)
            if ko:
                lines.append(f"### {en} ({ko})")
            else:
                lines.append(f"### {en}")
            lines.append("")

            # Korean definition (primary)
            if definition_ko:
                lines.append(definition_ko)
                lines.append("")
            elif definition_en:
                # Fallback: note that Korean definition is pending
                lines.append(f"*한국어 정의 준비 중. 영문 참고:* {definition_en}")
                lines.append("")
            else:
                lines.append("*정의 준비 중입니다.*")
                lines.append("")

            # Metadata row
            meta_parts = []
            if first_chapter and first_chapter != "auto-mined":
                meta_parts.append(f"**첫 등장:** {first_chapter}")
            if aliases:
                alias_str = ", ".join(escape_mdx(a) for a in aliases if a and a != t.get("ko"))
                if alias_str:
                    meta_parts.append(f"**별칭:** {alias_str}")

            if meta_parts:
                lines.append(" · ".join(meta_parts))
                lines.append("")

            lines.append("---")
            lines.append("")

    lines.append("")
    lines.append("*이 페이지는 `scripts/gen_glossary.py`로 자동 생성됩니다.*")
    lines.append(f"*총 {len(terms)}개 용어 수록.*")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate Glossary MDX from terms.json")
    parser.add_argument("--check", action="store_true", help="Validate only, no file write")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="Output path for glossary.mdx")
    parser.add_argument("--terms", type=Path, default=TERMS_JSON,
                        help="Path to terms.json")
    args = parser.parse_args()

    # Load and validate
    print(f"Loading terms from {args.terms}")
    terms = load_terms(args.terms)
    print(f"Loaded {len(terms)} terms")

    errors = validate_terms(terms)
    if errors:
        print(f"\nValidation FAILED ({len(errors)} errors):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    else:
        print("Validation PASSED: schema OK, no duplicates, SHA1 hashes verified")

    if args.check:
        print("--check mode: skipping file write")
        return

    # Generate MDX
    mdx_content = generate_mdx(terms)

    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Write output
    args.output.write_text(mdx_content, encoding="utf-8")
    print(f"Written glossary to {args.output}")
    print(f"  Lines: {mdx_content.count(chr(10))}")
    print(f"  Size: {len(mdx_content):,} bytes")


if __name__ == "__main__":
    main()

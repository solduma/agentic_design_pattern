#!/usr/bin/env python3
"""
check_coverage.py
Check manifest section IDs vs. generated MDX files (1:1).
- MISSING sections: need stub + notice text.
- Exclude sections with disposition in {omit-with-notice, auto-generate}.
Exit 1 on any mismatch.
"""
import sys
import os
import json
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
MANIFEST_PATH = os.path.join(REPO_ROOT, "assets", "manifest.json")

EXCLUDE_DISPOSITIONS = {"omit-with-notice", "auto-generate"}

# Default MDX output directory (T5 output lives here)
MDX_GLOB_PATTERN = os.path.join(REPO_ROOT, "src", "content", "**", "*.mdx")
MDX_ALT_PATTERN = os.path.join(REPO_ROOT, "src", "**", "*.mdx")


def find_generated_mdx_files() -> dict[str, str]:
    """Return {section_id: path} by scanning MDX output directories."""
    found = {}
    for pattern in [MDX_GLOB_PATTERN, MDX_ALT_PATTERN]:
        for path in glob.glob(pattern, recursive=True):
            stem = os.path.splitext(os.path.basename(path))[0]
            found[stem] = path
    return found


def load_manifest() -> list[dict]:
    if not os.path.isfile(MANIFEST_PATH):
        print(f"ERROR: manifest not found: {MANIFEST_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(MANIFEST_PATH) as f:
        data = json.load(f)
    return data.get("sections", [])


def check_coverage(mdx_dir: str | None = None) -> int:
    sections = load_manifest()

    # Filter: exclude omit-with-notice and auto-generate dispositions
    expected = {
        s["id"]: s
        for s in sections
        if s.get("disposition", "translate") not in EXCLUDE_DISPOSITIONS
    }

    if mdx_dir:
        found = {
            os.path.splitext(f)[0]: os.path.join(mdx_dir, f)
            for f in os.listdir(mdx_dir)
            if f.endswith(".mdx")
        }
    else:
        found = find_generated_mdx_files()

    missing = set(expected.keys()) - set(found.keys())
    extra = set(found.keys()) - set(expected.keys())

    errors = []

    if missing:
        for sid in sorted(missing):
            sec = expected[sid]
            if sec.get("status") == "MISSING":
                errors.append(
                    f"  MISSING stub needed: {sid} — add stub MDX with notice text"
                )
            else:
                errors.append(f"  MISSING MDX: {sid}")

    if extra:
        for sid in sorted(extra):
            errors.append(f"  EXTRA (not in manifest): {sid}")

    if errors:
        print(f"[check_coverage] FAIL: {len(errors)} issue(s):", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    print(f"[check_coverage] PASS: {len(expected)} sections, all have MDX files.")
    return 0


def self_test():
    import tempfile

    sections = load_manifest()
    expected_ids = {
        s["id"]
        for s in sections
        if s.get("disposition", "translate") not in EXCLUDE_DISPOSITIONS
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create MDX files for all expected sections
        for sid in expected_ids:
            with open(os.path.join(tmpdir, f"{sid}.mdx"), "w") as f:
                f.write(f"# {sid}\n")

        rc_good = check_coverage(tmpdir)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Only create half the files → should fail
        half = list(expected_ids)[: len(expected_ids) // 2]
        for sid in half:
            with open(os.path.join(tmpdir, f"{sid}.mdx"), "w") as f:
                f.write(f"# {sid}\n")

        rc_bad = check_coverage(tmpdir)

    ok = rc_good == 0 and rc_bad != 0
    print(f"[check_coverage] self-test {'PASS' if ok else 'FAIL'} "
          f"(full={rc_good}, partial={rc_bad})")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    mdx_dir_arg = sys.argv[1] if len(sys.argv) == 2 else None
    sys.exit(check_coverage(mdx_dir_arg))

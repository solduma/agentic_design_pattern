#!/usr/bin/env python3
"""
check_t5_coverage.py
T5 aggregation variant of check_coverage.py.
Same exclusions: disposition in {omit-with-notice, auto-generate}.
Looks in the T5 output directory (src/docs/ or docs/ by default).
Exit 1 on mismatch.
"""
import sys
import os
import json
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
MANIFEST_PATH = os.path.join(REPO_ROOT, "assets", "manifest.json")

EXCLUDE_DISPOSITIONS = {"omit-with-notice", "auto-generate"}

# T5 output directories (candidates)
T5_DIRS = [
    os.path.join(REPO_ROOT, "docs"),
    os.path.join(REPO_ROOT, "src", "docs"),
    os.path.join(REPO_ROOT, "site", "docs"),
]


def find_t5_mdx_files(t5_dir: str | None = None) -> dict[str, str]:
    """Return {section_id: path} from T5 output directory."""
    found = {}
    search_dirs = [t5_dir] if t5_dir else T5_DIRS
    for d in search_dirs:
        if os.path.isdir(d):
            for path in glob.glob(os.path.join(d, "**", "*.mdx"), recursive=True):
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


def check_t5_coverage(t5_dir: str | None = None) -> int:
    sections = load_manifest()

    expected = {
        s["id"]: s
        for s in sections
        if s.get("disposition", "translate") not in EXCLUDE_DISPOSITIONS
    }

    found = find_t5_mdx_files(t5_dir)

    missing = set(expected.keys()) - set(found.keys())
    extra = set(found.keys()) - set(expected.keys())

    errors = []
    if missing:
        for sid in sorted(missing):
            errors.append(f"  T5 MISSING: {sid}")
    if extra:
        for sid in sorted(extra):
            errors.append(f"  T5 EXTRA (not in manifest): {sid}")

    if errors:
        print(f"[check_t5_coverage] FAIL: {len(errors)} issue(s):", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    print(f"[check_t5_coverage] PASS: {len(expected)} sections, T5 aggregation complete.")
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
        for sid in expected_ids:
            with open(os.path.join(tmpdir, f"{sid}.mdx"), "w") as f:
                f.write(f"# {sid}\n")
        rc_good = check_t5_coverage(tmpdir)

    with tempfile.TemporaryDirectory() as tmpdir:
        half = list(expected_ids)[: len(expected_ids) // 2]
        for sid in half:
            with open(os.path.join(tmpdir, f"{sid}.mdx"), "w") as f:
                f.write(f"# {sid}\n")
        rc_bad = check_t5_coverage(tmpdir)

    ok = rc_good == 0 and rc_bad != 0
    print(f"[check_t5_coverage] self-test {'PASS' if ok else 'FAIL'} "
          f"(full={rc_good}, partial={rc_bad})")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    t5_dir_arg = sys.argv[1] if len(sys.argv) == 2 else None
    sys.exit(check_t5_coverage(t5_dir_arg))

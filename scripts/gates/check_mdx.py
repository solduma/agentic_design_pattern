#!/usr/bin/env python3
"""
check_mdx.py <file.mdx>
Compile a single MDX file using @mdx-js/mdx via a Node.js helper.
Exit 0 on success, non-zero on failure.
"""
import sys
import subprocess
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HELPER = os.path.join(SCRIPT_DIR, "mdx_compile_helper.mjs")


def check_mdx(mdx_file: str) -> int:
    if not os.path.isfile(mdx_file):
        print(f"ERROR: file not found: {mdx_file}", file=sys.stderr)
        return 1

    node_modules = os.path.join(SCRIPT_DIR, "node_modules")
    if not os.path.isdir(node_modules):
        print(
            f"ERROR: node_modules not found at {node_modules}. Run `npm install` in scripts/gates/",
            file=sys.stderr,
        )
        return 1

    result = subprocess.run(
        ["node", HELPER, mdx_file],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    return 0


def self_test():
    testdata = os.path.join(SCRIPT_DIR, "testdata")
    good = os.path.join(testdata, "good.mdx")
    bad = os.path.join(testdata, "bad.mdx")

    rc_good = check_mdx(good)
    rc_bad = check_mdx(bad)

    ok = rc_good == 0 and rc_bad != 0
    print(f"[check_mdx] self-test {'PASS' if ok else 'FAIL'} "
          f"(good={rc_good}, bad={rc_bad})")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(self_test())
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.mdx>", file=sys.stderr)
        sys.exit(1)
    sys.exit(check_mdx(sys.argv[1]))

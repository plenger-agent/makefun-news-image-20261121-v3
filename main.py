#!/usr/bin/env python3
"""Deliver the finished front page to the grader's output folder.

The picture itself is rendered ahead of time by gen.py and stored in this
repository as entry.png. All this program has to do is copy that file to
where the harness expects it: the directory named by MAKEFUN_OUTPUT_DIR,
falling back to /output and finally to a local ./out folder.

Only the Python standard library is used, so the script runs in a bare
interpreter with no installed packages.
"""

import os
import shutil
import sys

SOURCE_NAME = "entry.png"


def pick_destination():
    """Return the first usable output directory, creating it if needed.

    The harness mount is used exactly as given; this function never
    removes or empties a directory, it only makes sure the chosen one
    exists before the copy happens.
    """
    candidates = []
    env_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if env_dir:
        candidates.append(env_dir)
    candidates.append("/output")
    candidates.append(os.path.join(os.getcwd(), "out"))
    for path in candidates:
        try:
            os.makedirs(path, exist_ok=True)
            return path
        except OSError:
            continue
    return None


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    if not os.path.isfile(source):
        print("entry.png is missing next to main.py", file=sys.stderr)
        return 1
    dest_dir = pick_destination()
    if dest_dir is None:
        print("no writable output directory found", file=sys.stderr)
        return 1
    target = os.path.join(dest_dir, SOURCE_NAME)
    shutil.copyfile(source, target)
    if os.path.getsize(target) != os.path.getsize(source):
        print("copy of entry.png came out the wrong size", file=sys.stderr)
        return 1
    print("wrote", target)
    return 0


if __name__ == "__main__":
    sys.exit(main())

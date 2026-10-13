"""Store a Gemini key locally without putting it in command history."""

import getpass
import os
from pathlib import Path
import sys

KEY_FILE = Path(__file__).resolve().parent / ".gemini-key"


def main():
    if not sys.stdin.isatty():
        print("Run this command directly in your Terminal for hidden key entry.")
        return 1
    if KEY_FILE.exists():
        answer = input("A local key already exists. Replace it? [y/N] ")
        if answer.strip().lower() != "y":
            print("Existing key kept.")
            return 0
    key = getpass.getpass("Paste your Gemini API key (hidden), then press Enter: ").strip()
    if not key or any(c.isspace() for c in key):
        print("No key saved: the key must be nonempty and contain no whitespace.")
        return 1
    # Open without following symbolic links; restrict reads to the owner.
    fd = os.open(KEY_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as handle:
        os.fchmod(handle.fileno(), 0o600)
        handle.write(key + "\n")
    print("Key saved in .gemini-key, which Git ignores. Its contents were not displayed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

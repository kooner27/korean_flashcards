#!/usr/bin/env python3
"""
Convert each Quizlet-exported TAB file (saved with .csv) *in place*
into a standards-compliant two-column CSV.

• Tabs → single comma between Term and Definition
• Any commas inside a field → field is wrapped in "…" and internal quotes doubled
• Works safely: writes to a temp file, then atomically replaces the original
"""

import os
import sys
import tempfile

def quote_field(text: str) -> str:
    """Return RFC-4180-safe CSV field."""
    text = text.strip()
    # Strip existing wrapper quotes, if the whole field was already quoted
    if len(text) >= 2 and text[0] == text[-1] == '"':
        text = text[1:-1]
    # Escape interior double-quotes by doubling them
    text = text.replace('"', '""')
    return f'"{text}"'

def convert_folder(folder: str) -> None:
    if not os.path.isdir(folder):
        print(f'✖ "{folder}" is not a directory')
        return

    for fname in os.listdir(folder):
        if not fname.lower().endswith(".csv"):
            continue

        src = os.path.join(folder, fname)
        fd, tmp = tempfile.mkstemp(dir=folder, suffix=".tmp")
        os.close(fd)

        try:
            with open(src, "r", encoding="utf-8", newline="") as r, \
                 open(tmp, "w", encoding="utf-8", newline="") as w:

                for raw in r:
                    raw = raw.rstrip("\n\r")
                    if not raw:
                        continue                    # skip blank lines

                    parts = raw.split("\t")          # 1 tab = our split
                    if len(parts) < 2:
                        # malformed – ignore
                        continue

                    term_raw       = parts[0]
                    definition_raw = "\t".join(parts[1:])  # re-join stray tabs

                    w.write(
                        f"{quote_field(term_raw)},{quote_field(definition_raw)}\n"
                    )

            os.replace(tmp, src)   # atomic
            print(f"✔ Overwrote {fname}")
        except Exception as e:
            if os.path.exists(tmp):
                os.remove(tmp)
            print(f"✖ Failed {fname}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 fix_quizlet_csv.py /path/to/folder")
        sys.exit(1)
    convert_folder(sys.argv[1])

#!/usr/bin/env python3
"""
Convert Quizlet-exported TAB-separated files (.csv) to standards-compliant two-column CSV.

Supports:
• Single file or directory of files
• Tabs → single comma between Term and Definition
• Internal commas/quotes → fields wrapped in quotes and quotes doubled
• Safe overwrite using a temp file
"""

import os
import sys
import tempfile

def quote_field(text: str) -> str:
    text = text.strip()
    # if already quoted, strip outer quotes first
    if len(text) >= 2 and text[0] == text[-1] == '"':
        text = text[1:-1]
    text = text.replace('"', '""')
    return f'"{text}"'

def convert_file(path: str) -> None:
    filename = os.path.basename(path)

    if not path.lower().endswith(".csv"):
        print(f"✖ Skipping non‑CSV file: {filename}")
        return

    folder = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=folder, suffix=".tmp")
    os.close(fd)

    try:
        with open(path, "r", encoding="utf-8", newline="") as r, \
             open(tmp,  "w", encoding="utf-8", newline="") as w:
            lines_written = 0
            for raw in r:
                raw = raw.rstrip("\r\n")
                if not raw:
                    continue
                parts = raw.split("\t")
                if len(parts) < 2:
                    continue
                term = parts[0]
                definition = "\t".join(parts[1:])
                w.write(f"{quote_field(term)},{quote_field(definition)}\n")
                lines_written += 1

        if lines_written == 0:
            # nothing to convert
            os.remove(tmp)
            print(f"⚠ No valid records in {filename}, left unchanged")
        else:
            os.replace(tmp, path)
            print(f"✔ Overwrote {filename} ({lines_written} line{'s' if lines_written!=1 else ''})")

    except Exception as e:
        if os.path.exists(tmp):
            os.remove(tmp)
        print(f"✖ Failed {filename}: {e}")

def convert_folder(folder: str) -> None:
    if not os.path.isdir(folder):
        print(f'✖ "{folder}" is not a directory')
        return

    csvs = [f for f in os.listdir(folder) if f.lower().endswith(".csv")]
    if not csvs:
        print(f"⚠ No .csv files found in directory: {folder}")
        return

    print(f"→ Scanning {len(csvs)} file{'s' if len(csvs)!=1 else ''} in directory: {folder}")
    for fname in csvs:
        convert_file(os.path.join(folder, fname))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 fix_quizlet_csv.py /path/to/file_or_folder")
        sys.exit(1)

    target = sys.argv[1]
    if os.path.isfile(target):
        convert_file(target)
    elif os.path.isdir(target):
        convert_folder(target)
    else:
        print(f'✖ "{target}" is not a valid file or directory')

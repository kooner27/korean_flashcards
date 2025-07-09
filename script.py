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
    if len(text) >= 2 and text[0] == text[-1] == '"':
        text = text[1:-1]
    text = text.replace('"', '""')
    return f'"{text}"'

def convert_file(path: str) -> None:
    if not path.lower().endswith(".csv"):
        print(f"✖ Skipping non-csv file: {path}")
        return

    folder = os.path.dirname(path)
    filename = os.path.basename(path)
    fd, tmp = tempfile.mkstemp(dir=folder, suffix=".tmp")
    os.close(fd)

    try:
        with open(path, "r", encoding="utf-8", newline="") as r, \
             open(tmp, "w", encoding="utf-8", newline="") as w:
            for raw in r:
                raw = raw.rstrip("\n\r")
                if not raw:
                    continue
                parts = raw.split("\t")
                if len(parts) < 2:
                    continue
                term = parts[0]
                definition = "\t".join(parts[1:])
                w.write(f"{quote_field(term)},{quote_field(definition)}\n")

        os.replace(tmp, path)
        print(f"✔ Overwrote {filename}")
    except Exception as e:
        if os.path.exists(tmp):
            os.remove(tmp)
        print(f"✖ Failed {filename}: {e}")

def convert_folder(folder: str) -> None:
    if not os.path.isdir(folder):
        print(f'✖ "{folder}" is not a directory')
        return

    for fname in os.listdir(folder):
        if fname.lower().endswith(".csv"):
            convert_file(os.path.join(folder, fname))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 fix_quizlet_csv.py /path/to/file_or_folder")
        sys.exit(1)

    path = sys.argv[1]
    if os.path.isfile(path):
        convert_file(path)
    elif os.path.isdir(path):
        convert_folder(path)
    else:
        print(f'✖ "{path}" is not a valid file or directory')

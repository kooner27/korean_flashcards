#!/usr/bin/env python3
"""
txt2csv_flashcards.py

Convert all .txt files in a folder into CSV files for flashcards.
- Each non-empty line is one card.
- The first '=' on the line splits TERM (=) DEFINITION.
- Fields are always quoted so commas are safe.
- Output is one CSV per input by default (same basename).
- Optionally combine all .txt files into a single CSV.

Usage:
  python txt2csv_flashcards.py /path/to/folder
  python txt2csv_flashcards.py /path/to/folder --combined flashcards.csv
  python txt2csv_flashcards.py /path/to/folder -o /path/to/outdir
"""

from __future__ import annotations
import argparse
import csv
from pathlib import Path

def parse_line(line: str) -> tuple[str, str] | None:
    """Split at the first '='; return (term, definition) or None if invalid/blank."""
    s = line.strip()
    if not s:
        return None
    # Split on first '=' only
    parts = s.split("=", 1)
    if len(parts) != 2:
        return None
    term, definition = parts[0].strip(), parts[1].strip()
    return term, definition

def read_text(path: Path) -> list[tuple[str, str]]:
    """Read a .txt file (UTF-8/UTF-8-BOM; fallback cp949) and parse cards."""
    encodings = ["utf-8-sig", "utf-8", "cp949"]  # cp949 is a common Korean encoding
    last_err = None
    for enc in encodings:
        try:
            with path.open("r", encoding=enc, errors="strict") as f:
                lines = f.readlines()
            break
        except Exception as e:
            last_err = e
    else:
        raise RuntimeError(f"Failed to read {path} with tried encodings {encodings}: {last_err}")

    cards: list[tuple[str, str]] = []
    for idx, raw in enumerate(lines, 1):
        parsed = parse_line(raw)
        if parsed is None:
            # Skip silently if the line is blank or lacks '='
            continue
        cards.append(parsed)
    return cards

def write_csv(rows: list[tuple[str, str]], out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        # No header by default to avoid creating a dummy card in some flashcard apps
        for term, definition in rows:
            writer.writerow([term, definition])

def convert_folder(folder: Path, outdir: Path | None, combined: Path | None):
    txt_files = sorted(p for p in folder.glob("*.txt") if p.is_file())
    if not txt_files:
        print(f"No .txt files found in: {folder}")
        return

    if combined:
        all_rows: list[tuple[str, str]] = []
        for p in txt_files:
            rows = read_text(p)
            all_rows.extend(rows)
            print(f"Read {len(rows):4d} cards from {p.name}")
        write_csv(all_rows, combined)
        print(f"\nWrote {len(all_rows)} cards to: {combined}")
        return

    # one CSV per .txt
    for p in txt_files:
        rows = read_text(p)
        if outdir:
            out_path = outdir / f"{p.stem}.csv"
        else:
            out_path = p.with_suffix(".csv")
        write_csv(rows, out_path)
        print(f"Wrote {len(rows):4d} cards -> {out_path}")

def main():
    ap = argparse.ArgumentParser(description="Convert .txt flashcards to CSV.")
    ap.add_argument("folder", type=Path, help="Folder containing .txt files")
    ap.add_argument("-o", "--output-dir", type=Path, help="Directory for per-file CSV outputs")
    ap.add_argument("--combined", type=Path, help="Write all cards into this single CSV file")
    args = ap.parse_args()

    folder = args.folder
    if not folder.exists() or not folder.is_dir():
        ap.error(f"{folder} is not a directory")

    if args.combined and args.output_dir:
        print("[info] --combined ignores --output-dir (writing one file).")

    combined = args.combined
    outdir = None if combined else args.output_dir

    convert_folder(folder, outdir, combined)

if __name__ == "__main__":
    main()


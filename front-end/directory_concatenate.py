#!/usr/bin/env python3
"""directory_concatenate.py

Recursively collect code files under a directory (below a size threshold) and
dump them all into a single human‑readable text file.

The resulting text file is organised as:
1. A pretty tree view of the directory structure.
2. The full source of each collected file, preceded by a Markdown‑style header.

Example
-------
$ python directory_concatenate.py ./src --max-mb 0.5 --ext tsx ts js py --output src_dump.txt
"""

import argparse
from pathlib import Path
from typing import List

# Characters for drawing the tree (UTF‑8, compatible with `tree` command)
INDENT = "    "
BRANCH = "│   "
TEE = "├── "
LAST = "└── "

def build_tree(root: Path) -> List[str]:
    """Return a list of strings representing the directory tree."""
    lines: List[str] = []

    def _inner(dir_path: Path, prefix: str = ""):
        entries = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        count = len(entries)
        for idx, entry in enumerate(entries):
            connector = LAST if idx == count - 1 else TEE
            lines.append(f"{prefix}{connector}{entry.name}")
            if entry.is_dir():
                extension = INDENT if idx == count - 1 else BRANCH
                _inner(entry, prefix + extension)

    _inner(root)
    return lines

def gather_files(root: Path, extensions: List[str], max_bytes: int) -> List[Path]:
    """Return files whose extension is among *extensions* (case‑insensitive) and size ≤ *max_bytes*."""
    ext_set = {e.lower().lstrip('.') for e in extensions}
    files = [
        p for p in root.rglob('*')
        if p.is_file()
        and p.suffix.lower().lstrip('.') in ext_set
        and p.stat().st_size <= max_bytes
    ]
    return sorted(files, key=lambda p: p.relative_to(root).as_posix())

def write_output(out_path: Path, root: Path, tree_lines: List[str], files: List[Path]) -> None:
    """Write tree and file contents to *out_path*."""
    with out_path.open('w', encoding='utf-8') as fh:
        fh.write('Directory structure:\n')
        fh.write(f"{root.name}\n")
        for line in tree_lines:
            fh.write(f"{line}\n")
        fh.write('\n\n')
        for file in files:
            rel = file.relative_to(root).as_posix()
            fh.write(f"### {rel}\n\n")
            try:
                content = file.read_text(encoding='utf-8', errors='replace')
            except Exception as exc:
                content = f"[Could not read file: {exc}]\n"
            fh.write(content)
            if not content.endswith('\n'):
                fh.write('\n')
            fh.write('\n')

def main() -> None:
    parser = argparse.ArgumentParser(
        description='Concatenate code files inside a directory into one text file.')
    parser.add_argument('directory', type=Path, help='Root directory to scan.')
    parser.add_argument('--max-mb', type=float, default=1.0,
                        help='Maximum individual file size in MB (default: 1).')
    parser.add_argument('--ext', nargs='+', default=['tsx', 'ts', 'js'],
                        help='File extensions to include (space‑separated list).')
    parser.add_argument('--output', default='merged_code.txt',
                        help='Output text file name (default: merged_code.txt).')
    args = parser.parse_args()

    root = args.directory.expanduser().resolve()
    if not root.is_dir():
        parser.error(f'{root} is not a valid directory.')

    max_bytes = int(args.max_mb * 1024 * 1024)
    files = gather_files(root, args.ext, max_bytes)
    tree_lines = build_tree(root)

    out_path = Path(args.output).expanduser().resolve()
    write_output(out_path, root, tree_lines, files)
    print(f'✔ Wrote {len(files)} file(s) into {out_path}')

if __name__ == '__main__':
    main()

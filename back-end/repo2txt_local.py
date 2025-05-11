#!/usr/bin/env python3
"""
repo2txt_local.py  (v3 – full recursive tree)
------------------------------------------------
Walk **recursively** through an entire repository, dump every *textual* file
smaller than a given size into a single **Markdown** file, and show the **full
folder tree** (including directories that contain only excluded files).

Usage
~~~~~
    python repo2txt_local.py --max-mb 2 --output repo_dump.md --respect-gitignore

Key changes in *v3*
-------------------
1. **Full tree** – we gather *all* directories via `Path.rglob()` so the tree
   reflects the exact repo layout, even if some sub-folders end up empty after
   filtering.
2. Minor refactor: `collect_files()` now returns both `files` and `dirs`.
3. Tree printer improved to keep directories before files and show empty
   folders.
"""

from __future__ import annotations

import argparse
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# ──────────────────────────────── helpers ─────────────────────────────────────

LANG_MAP: Dict[str, str] = {
    "py": "python", "js": "javascript", "ts": "typescript", "tsx": "tsx",
    "jsx": "javascript", "java": "java", "go": "go", "rs": "rust", "c": "c",
    "cpp": "cpp", "h": "c", "hpp": "cpp", "html": "html", "css": "css",
    "json": "json", "md": "markdown", "sh": "bash", "yml": "yaml", "yaml": "yaml",
}


def is_binary(path: Path, sniff_bytes: int = 1024) -> bool:
    """Heuristic binary detection via NUL and non-printable ratio."""
    try:
        chunk = path.read_bytes()[:sniff_bytes]
    except Exception:
        return True
    if b"\0" in chunk:
        return True
    text_chars = bytes({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x7F)))
    non_printable = chunk.translate(None, text_chars)
    return len(non_printable) / max(len(chunk), 1) > 0.3


def git_ignored(path: Path, repo_root: Path) -> bool:
    """True if *path* is ignored by Git."""
    return (
        subprocess.run(
            ["git", "check-ignore", "-q", str(path)],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )

# ────────────────────────── directory tree printer ────────────────────────────

def build_tree(directories: List[Path], files: List[Path], root: Path) -> str:
    """Return an ASCII tree of *root*, listing all dirs then files."""
    tree: defaultdict[Path, List[Path]] = defaultdict(list)
    for d in directories:
        tree[d.parent].append(d)
    for f in files:
        tree[f.parent].append(f)

    for children in tree.values():
        children.sort(key=lambda x: (x.is_file(), x.name.lower()))

    lines: List[str] = [f"{root.name}/"]

    def _rec(dir_path: Path, prefix: str = ""):
        children = tree.get(dir_path, [])
        for idx, child in enumerate(children):
            connector = "└── " if idx == len(children) - 1 else "├── "
            lines.append(f"{prefix}{connector}{child.name}{'/' if child.is_dir() else ''}")
            if child.is_dir():
                _rec(child, prefix + ("    " if idx == len(children) - 1 else "│   "))

    _rec(root)
    return "\n".join(lines)

# ───────────────────────────────── crawler ────────────────────────────────────

def collect(root: Path, max_bytes: int, exclude: set[Path], respect_gitignore: bool) -> Tuple[List[Path], List[Path]]:
    """Return (dirs, files) lists after applying filters."""
    dirs: List[Path] = []
    files: List[Path] = []
    for p in root.rglob("*"):
        if p in exclude:
            continue
        if respect_gitignore and git_ignored(p, root):
            continue
        if p.is_dir():
            dirs.append(p)
        else:
            if p.stat().st_size > max_bytes or is_binary(p):
                continue
            files.append(p)
    return dirs, files


def guess_lang(path: Path) -> str:
    return LANG_MAP.get(path.suffix.lstrip("."), "")

# ─────────────────────────────────── main ─────────────────────────────────────

def main() -> None:
    pa = argparse.ArgumentParser("Dump repo into one Markdown file (recursive)")
    pa.add_argument("--root", default=".")
    pa.add_argument("--max-mb", type=float, default=2.0)
    pa.add_argument("--output", default="repo_dump.md")
    pa.add_argument("--respect-gitignore", action="store_true")
    args = pa.parse_args()

    root = Path(args.root).resolve()
    script_path = Path(__file__).resolve()
    out_path = Path(args.output).resolve()
    max_bytes = int(args.max_mb * 1024 * 1024)

    dirs, files = collect(
        root=root,
        max_bytes=max_bytes,
        exclude={script_path, out_path},
        respect_gitignore=args.respect_gitignore,
    )

    files.sort(key=lambda p: p.relative_to(root).parts)
    dirs.sort(key=lambda p: p.relative_to(root).parts)

    with out_path.open("w", encoding="utf-8") as fp:
        # 1. Full directory tree
        fp.write("## Repository Structure\n\n")
        fp.write("```text\n")
        fp.write(build_tree(dirs, files, root))
        fp.write("\n```\n\n")

        # 2. Source files
        fp.write("## Source Files\n\n")
        for f in files:
            rel = f.relative_to(root)
            lang = guess_lang(f)
            fp.write(f"### {rel}\n\n```{lang}\n")
            try:
                fp.write(f.read_text(errors="replace"))
            except Exception as exc:
                fp.write(f"<Could not read file: {exc}>\n")
            fp.write("\n```\n\n")

    print(f"✅ Wrote {len(files)} files to {out_path.relative_to(Path.cwd())} (limit {args.max_mb} MB)")


if __name__ == "__main__":
    main()

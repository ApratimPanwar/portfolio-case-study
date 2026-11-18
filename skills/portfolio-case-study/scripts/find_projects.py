#!/usr/bin/env python3
"""Find folders that look like design projects, and Figma links mentioned in them.

Usage:
    python find_projects.py [root ...] [--depth 4] [--min-images 3] [--top 25] [--json out.json]

With no root, scans ~/Desktop, ~/Documents, ~/Downloads, ~/Pictures.
Read-only. Never opens files outside the given roots.
"""
import argparse, json, os, re, sys, time
from pathlib import Path

IMG = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff", ".avif", ".heic"}
VID = {".mp4", ".mov", ".webm", ".m4v"}
DESIGN = {".psd", ".ai", ".indd", ".afdesign", ".afphoto", ".sketch", ".xd",
          ".fig", ".blend", ".c4d", ".3dm", ".skp", ".procreate", ".kra"}
DOC = {".pdf", ".pptx", ".key"}
TEXT = {".txt", ".md", ".url", ".webloc", ".html", ".htm", ".json", ".csv", ".rtf"}
SKIP = {"node_modules", ".git", "__pycache__", "venv", ".venv", "appdata",
        "$recycle.bin", "library", "cache", ".cache", "site-packages", "dist", "build"}
FIGMA = re.compile(r"https?://(?:www\.)?figma\.com/(?:design|file|proto|board|slides|make)/([0-9A-Za-z]{22,128})[^\s\"'<>)\]]*")
MAX_TEXT = 512 * 1024


def figma_links(path: Path):
    try:
        if path.stat().st_size > MAX_TEXT:
            return []
        txt = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []
    return [m.group(0) for m in FIGMA.finditer(txt)]


def scan(root: Path, depth: int):
    """Yield (folder, stats) for every folder up to `depth` below root."""
    root_depth = len(root.parts)
    for dirpath, dirnames, filenames in os.walk(root):
        d = Path(dirpath)
        dirnames[:] = [n for n in dirnames
                       if n.lower() not in SKIP and not n.startswith(".")]
        if len(d.parts) - root_depth >= depth:
            dirnames[:] = []
        st = {"images": 0, "video": 0, "design": 0, "docs": 0,
              "figma": [], "newest": 0.0, "bytes": 0, "design_files": []}
        for f in filenames:
            p = d / f
            ext = p.suffix.lower()
            try:
                s = p.stat()
            except OSError:
                continue
            if ext in IMG:
                st["images"] += 1
            elif ext in VID:
                st["video"] += 1
            elif ext in DESIGN:
                st["design"] += 1
                st["design_files"].append(f)
            elif ext in DOC:
                st["docs"] += 1
            elif ext in TEXT:
                st["figma"] += figma_links(p)
            else:
                continue
            st["bytes"] += s.st_size
            st["newest"] = max(st["newest"], s.st_mtime)
        yield d, st


def score(st):
    # A project folder: several images, ideally source files or a Figma link,
    # maybe a process PDF. Loose screenshots alone score low.
    s = min(st["images"], 40) + 3 * min(st["video"], 5)
    s += 8 * min(st["design"], 3) + 10 * min(len(set(st["figma"])), 3)
    s += 3 * min(st["docs"], 3)
    # Photo dumps (images only, no source files, links or docs) are rarely a
    # single project. Demote them so real projects surface first.
    if not (st["design"] or st["figma"] or st["docs"]):
        s *= 0.6
    return round(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="*", type=Path)
    ap.add_argument("--depth", type=int, default=4)
    ap.add_argument("--min-images", type=int, default=3)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    home = Path.home()
    roots = a.roots or [home / n for n in ("Desktop", "Documents", "Downloads", "Pictures")]
    roots = [r for r in roots if r.is_dir()]
    if not roots:
        sys.exit("no readable roots")

    found = []
    for r in roots:
        for d, st in scan(r, a.depth):
            if d == r:      # the root itself is a container, not a project
                continue
            if st["images"] + st["video"] < a.min_images and not st["figma"] and not st["design"]:
                continue
            st["figma"] = sorted(set(st["figma"]))
            found.append({"path": str(d), "score": score(st), **st})

    # A folder whose images all sit in one child is less useful than the child.
    found.sort(key=lambda x: (-x["score"], -x["newest"]))
    top = found[: a.top]

    print(f"\nscanned: {', '.join(str(r) for r in roots)}  (depth {a.depth})")
    print(f"{len(found)} candidate folder(s); top {len(top)}:\n")
    print(f"{'#':>3} {'score':>5} {'img':>4} {'vid':>3} {'src':>3} {'fig':>3}  {'modified':<10}  path")
    print("-" * 100)
    for i, f in enumerate(top, 1):
        mod = time.strftime("%Y-%m-%d", time.localtime(f["newest"])) if f["newest"] else "-"
        print(f"{i:>3} {f['score']:>5} {f['images']:>4} {f['video']:>3} {f['design']:>3} "
              f"{len(f['figma']):>3}  {mod:<10}  {f['path']}")
    figs = sorted({u for f in found for u in f["figma"]})
    if figs:
        print(f"\nFigma links found in files ({len(figs)}):")
        for u in figs:
            print(f"  {u}")
    print("\nsrc = source design files (.psd .ai .indd .sketch .xd .fig ...). "
          ".fig is not readable offline; ask for its cloud URL.")

    if a.json:
        Path(a.json).write_text(json.dumps({"roots": [str(r) for r in roots],
                                            "candidates": found, "figma": figs},
                                           indent=2), encoding="utf-8")
        print(f"wrote {a.json}")


if __name__ == "__main__":
    main()

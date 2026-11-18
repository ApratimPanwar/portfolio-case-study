#!/usr/bin/env python3
"""Inventory a project image folder and propose a masonry layout.

Usage:
    python collect_assets.py <folder> [--columns 3] [--platform generic|cargo]
                                      [--wide 1.6] [--out assets.json]

Writes assets.json (default: inside the folder) and prints a review table.
Layout is height-balanced only; reorder for narrative before using it.
"""
import argparse, json, sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow required:  pip install pillow")

Image.MAX_IMAGE_PIXELS = 600_000_000   # user's own files; process boards can be huge

IMG = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff", ".bmp", ".avif"}
VID = {".mp4", ".mov", ".webm", ".m4v"}
MAX_PX = 4000
MAX_BYTES = 4 << 20


def human(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{u}"
        n /= 1024
    return f"{n:.1f}TB"


def scan(folder: Path):
    items = []
    for p in sorted(folder.rglob("*"), key=lambda q: str(q).lower()):
        if not p.is_file() or p.name.startswith("."):
            continue
        ext = p.suffix.lower()
        if ext not in IMG and ext not in VID:
            continue
        rec = {"file": p.name, "path": str(p), "rel": str(p.relative_to(folder)),
               "kind": "video" if ext in VID else "image",
               "bytes": p.stat().st_size,
               "w": None, "h": None, "aspect": None, "orient": None,
               "heavy": p.stat().st_size > MAX_BYTES}
        if rec["kind"] == "image":
            try:
                with Image.open(p) as im:
                    w, h = im.size
                rec.update(w=w, h=h, aspect=round(w / h, 3))
                rec["orient"] = ("landscape" if w > h * 1.05
                                 else "portrait" if h > w * 1.05 else "square")
                rec["heavy"] = rec["heavy"] or max(w, h) > MAX_PX
            except Exception as e:
                rec["error"] = f"{type(e).__name__}: {e}"
        items.append(rec)
    return items


def assign(items, cols, wide, platform):
    heights = [0.0] * cols
    n = 0
    for it in items:
        if it.get("error"):
            it["column"] = it["span"] = it["slot"] = None
            continue
        asp = it.get("aspect") or 1.0
        span = 2 if (cols >= 2 and asp >= wide and it["kind"] == "image") else 1
        if span == 2:
            c = min(range(cols - 1), key=lambda i: max(heights[i], heights[i + 1]))
            top = max(heights[c], heights[c + 1]) + 1 / asp
            heights[c] = heights[c + 1] = top
        else:
            c = min(range(cols), key=lambda i: heights[i])
            heights[c] += 1 / asp
        it["order"] = n + 1
        it["column"] = c
        it["span"] = span
        it["slot"] = f"column-{c}-slot-{n}" if platform == "cargo" else None
        n += 1
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", type=Path)
    ap.add_argument("--columns", type=int, default=3)
    ap.add_argument("--platform", choices=["generic", "cargo"], default="generic")
    ap.add_argument("--wide", type=float, default=1.6,
                    help="aspect ratio at/above which an image spans 2 columns")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    if not a.folder.is_dir():
        sys.exit(f"not a directory: {a.folder}")
    if a.columns < 1:
        sys.exit("--columns must be >= 1")

    items = assign(scan(a.folder), a.columns, a.wide, a.platform)
    if not items:
        sys.exit(f"no images or video found under {a.folder}")

    out = Path(a.out) if a.out else a.folder / "assets.json"
    out.write_text(json.dumps({"folder": str(a.folder), "columns": a.columns,
                               "platform": a.platform, "count": len(items),
                               "items": items}, indent=2), encoding="utf-8")

    print(f"\n{len(items)} asset(s) in {a.folder}  |  {a.columns} col  |  {a.platform}\n")
    print(f"{'#':>3}  {'file':<34} {'dims':>11} {'asp':>5} {'size':>7}  placement")
    print("-" * 88)
    for i, it in enumerate(items, 1):
        name = it["file"] if len(it["file"]) <= 34 else it["file"][:31] + "..."
        if it.get("error"):
            print(f"{i:>3}  {name:<34} {'UNREADABLE':>11}  {it['error'][:30]}")
            continue
        dims = f"{it['w']}x{it['h']}" if it["w"] else "video"
        asp = f"{it['aspect']:.2f}" if it["aspect"] else "-"
        place = it["slot"] or f"col {it['column']}"
        if it["span"] == 2:
            place += " (span 2)"
        if it["heavy"]:
            place += "  [!heavy]"
        print(f"{i:>3}  {name:<34} {dims:>11} {asp:>5} {human(it['bytes']):>7}  {place}")

    bad = sum(1 for i in items if i.get("error"))
    heavy = sum(1 for i in items if i.get("heavy"))
    print(f"\nwrote {out}")
    if bad:
        print(f"WARNING: {bad} unreadable file(s) excluded from layout")
    if heavy:
        print(f"[!heavy] {heavy} file(s) over {MAX_PX}px or {MAX_BYTES >> 20}MB - downscale before upload")
    print("Layout is height-balanced only. Reorder for narrative before use.\n")


if __name__ == "__main__":
    main()

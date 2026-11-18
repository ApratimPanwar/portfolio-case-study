#!/usr/bin/env python3
"""Make web-ready copies of project images. Originals are never modified.

Usage:
    python prepare_images.py <assets.json | folder> <out_dir>
                             [--max 2400] [--quality 82] [--format auto|keep|webp|jpg]
                             [--prefix slug]

- Downscales to fit --max px wide and --max x 4 tall (never upscales), so tall
  process strips stay readable instead of collapsing to a sliver.
- Strips EXIF/GPS metadata (location data must not ship to a public site).
- Applies EXIF orientation before stripping so photos stay upright.
- Names files <prefix>-01.ext, <prefix>-02.ext ... in the given order, so the
  upload order and the file order are the same thing.
- Reads order from assets.json (after you have reordered it), else filename order.
- auto (default): PNG/GIF with transparency stay PNG; opaque PNGs stay PNG only
  if small (flat graphics), else become JPEG (renders, mockups); the rest JPEG.
- Copies video files through untouched.
Writes <out_dir>/manifest.json mapping each output to its source.
"""
import argparse, io, json, re, shutil, sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow required:  pip install pillow")

# These are the user's own local files; tall process boards can exceed Pillow's
# default 89MP "decompression bomb" guard, which is meant for untrusted input.
Image.MAX_IMAGE_PIXELS = 600_000_000
PNG_KEEP_BYTES = 600 * 1024   # opaque PNGs bigger than this become JPEG in auto mode

IMG = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff", ".bmp", ".avif"}
VID = {".mp4", ".mov", ".webm", ".m4v"}


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "img"


def has_alpha(im):
    """True only if the image actually uses transparency, not just has a channel."""
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        return im.convert("RGBA").getchannel("A").getextrema()[0] < 255
    return False


def sources(src: Path):
    if src.is_file() and src.suffix == ".json":
        data = json.loads(src.read_text(encoding="utf-8"))
        items = [i for i in data["items"] if not i.get("error")]
        items.sort(key=lambda i: i.get("order") or 10**6)
        return [Path(i["path"]) for i in items]
    if src.is_dir():
        return sorted((p for p in src.rglob("*") if p.suffix.lower() in IMG | VID),
                      key=lambda p: str(p).lower())
    sys.exit(f"not an assets.json or folder: {src}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--max", type=int, default=2400)
    ap.add_argument("--quality", type=int, default=82)
    ap.add_argument("--format", choices=["auto", "keep", "webp", "jpg"], default="auto")
    ap.add_argument("--prefix", default=None)
    a = ap.parse_args()

    files = sources(a.src)
    if not files:
        sys.exit("nothing to prepare")
    a.out.mkdir(parents=True, exist_ok=True)
    prefix = slugify(a.prefix or (a.src.stem if a.src.is_dir() else a.src.parent.name))
    width = max(2, len(str(len(files))))
    manifest, before, after = [], 0, 0

    for n, p in enumerate(files, 1):
        ext = p.suffix.lower()
        before += p.stat().st_size
        if ext in VID:
            dst = a.out / f"{prefix}-{n:0{width}d}{ext}"
            shutil.copy2(p, dst)
        else:
            with Image.open(p) as im:
                im = ImageOps.exif_transpose(im)
                im.thumbnail((a.max, a.max * 4), Image.LANCZOS)
                fmt = a.format
                if fmt == "keep":
                    fmt = {".png": "png", ".gif": "png", ".webp": "webp"}.get(ext, "jpg")
                elif fmt == "auto":
                    fmt = "jpg"
                    if ext in (".png", ".gif", ".webp"):
                        if has_alpha(im):
                            fmt = "png"
                        else:
                            buf = io.BytesIO()
                            im.save(buf, "PNG", optimize=True)
                            if buf.tell() <= PNG_KEEP_BYTES:
                                fmt = "png"
                if fmt == "jpg" and im.mode in ("RGBA", "LA", "P"):
                    rgba = im.convert("RGBA")
                    bg = Image.new("RGB", im.size, "white")
                    bg.paste(rgba, mask=rgba.split()[-1])
                    im = bg
                elif fmt == "jpg" and im.mode != "RGB":
                    im = im.convert("RGB")
                dst = a.out / f"{prefix}-{n:0{width}d}.{fmt}"
                kw = {"png": {"optimize": True},
                      "webp": {"quality": a.quality, "method": 6},
                      "jpg": {"quality": a.quality, "optimize": True, "progressive": True}}[fmt]
                # no exif= argument, so metadata is not written
                im.save(dst, "JPEG" if fmt == "jpg" else fmt.upper(), **kw)
        after += dst.stat().st_size
        manifest.append({"order": n, "file": dst.name, "source": str(p)})
        print(f"{n:>3}  {p.name[:40]:<40} -> {dst.name}")

    (a.out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    mb = lambda b: f"{b / 2**20:.1f}MB"
    print(f"\n{len(files)} file(s): {mb(before)} -> {mb(after)}  in {a.out}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Turn Adobe Illustrator files into case-study material without opening Illustrator.

Usage:
    python extract_ai.py <file.ai | folder> <out_dir> [--dpi auto|N] [--max 2400]
                         [--artboards 1,3-5] [--no-text]

Most .ai files are saved with "Create PDF Compatible File" on (Illustrator's
default), so every artboard is a PDF page. For each file this writes:
    <out>/<stem>-ab01.png ...   one PNG per artboard
    <out>/<stem>.json           artboard count, sizes (mm), text per artboard
and prints what it found. Originals are only read, never modified.

Also detects the cases this route cannot handle:
  - saved without PDF content  -> use scripts/illustrator/ (needs Illustrator)
  - not really Illustrator (an SVG or other file renamed .ai) -> reported, skipped

--dpi auto (default) picks a resolution per artboard so its long edge lands near
--max px: a 70x120mm label renders at ~500dpi, a 700mm poster at ~85dpi.

Rendering uses pdftoppm (poppler) if on PATH, else PyMuPDF (`pip install pymupdf`).
Text and sizes use pypdf (`pip install pypdf`).
"""
import argparse, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

try:
    import pypdf
except ImportError:
    sys.exit("pypdf required:  pip install pypdf")

NO_PDF_CONTENT = re.compile(r"saved\s+without\s+PDF\s+Content", re.I)
PT_TO_MM = 25.4 / 72


def sniff(path: Path):
    head = path.open("rb").read(1024).lstrip()
    if head.startswith(b"%PDF"):
        return "pdf"
    if head.startswith(b"%!PS-Adobe"):
        return "legacy"          # pre-CS / EPS-style .ai with no PDF layer
    if head.startswith(b"<?xml") or head.startswith(b"<svg") or b"<svg" in head:
        return "svg"
    return "unknown"


def parse_range(spec, n):
    if not spec:
        return list(range(1, n + 1))
    out = set()
    for part in spec.split(","):
        a, _, b = part.partition("-")
        lo, hi = int(a), int(b or a)
        out.update(range(max(1, lo), min(n, hi) + 1))
    return sorted(out)


def renderer():
    if shutil.which("pdftoppm"):
        return "pdftoppm"
    try:
        import fitz  # noqa: F401  (PyMuPDF)
        return "pymupdf"
    except ImportError:
        return None


def render(engine, src: Path, page: int, dpi: int, dst: Path):
    if engine == "pdftoppm":
        with tempfile.TemporaryDirectory() as td:
            base = Path(td) / "p"
            subprocess.run(["pdftoppm", "-png", "-r", str(dpi), "-f", str(page), "-l", str(page),
                            "-singlefile", str(src), str(base)],
                           check=True, capture_output=True)
            shutil.move(str(base) + ".png", dst)
    else:
        import fitz
        with fitz.open(src) as doc:
            doc[page - 1].get_pixmap(dpi=dpi, alpha=False).save(dst)


def cap_width(dst: Path, max_px: int):
    try:
        from PIL import Image
    except ImportError:
        return
    Image.MAX_IMAGE_PIXELS = 600_000_000
    with Image.open(dst) as im:
        if im.width <= max_px:
            return
        im = im.copy()
    im.thumbnail((max_px, max_px * 4), Image.LANCZOS)
    im.save(dst, optimize=True)


def extract(path: Path, out: Path, a, engine):
    kind = sniff(path)
    rec = {"file": str(path), "kind": kind}
    if kind == "svg":
        rec["note"] = "not an Illustrator file: SVG/XML with a .ai extension. Use it as an SVG or ignore it."
        return rec
    if kind in ("legacy", "unknown"):
        rec["note"] = "no PDF layer; open with scripts/illustrator/ (needs Illustrator)"
        return rec

    try:
        reader = pypdf.PdfReader(str(path))
    except Exception as e:  # damaged, encrypted, or exotic
        rec.update(kind="unreadable", note=f"{type(e).__name__}: {e}")
        return rec

    n = len(reader.pages)
    first_text = (reader.pages[0].extract_text() or "") if n else ""
    if NO_PDF_CONTENT.search(first_text):
        rec.update(kind="no-pdf-content",
                   note="saved without PDF content; only Illustrator can read it (scripts/illustrator/)")
        return rec

    rec["creator"] = str((reader.metadata or {}).get("/Creator", ""))
    rec["artboards"] = []
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", path.stem).strip("-") or "artboard"
    width = max(2, len(str(n)))
    for i in parse_range(a.artboards, n):
        pg = reader.pages[i - 1]
        box = pg.trimbox if "/TrimBox" in pg else pg.mediabox
        ab = {"index": i,
              "w_mm": round(float(box.width) * PT_TO_MM, 1),
              "h_mm": round(float(box.height) * PT_TO_MM, 1)}
        if engine:
            dst = out / f"{stem}-ab{i:0{width}d}.png"
            if a.dpi == "auto":
                long_in = max(float(box.width), float(box.height)) / 72
                dpi = int(min(600, max(72, a.max / long_in)))
            else:
                dpi = int(a.dpi)
            render(engine, path, i, dpi, dst)
            ab["dpi"] = dpi
            cap_width(dst, a.max)
            ab["png"] = dst.name
        if not a.no_text:
            txt = pg.extract_text() or ""
            ab["text"] = re.sub(r"[ \t]+", " ", txt).strip()
        rec["artboards"].append(ab)
    rec["artboard_count"] = n
    (out / f"{stem}.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--dpi", default="auto", help='"auto" or a number')
    ap.add_argument("--max", type=int, default=2400, help="max PNG width in px")
    ap.add_argument("--artboards", default=None, help="e.g. 1,3-5 (default: all)")
    ap.add_argument("--no-text", action="store_true")
    a = ap.parse_args()

    files = ([a.src] if a.src.is_file()
             else sorted(p for p in a.src.rglob("*") if p.suffix.lower() == ".ai"))
    if not files:
        sys.exit(f"no .ai files at {a.src}")
    a.out.mkdir(parents=True, exist_ok=True)

    engine = renderer()
    if not engine:
        print("note: no renderer (install poppler for pdftoppm, or `pip install pymupdf`); "
              "extracting sizes and text only\n")

    results = []
    for f in files:
        r = extract(f, a.out, a, engine)
        results.append(r)
        if r.get("artboards") is not None:
            sizes = sorted({f"{x['w_mm']:g}x{x['h_mm']:g}mm" for x in r["artboards"]})
            words = sum(len(x.get("text", "").split()) for x in r["artboards"])
            print(f"OK    {f.name}: {r['artboard_count']} artboard(s), {', '.join(sizes)}, {words} words")
        else:
            print(f"SKIP  {f.name}: {r['note']}")

    (a.out / "ai_index.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    ok = sum(1 for r in results if r.get("artboards") is not None)
    print(f"\n{ok}/{len(results)} file(s) extracted into {a.out}  (renderer: {engine or 'none'})")


if __name__ == "__main__":
    main()

# Source design files

Finished work often lives in source files, not exports. Pull artboards out of
them so the case study shows the real artwork, and read them for facts worth
writing about (formats, sizes, fonts, number of variants).

## Adobe Illustrator (.ai)

Two routes. Default to A; use B when A can't read the file or you need
information a PDF doesn't carry.

### A. Without Illustrator - `scripts/extract_ai.py`

```
python scripts/extract_ai.py <file.ai | folder> <work>/source [--artboards 1,3-5]
```

Works on any machine (pypdf + pdftoppm or PyMuPDF). Illustrator saves a PDF
layer by default ("Create PDF Compatible File"), so each artboard is a page.

You get, per artboard: a PNG (auto DPI: long edge near 2400px, so a 70mm label
and a 700mm poster both come out usable), its trim size in mm, and its live text.
Plus `<stem>.json` and `ai_index.json`.

It reports and skips:
- **saved without PDF content**: Illustrator writes a placeholder page instead
  of the artwork. Detected by its text. Use route B.
- **not really Illustrator**: SVG or other files renamed `.ai`. Use as-is or ignore.
- **legacy/unreadable**: pre-CS files or damaged ones. Route B, or ask the user.

### B. With Illustrator - `scripts/illustrator/`

Drives the user's installed Illustrator. Adds what route A can't see:
artboard **names**, layer tree (visible/locked), **fonts used**, spot colours,
linked files with a **broken-link check**, and exports through Illustrator's own
renderer.

Windows:
```
pwsh scripts/illustrator/run_illustrator.ps1 -Path <file.ai>[,<file.ai>...] -Out <work>/source -Scale 100
```

macOS (untested; same JSX):
```
osascript -e 'tell application id "com.adobe.illustrator" to do javascript (POSIX file "<skill>/scripts/illustrator/ai_inspect.jsx") with arguments {"<abs file.ai>", "<abs out dir>", "100"}'
```

Behaviour:
- Illustrator opens on screen. Tell the user before running it.
- Never saves. Files it opened are closed unsaved. Files the user already had
  open stay open, untouched apart from the active artboard. If the script
  launched Illustrator it quits it; if Illustrator was already running it stays.
- Takes ~5s to launch and ~3s to exit; the runner waits and retries, so
  back-to-back runs don't collide.
- `-Scale` is percent of 72ppi: 100 gives 1px per point.

## Using the output

- Add the artboard PNGs to the image set:
  `collect_assets.py <project folder> <work>/source --out <work>/assets.json`,
  then reorder and prune. Not every artboard belongs; drafts, dielines and
  duplicate "copy" artboards usually don't.
- **Pick one version.** Folders hold variants: `name [Recovered].ai`, `_PRINT`,
  `_draft`, `final_final`. Ask which is the shipped one before extracting all.
- Extracted text is for understanding the project (product names, formats,
  claims), not for pasting. Packaging and print often carry phone numbers,
  emails, addresses and licence numbers: never copy those into a case study.
- Facts worth a sentence: number of SKUs/variants (artboards), formats and sizes,
  typefaces (route B), spot colours for print work.

## Other formats

- **PDF** (process decks, print-ready files): same as route A; `extract_ai.py`
  reads any PDF if renamed or passed directly, or use `pdftoppm` directly.
- **Figma**: use the Figma MCP (see SKILL.md), not exports.
- **.psd, .indd, .sketch, .xd, .afdesign**: not handled. Ask for exports, or for
  the app's own PDF/PNG export.
- **.fig** (local Figma file): not readable offline; ask for the cloud URL.

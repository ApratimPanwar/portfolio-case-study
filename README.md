# portfolio-case-study

A [Claude Code](https://claude.com/claude-code) skill that finds the design
projects you never published, writes them up in your portfolio's own house style,
and puts them on your site.

There's always one project that never makes it onto the portfolio. It's finished,
shipped, paid for, and it sits in a folder. This skill writes down your case-study
format once, so every new write-up starts where the last one ended, and gets it
the rest of the way onto the site.

## How it works

```
DISCOVER  folders + Figma         ->  candidate projects   (you pick)
LEARN     your existing portfolio ->  house-rules.md       (once)
BUILD     project + house rules   ->  case.json + images   (per project)
DEPLOY    case.json               ->  your site            (draft -> preview -> you say go)
```

**DISCOVER** scans your folders for things that look like projects: images,
source files (`.psd`, `.ai`, `.indd`, `.sketch`…), process PDFs, and Figma links
mentioned in notes. It ranks them and you pick one. With a Figma token it can also
list your team's Figma files.

**LEARN** reads your live portfolio and records the rules it actually follows:
structure, word counts, image grid, title pattern and voice, with real quotes as
do/don't examples. It shows you the inconsistencies it found, so you decide what's
a rule and what's a mistake. It also records where case studies live on your
platform (CMS collection, repo folder, block markup).

**BUILD** takes the project folder, Figma links and your rough notes. If the
finished artwork lives in Illustrator files, it pulls every artboard out as an
image (sized for the web whether it's a 70mm label or a 700mm poster), along with
the text, print sizes and, with Illustrator installed, artboard names, fonts and
linked-file status. A raw
voice-note transcript is ideal: who the client was, what they asked for, what
changed and why. It writes the case study in your voice, orders the images for the
story, and makes web-ready copies (downscaled, GPS/EXIF stripped). The result is a
platform-neutral `case.json`. It doesn't make up metrics, quotes or results.

**DEPLOY** sends `case.json` to your site:

| Platform | How | What's automated |
|---|---|---|
| Custom / static / Claude-built site (Astro, Next, Hugo, 11ty, Jekyll, HTML) | edits your repo, builds, previews, pushes | everything; you approve the push |
| Framer | [Framer Server API](https://www.framer.com/developers/server-api-introduction) script | images, CMS item, preview; you approve production |
| Webflow | Webflow Data API v2 | staged CMS item; you approve publishing |
| Cargo | drives the editor in your signed-in Chrome | uploads + layout; you press Publish |
| Squarespace, Wix, Notion, Behance… | paste-ready content + image order | the writing |

Nothing goes live without your explicit yes. Every route goes draft → preview →
your approval → live.

When you correct something, it offers to write the correction into
`house-rules.md`, so the fix sticks for every future case study.

## Install

In Claude Code:

```
/plugin marketplace add ApratimPanwar/portfolio-case-study
/plugin install portfolio-case-study@portfolio-case-study
```

Or copy `skills/portfolio-case-study/` into `~/.claude/skills/`.

Requirements:
- Python 3 with Pillow and pypdf: `pip install pillow pypdf`
- For Illustrator files: [poppler](https://poppler.freedesktop.org/) (`pdftoppm`) or `pip install pymupdf`.
  Optional: Adobe Illustrator, for artboard names, fonts and link checks (Windows script included; macOS command documented)
- For Framer: Node 22+, then `npm install` in `skills/portfolio-case-study/scripts/framer/`
- For Figma: the [Figma MCP server](https://help.figma.com/hc/en-us/articles/32132100833559) connected in Claude Code
- For Cargo/browser-assisted deploys: [Claude in Chrome](https://claude.com/chrome)

## Use

```
Find projects on my Desktop I haven't put on my portfolio
```
```
Learn the house style from https://your-portfolio.com
```
```
Make a case study from ~/Projects/acme-rebrand, Figma: <url>.
Notes: <paste your voice-note transcript>
```
```
Deploy it to my Framer site
```

## Keys and tokens

Set these in your own environment. The skill never asks for them in chat and
never writes them to files.

| Variable | For | Where to get it |
|---|---|---|
| `FRAMER_API_KEY` | Framer deploys | Framer → Site Settings → General → API keys |
| `WEBFLOW_TOKEN` | Webflow deploys | Webflow → Site settings → Apps & integrations → API access (CMS read/write) |
| `FIGMA_TOKEN` | listing Figma files (optional) | Figma → Settings → Security → Personal access tokens (`projects:read`) |

## Scripts

All in `skills/portfolio-case-study/scripts/`. They work on their own too.

| Script | Does |
|---|---|
| `find_projects.py [roots]` | rank folders that look like design projects; collect Figma links in them |
| `figma_list.py <team_id>` | list Figma files in a team (needs `FIGMA_TOKEN`) |
| `extract_ai.py <file.ai or folder> <out>` | artboards to PNG, print sizes, text; flags files that need Illustrator |
| `illustrator/run_illustrator.ps1` | drive Illustrator: artboard names, layers, fonts, spot colours, broken links, exports |
| `collect_assets.py <folders...>` | inventory images, flag oversized files, propose a grid |
| `prepare_images.py <assets.json> <out>` | downscale, strip EXIF/GPS, number in display order |
| `framer/deploy.mjs <case.json>` | dry run → draft → preview → production, one flag per stage |

## Figma access

The connected Figma account must be able to open the file. A share link that
opens in your browser can still be refused to the API. If so, set link sharing to
"Anyone with the link · can view", or export the frames into the project folder.

## Credit

Inspired by [@0xCharlota's thread](https://x.com/0xCharlota/status/2105590462622871841)
on turning a case-study format into a reusable Framer Skill. This takes the same
idea across platforms for Claude Code.

## License

MIT

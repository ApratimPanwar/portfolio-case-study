# portfolio-case-study

A [Claude Code](https://claude.com/claude-code) skill that turns finished design
projects into portfolio case studies, written in your portfolio's own house style.

There's always one project that never makes it onto the portfolio. It's finished
and shipped, and it sits in a folder. This skill writes down your case-study
format once, so each new write-up starts where the last one ended.

## How it works

```
LEARN   your existing portfolio  ──►  house-rules.md          (once)
BUILD   images + Figma + notes + house-rules.md  ──►  case study   (per project)
```

**LEARN** reads your live portfolio (or exported pages) and records the rules it
actually follows: structure, word counts, image grid, title pattern and voice,
with real quotes as do/don't examples. It shows you the inconsistencies it finds
so you decide what's a rule and what's a mistake.

**BUILD** takes:
- a folder of project images
- Figma links (optional)
- rough notes. A raw voice-note transcript is ideal: who the client was, what
  they asked for, what changed and why.

It gives you back:
- the image upload order, with oversized files flagged
- the case study, ready to paste into your platform
- the questions it couldn't answer from your notes

It doesn't make up metrics, quotes or results.

When you correct something, it offers to write the correction into
`house-rules.md`, so the fix sticks for every future case study.

## Install

In Claude Code:

```
/plugin marketplace add ApratimPanwar/portfolio-case-study
/plugin install portfolio-case-study@portfolio-case-study
```

Or copy `skills/portfolio-case-study/` into `~/.claude/skills/` (all projects)
or `.claude/skills/` (one project).

The image script needs Python 3 and Pillow: `pip install pillow`.

## Use

```
Learn the house style from https://your-portfolio.com
```
```
Make a case study from ~/Projects/acme-rebrand, Figma: <url>.
Notes: <paste your voice-note transcript>
```

## Platforms

| Platform | What you get | Last step |
|---|---|---|
| Cargo | Block HTML with gallery slots | Drag images in, paste HTML |
| Framer | Values for each CMS field | Upload images to the CMS item |
| Webflow | Values for each CMS field, rich text as HTML | Paste fields, upload images |
| Squarespace | Text for each block, in page order | Build the blocks |
| Notion | Markdown | Paste, drag images in |
| Static sites (Astro, Next, Hugo…) | Markdown file + images in your repo | Nothing. Claude can finish it |

Most hosted builders don't let outside tools write page content, and they assign
their own image IDs on upload. So the skill hands you paste-ready content and an
upload order instead of claiming to publish for you.

## Figma

Uses the [Figma MCP server](https://help.figma.com/hc/en-us/articles/32132100833559)
if it's connected. The connected account must be able to open the file. A share
link that opens in your browser can still be refused. If so, set link sharing to
"Anyone with the link · can view", or export the frames into the image folder.

## Credit

Inspired by [@0xCharlota's thread](https://x.com/0xCharlota/status/2105590462622871841)
on turning a case-study format into a reusable Framer Skill. This is a
platform-independent take on the same idea for Claude Code.

## License

MIT

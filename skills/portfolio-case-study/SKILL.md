---
name: portfolio-case-study
description: Turn a finished design project into a portfolio case study that matches the portfolio it is going on. Two modes - LEARN reads an existing portfolio (URL or exported pages) and writes down its house rules once; BUILD takes a folder of images, optional Figma URLs, and raw notes or a voice-note transcript, and produces a ready-to-post case study in that house style for the target platform (Cargo, Framer, Webflow, Squarespace, Notion, Markdown/static HTML). Use when someone wants to write up a project, add a project to their portfolio, clear a case-study backlog, or set up a repeatable case-study format.
---

# Portfolio case study

The point: explain the format once, then every new project starts where the last
one ended. The rules live in a file next to the project, not in a prompt someone
has to remember.

Two modes. Run LEARN once per portfolio. Run BUILD once per project.

```
LEARN   existing portfolio  ──►  house-rules.md
BUILD   images + Figma + notes + house-rules.md  ──►  case study + upload list
```

If `house-rules.md` does not exist yet, BUILD must run LEARN first. Never build
from defaults silently.

---

## LEARN — write down the rules the portfolio already follows

**Find the rules file location first.** Default: `./house-rules.md` in the
project root. If the user already has one anywhere, use it and skip to BUILD.

Inputs, any one of:
- the portfolio URL (preferred — read it with the browser tools)
- exported pages / screenshots / a template the user wants to remix
- nothing — then interview the user, and say clearly the rules are invented, not learned

Procedure: follow `references/learning-rules.md`. It covers what to measure on
the live site (structure, word counts, image counts, markup), how to read the
voice, and how to separate *rules* from *accidents*.

Output: fill `templates/house-rules.template.md` and save it as `house-rules.md`.
Show the user the rules and the **inconsistencies you found** before saving —
they decide whether a deviation is a rule or a mistake.

---

## BUILD — make one case study

### Inputs (ask for anything missing; do not guess)

1. **Image folder** — absolute path, must exist.
2. **Figma URLs** — optional. Cloud links only.
3. **Notes** — raw is correct. A pasted voice-note transcript is ideal: who the
   client was, what they asked for, what changed and why. Do not ask the user to
   clean it up; that is this skill's job.
4. **Supporting link** — optional (process PDF, live site, Behance, Instagram).

### Steps

1. **Load `house-rules.md`.** Everything below defers to it.
2. **Inventory images.** Run
   `python scripts/collect_assets.py <folder> --columns <N from house rules>`.
   Gets dimensions, flags heavy files, proposes a height-balanced grid. The order
   it proposes is by filename — reorder for the story (lead image → context →
   process → detail → final application).
3. **Read Figma, if given.** `get_metadata` first for the frame/page tree, then
   `get_screenshot` on the frames that matter, `get_design_context` only when you
   need exact values to write about. Figma tells you *what was designed and how it
   is organised*; the image folder is still the image source.
4. **Extract the story from the notes.** Before writing a word, list:
   client & problem · constraint · what you did · what you rejected and why ·
   what shipped · evidence it worked. Mark anything not in the notes as missing.
   Ask about the missing items if they matter; otherwise leave them out.
5. **Write.** House rules first, then `references/writing-rules.md` for anything
   the house rules do not cover.
6. **Emit for the platform.** See `references/platforms.md`.
7. **Hand off**, in this order:
   - image upload order (numbered filenames, with any `[!heavy]` files called out)
   - the case study, paste-ready for the platform
   - open questions / things you were unsure about — said plainly
   - any rule you broke on purpose, and why

### Improving the skill

When the user corrects the output ("captions never end with a full stop", "lead
with the outcome, not the client"), offer to write the correction into
`house-rules.md`. That is the whole advantage over prompting from scratch: fix a
rule once and it stays fixed.

---

## Gotchas

- **No made-up facts.** No metrics, quotes, timelines, team sizes, or results
  that are not in the notes. A case study with an invented number is worse than
  one without a number.
- **Learning ≠ copying mistakes.** Existing portfolios contain typos, one-off
  layouts, and weak copy. LEARN captures them as *observed*, and the user decides
  what becomes a rule. Do not encode a typo as house style.
- **Hosted builders mint their own image IDs.** Cargo (`media-item hash`),
  Webflow, Squarespace and Framer assign asset IDs on upload. Never fabricate one.
  Emit placeholders + an upload order; the user drags images in.
- **Most builders have no write API for page content.** The last step is usually
  paste-and-upload by the user, or driving the editor through the browser while
  the user is signed in. Never sign in on their behalf. Do not promise one-click.
- **Figma access is per account.** A Figma link that opens in the user's browser
  can still 403 for the API — the `?t=` share token does not authorize the MCP.
  Fix: link sharing → "Anyone with the link · can view", or reconnect the Figma
  MCP to the account that owns the file. Fallback: exported frames in the folder.
- **`.fig` files are not readable offline.** Always ask for the cloud URL.
- **Check it is the user's work.** If the file or folder is named for another
  studio or looks like a template/community file, ask before writing it up.
- **Heavy images.** Builders usually serve originals. Anything over ~4000px or
  ~4MB should be downscaled before upload; the script flags these.

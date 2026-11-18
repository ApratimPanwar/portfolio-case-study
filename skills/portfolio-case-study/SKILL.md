---
name: portfolio-case-study
description: Find finished design projects on disk and in Figma, pull artwork out of Illustrator (.ai) source files, write them up as portfolio case studies in the portfolio's own house style, and deploy them to the user's site - Framer (Server API), Webflow (Data API), a custom/static or Claude-built site (repo edit + build + push), Cargo (browser-assisted), or paste-ready for anything else. Use when someone wants to add a project to their portfolio, write up a finished project, clear a case-study backlog, find projects they never published, set up a repeatable case-study format, or publish a case study to their website.
---

# Portfolio case study

Explain the format once; every new project starts where the last one ended. The
rules live in a file next to the work, not in a prompt someone has to remember.

```
DISCOVER  folders + Figma         -> candidate projects   (user picks)
LEARN     existing portfolio      -> house-rules.md       (once per portfolio)
BUILD     project + house rules   -> case.json + images   (platform-neutral)
DEPLOY    case.json               -> the user's site      (staged, user approves going live)
```

Run whichever stages are needed. A user with a folder in hand skips DISCOVER. A
user with `house-rules.md` skips LEARN. BUILD never runs without house rules: if
there are none, run LEARN first, or say plainly that you are using defaults.

Work directory per project: `<portfolio root>/case-studies/<slug>/` holding
`case.json`, `images/` and `assets.json`. Ask if there is no obvious root.

---

## DISCOVER - find the projects

1. **Folders.** `python scripts/find_projects.py [roots...]` ranks folders that look
   like design projects (images + source files + Figma links + process PDFs) and
   lists any Figma links found in text files inside them. Default roots: Desktop,
   Documents, Downloads, Pictures. If the user names a place, scan only that.
2. **Figma.** In order of preference:
   - links found by `find_projects.py` or given by the user;
   - `FIGMA_TOKEN=... python scripts/figma_list.py <team_id> --match <words>` if the
     user has a token with `projects:read` (often unavailable; a 403 is expected);
   - ask the user for the URLs.
   Check each link with the Figma MCP `get_metadata` before relying on it.
3. **Present a short list**: path, image count, source files, Figma links, last
   modified. The user picks. Do not open, read or describe folders they did not
   pick. Scans surface personal folders too; keep the list to likely projects and
   never comment on the rest.

## LEARN - write down the house rules

Inputs, any one: the live portfolio URL (preferred), exported pages/screenshots,
a template to remix, or an interview (then say the rules are invented, not learned).

Follow `references/learning-rules.md`. Fill `templates/house-rules.template.md`,
save as `<portfolio root>/house-rules.md`. Before saving, show the user the rules
**and the inconsistencies you found**; they decide what is a rule and what is a
mistake, and whether to keep the current voice or an improved one.

Also record the **platform** and how case studies are stored there (CMS collection
and field names, repo content folder and frontmatter, or block markup). DEPLOY
reads this.

## BUILD - make one case study

Inputs (ask for anything missing, never guess):
- the project folder; Figma URLs (optional); a supporting link (optional);
- **notes**: raw is right. A pasted voice-note transcript is ideal: who the client
  was, what they asked for, what changed and why. Do not ask the user to tidy it.

Steps:
1. Load `house-rules.md`.
2. **Source files.** If the folder has `.ai` files, pull the artboards out
   (`references/source-files.md`): ask which version is the shipped one, then
   `python scripts/extract_ai.py <file.ai> <work>/source`. Use the Illustrator
   route (`scripts/illustrator/`) if a file was saved without PDF content, or
   when artboard names, fonts or link status matter. Tell the user first; it
   opens Illustrator.
3. `python scripts/collect_assets.py <folder> [<work>/source] --columns <N>
   [--platform cargo] --out <work>/assets.json`. Reorder for the story (lead
   image, context, process, detail, final application) by editing each item's
   `order`; drop images that do not belong (drafts, dielines, duplicates).
4. Read Figma: `get_metadata` for the page/frame tree, `get_screenshot` on the
   frames that matter, `get_design_context` only for exact values worth writing
   about. Figma explains what was designed; the folder supplies the images.
5. Extract the story before writing: client and problem, constraint, what you
   did, what you rejected and why, what shipped, evidence. Mark gaps. Ask about
   gaps that matter; leave the rest out. Source files add facts (variant count,
   formats, typefaces), not story.
6. Write to house rules; `references/writing-rules.md` covers anything they don't.
7. `python scripts/prepare_images.py <work>/assets.json <work>/images --prefix <slug>`
   (downscales, strips EXIF/GPS, numbers files in display order).
8. Write `<work>/case.json` per `references/case-schema.md`.
9. Show the user the copy, the image order, and any gaps or rules you broke on
   purpose. Revise until they are happy, then DEPLOY.

## DEPLOY - put it on the site

Follow `references/deploy.md` for the platform recorded in house rules. Every
adapter climbs the same ladder: prepare -> draft -> preview the user sees ->
**user says yes** -> live.

- Custom / static / Claude-built site: edit the repo, build, preview locally,
  then commit and push on a yes.
- Framer: `scripts/framer/deploy.mjs` (dry run, draft, preview, production).
- Webflow: Data API, staged item, publish on a yes.
- Cargo and builders without an API: browser-assisted in the user's signed-in
  Chrome, or paste-ready output with an upload order.

## Getting better over time

When the user corrects output ("captions never end with a full stop", "lead with
the outcome"), offer to add it to `house-rules.md` under the corrections log. Fix
it once and it stays fixed.

---

## Gotchas

- **Going live is the user's call, every time.** Publishing, deploying to
  production, pushing to a branch that auto-deploys, and pressing Publish in a
  builder all need an explicit yes in chat for this specific case study.
- **Secrets stay in the environment.** `FRAMER_API_KEY`, `WEBFLOW_TOKEN`,
  `FIGMA_TOKEN` are set by the user; never ask for them in chat, print them, or
  write them into files that could be committed.
- **Never sign in for the user.** Browser-assisted deploys start with the user
  already signed in.
- **No made-up facts.** No metrics, quotes, timelines, team sizes or results that
  are not in the notes.
- **Learning is not copying mistakes.** Typos, one-off layouts and weak copy go in
  "Observed issues", not in the rules.
- **Builders mint their own image IDs** (Cargo `media-item hash`, Webflow/Framer
  asset IDs). Upload through the builder or its API; never fabricate an ID.
- **Figma access is per account.** A link that opens in the user's browser can
  still 403 for the MCP; the `?t=` share token does not authorize the API. Fix:
  share as "Anyone with the link: can view", or connect the MCP to the owning
  account. Fallback: exported frames in the folder.
- **`.fig` files cannot be read offline.** Ask for the cloud URL.
- **`.ai` files are not all artwork.** Some are SVGs renamed `.ai`; some were
  saved without PDF content and show only Illustrator's placeholder page. Use
  `extract_ai.py`'s verdict, not the extension.
- **Driving Illustrator is visible and slow-ish.** It opens on the user's
  screen. Say so before running it, and never save over their files.
- **Source files carry private details.** Packaging and print text often holds
  phone numbers, emails, addresses and licence numbers. Use extracted text to
  understand the project; never paste those details into a case study.
- **Check it is the user's work.** Files named for another studio, templates and
  community files: ask before writing them up.
- **Ship prepared images only.** Originals are often 8000px+ and carry GPS data;
  `prepare_images.py` fixes both. Never upload from the original folder.
- **Discovery output is private.** Folder names can reveal unrelated personal
  material. Show only likely projects; don't open or describe anything unpicked.

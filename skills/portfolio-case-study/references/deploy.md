# DEPLOY — getting case.json onto the site

Pick the adapter for the user's platform. Every adapter follows the same ladder,
and every rung that changes the public site needs the user's explicit yes in chat:

```
prepare  ->  stage / draft  ->  preview the user looks at  ->  [user says yes]  ->  live
```

Never skip from draft to live in one step. Never treat a yes for one project, or
an earlier session, as a yes for this one.

| Platform | Route | Automation |
|---|---|---|
| Custom / static site (Astro, Next, Hugo, 11ty, Jekyll, plain HTML, Claude-built) | edit the repo, build, push | full |
| Framer | `scripts/framer/deploy.mjs` (Framer Server API) | full, staged |
| Webflow | Webflow Data API v2 | full, staged (needs token) |
| Cargo | drive the editor in the user's signed-in Chrome | assisted |
| Squarespace, Wix, others with no write API | browser-assisted or paste-ready | assisted / manual |
| Notion, Behance, Dribbble, LinkedIn | paste-ready content + image order | manual |

---

## Custom / static site

The only platform where Claude can do everything. Applies to any site that lives
in a git repo, including sites Claude built.

1. **Detect the stack.** Look for `astro.config.*`, `next.config.*`, `.eleventy.*`,
   `hugo.toml`/`config.toml`, `_config.yml` (Jekyll), `gatsby-config.*`,
   `svelte.config.*`, or plain `index.html`. Read `package.json` scripts.
2. **Find an existing case study** in the repo and treat it as the template:
   content folder (`src/content/projects/`, `content/work/`, `_posts/`,
   `projects/*.html`…), frontmatter keys, image folder and how images are
   referenced. Copy its conventions exactly; do not invent new keys.
3. **Write the entry** from case.json: frontmatter from the shared fields, body
   from `body_md` (or render to the site's HTML if it is plain HTML). Copy
   prepared images into the site's asset folder.
4. **Index/listing:** if projects are listed by hand (plain HTML, hard-coded
   arrays), add the card/link. If listed from a content collection, nothing to do.
5. **Build and preview.** Run the project's build. Fix errors you caused. Start the
   dev server (preview tools / `.claude/launch.json`) and screenshot the new page
   and the listing, desktop and mobile width. Show the user.
6. **Ship, after a yes.** Work on a branch, commit, and push. If the host deploys
   from the main branch (Vercel, Netlify, Cloudflare Pages, GitHub Pages), say
   that merging/pushing to it publishes, and ask before doing it. Prefer a PR so
   the host builds a preview deployment first.

## Framer — `scripts/framer/deploy.mjs`

Uses the Framer Server API (`framer-api`, open beta, Node >= 22). Case studies
live in a CMS collection; the script maps case.json onto its fields.

Setup (once): user creates an API key in **Site Settings > General**, and sets it
as `FRAMER_API_KEY` in their own environment. Never ask them to paste the key into
chat; never write it to a file in the repo. `npm install` in `scripts/framer/`.

```
node deploy.mjs <work>/case.json --project <framer project url>                      # list collections
node deploy.mjs <work>/case.json --project <url> --collection "Projects"              # dry run: field mapping
node deploy.mjs <work>/case.json --project <url> --collection "Projects" --write      # images + DRAFT item
node deploy.mjs <work>/case.json --project <url> --collection "Projects" --write --live-item --publish   # PREVIEW
node deploy.mjs --project <url> --production <deploymentId>                           # promote, after a yes
```

- Show the user the dry-run mapping before `--write`. If a field maps wrongly or
  a value has no field, write a `map.json` (`{"Framer field": "case_key" | null}`)
  and pass `--map`.
- Re-running upserts by slug; it does not duplicate.
- `--write` alone is safe: drafts are excluded from publishing. The user can open
  the item in the Framer editor and edit it there.
- `--publish` makes a preview deployment, not production. `--production` promotes
  that exact deployment id, so what goes live is what the user reviewed.
- Gallery fields must be an array field with an image sub-field. Other field
  types (boolean, enum, color, references) are left unset; tell the user.
- If the user has Framer's own agent / Framer Skills, `house-rules.md` can also be
  pasted into a Framer Skill. The rules are platform-independent.

## Webflow — Data API v2

Only when the user has created a site API token with CMS read/write scope and set
it as `WEBFLOW_TOKEN` in their environment. Otherwise use paste-ready fields.

- Base `https://api.webflow.com/v2`, header `Authorization: Bearer $WEBFLOW_TOKEN`.
- Get the collection (`GET /collections/{collection_id}`) to read field slugs and
  types; map case.json onto them and show the mapping first.
- `POST /collections/{collection_id}/items` creates a **staged draft**. That is the
  default rung. Rich text fields take simple HTML (convert `body_md`).
- Images need a public URL Webflow can fetch, or an upload through Webflow's
  Assets API. Check the current field-format docs before the first write.
- `POST /collections/{collection_id}/items/publish` with the item id publishes it,
  after the user has reviewed the draft and said yes.

## Cargo — browser-assisted

Cargo has no content API. Route: the user's own signed-in Chrome, through the
Claude in Chrome tools. Cargo keeps edits as an unpublished draft until Publish is
pressed, which gives a natural review step.

1. Ask the user to open their site's editor in Chrome and sign in themselves.
   Never type their password.
2. Read the existing project block's markup (code view) and match it; LEARN
   should already have recorded it in house-rules.md.
3. Add the new block: usually duplicate an existing project block, then replace
   its contents. Upload the prepared images into the gallery **in case.json order**
   with the file-upload tool; Cargo assigns the `media-item hash` values.
4. Paste the text column HTML (from `body_md`, house-rules markup) in code view.
   Never write or edit `hash` attributes by hand.
5. Screenshot the result, show the user. Pressing **Publish** is an irreversible
   public action: the user does it, or says yes to you doing it.

If the browser tools are not available: hand over the image order and the
paste-ready HTML with `hash="REPLACE_ON_UPLOAD"` placeholders.

## Squarespace / Wix / anything without a write API

Same pattern as Cargo when the user is signed in and wants help: browser-assisted,
draft first, user publishes. Otherwise: per-block text in page order, plus the
image order.

## Notion / Behance / Dribbble / LinkedIn

Produce the content (Markdown for Notion; title, plain paragraphs, tags and image
order for the others). Do not post on the user's behalf.

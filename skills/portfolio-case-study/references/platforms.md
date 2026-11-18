# Platform output

Pick the section for the user's platform. If the platform isn't listed, emit
clean semantic HTML + a Markdown copy, and the upload order.

Always: **images go in by the user's hand or by a real asset pipeline, never by a
fabricated ID.** Read the live markup in LEARN to confirm details below — builders
change their internals.

## Cargo (cargo.site)

- Pages are HTML with Cargo custom elements: `<column-set>`, `<column-unit span>`,
  `<gallery-columnized>`, `<media-item hash=… slot=…>`.
- `hash` is minted on upload. Emit `hash="REPLACE_ON_UPLOAD"` placeholders.
- Gallery slots: `column-<c>-slot-<n>`, `n` a running index with no gaps.
  `columnized-span="2"` for wide images. `collect_assets.py --platform cargo`
  emits these.
- No content API. Handoff: user drags images into the gallery in your order,
  then pastes the text HTML into the block's code view.

## Framer

- Case studies usually live in a **CMS collection** (one item per project) with a
  detail-page template. Find the collection fields in LEARN.
- Emit one value per CMS field (title, slug, summary, body as rich text, cover,
  gallery, link). Rich-text body: plain paragraphs and headings only.
- If the user has Framer's own agent/Skills, the house-rules file can be pasted
  into a Framer Skill as-is — the rules are platform-independent.
- Images: user uploads into the CMS item fields.

## Webflow

- Also CMS-collection based. Map to the collection's field slugs from LEARN.
- Emit field values; rich-text as simple HTML (`<p>`, `<h3>`, `<ul>`, `<figure>`).
- Webflow has a CMS Data API, but using it needs a site token the user must
  create — only go that route if they explicitly set it up. Default to
  paste-ready fields.

## Squarespace

- No content API for pages. Emit text per block (heading, body, caption) in page
  order, plus the image order for gallery blocks. User builds the blocks.

## Notion

- Emit Markdown — Notion converts it on paste (headings, paragraphs, lists,
  dividers). Images: user drags in, or external URLs if they're hosted.

## Static site / Markdown (Astro, Next, Hugo, Jekyll, 11ty…)

- Look at an existing case-study file in their repo and copy its frontmatter
  keys exactly.
- Copy images into the repo's asset folder (downscaled per `[!heavy]` flags),
  with real paths in the Markdown. This is the only platform where you can
  finish the job end-to-end — say so.

## Behance / Dribbble / LinkedIn

- Long-form text in plain paragraphs, short title, tags list, image order.
  These are publishing destinations — do not post; hand the user the content.

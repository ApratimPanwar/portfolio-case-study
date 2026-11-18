# case.json — the platform-neutral case study

BUILD writes this. Every DEPLOY adapter reads it. Writing happens once; only the
last mile differs per platform. Save it next to the prepared images:
`<work_dir>/case.json`, with images in `<work_dir>/images/`.

```json
{
  "slug": "acme-coffee-identity",
  "title": "Brand Identity for Acme Coffee",
  "client": "Acme Coffee",
  "year": 2025,
  "role": "Brand identity, guidelines",
  "summary": "One sentence. Used for cards, meta description, CMS excerpt fields.",
  "body_md": "Paragraph one.\n\nParagraph two.\n\n## Optional heading\n\nParagraph three.",
  "images_dir": "/abs/path/to/work_dir/images",
  "cover": "acme-coffee-identity-01.jpg",
  "images": [
    { "file": "acme-coffee-identity-01.jpg", "alt": "Logo on a kraft paper cup", "caption": "", "span": 1 },
    { "file": "acme-coffee-identity-02.jpg", "alt": "Shopfront signage at dusk", "caption": "", "span": 2 }
  ],
  "link": { "label": "Detailed Document view ( Process + Research ) ->", "url": "https://..." },
  "tags": ["branding"],
  "extra": { "cargo": { "letter": "E" } }
}
```

## Rules

- `slug`: lowercase, hyphenated, unique on the site. Adapters upsert by slug, so
  re-running a deploy updates the same entry rather than duplicating it.
- `body_md`: Markdown, paragraphs and `##`/`###` headings, links, simple lists.
  No raw HTML, no images inline. Adapters convert it (Framer accepts Markdown
  directly; static sites use it as-is; Cargo/Webflow get simple HTML).
- `images`: in display order. `file` names refer to `images_dir`, produced by
  `prepare_images.py` (downscaled, metadata stripped). Never point at originals.
- `alt`: required, literal description. `caption`: optional, house rules decide.
- `span`: 1 or 2. Only grid-based layouts use it.
- `link`: optional; `null` when there is no real destination.
- `extra`: per-platform values that don't belong in the shared fields.
- Omit unknown fields rather than inventing values (no guessed `year`, no
  guessed `role`).

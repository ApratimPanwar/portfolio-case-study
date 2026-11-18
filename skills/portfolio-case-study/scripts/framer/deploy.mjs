#!/usr/bin/env node
// Deploy a case.json to a Framer CMS collection via the Framer Server API.
//
// Staged on purpose. Each stage needs its own flag, so nothing goes live by accident:
//
//   1. node deploy.mjs case.json --project <url>                      dry run: list collections / show field mapping
//   2. ... --collection "Projects" --write                            upload images, upsert item as a DRAFT
//   3. ... --collection "Projects" --write --live-item --publish      make the item live, publish a PREVIEW
//   4. node deploy.mjs --project <url> --production <deploymentId>    promote that exact preview to production
//
// Auth: FRAMER_API_KEY env var (Site Settings > General > API keys). Never pass it as an argument.
// Optional: --map map.json  {"Framer field name": "case_key" | null}  overrides auto-mapping.
//
// Setup once: npm install  (in this folder; Node >= 22)

import { readFileSync, existsSync } from "node:fs";
import { join, extname, basename, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const args = process.argv.slice(2);
const VALUED = new Set(["--project", "--collection", "--map", "--production"]);
const flag = (n) => args.includes(n);
const opt = (n) => {
  const i = args.indexOf(n);
  return i >= 0 ? args[i + 1] : undefined;
};
const die = (m) => {
  console.error(`error: ${m}`);
  process.exit(1);
};

const positional = args.filter((a, i) => !a.startsWith("--") && !VALUED.has(args[i - 1]));
const casePath = positional[0];
const project = opt("--project") ?? process.env.FRAMER_PROJECT_URL;
const productionId = opt("--production");

if (!project) die("--project <framer project url> (or FRAMER_PROJECT_URL) is required");
if (!process.env.FRAMER_API_KEY) die("set FRAMER_API_KEY (Framer > Site Settings > General > API keys)");
if (!productionId && !casePath) die("pass a case.json, or --production <deploymentId>");
if (flag("--publish") && !flag("--write")) die("--publish needs --write in the same run");
if (productionId && casePath) die("--production promotes an existing preview; run it on its own");

let connect;
try {
  ({ connect } = await import("framer-api"));
} catch {
  die(`framer-api not installed. Run "npm install" in ${dirname(fileURLToPath(import.meta.url))}`);
}

// Framer field name (lowercased) -> case.json key. Type compatibility is checked via FITS.
const NAMES = {
  title: ["title", "name", "project", "project name", "heading"],
  body_md: ["body", "content", "case study", "story", "text", "long description", "article"],
  summary: ["summary", "excerpt", "intro", "subtitle", "tagline", "short description", "description"],
  client: ["client", "company", "brand", "customer"],
  year: ["year", "date", "published", "completed"],
  role: ["role", "services", "discipline", "category", "scope"],
  cover: ["cover", "thumbnail", "image", "hero", "main image", "featured image", "cover image"],
  images: ["gallery", "images", "photos", "media", "slides"],
  link: ["link", "url", "external link", "document", "website", "live site", "case study link"],
  tags: ["tags", "keywords"],
};
const FITS = {
  title: ["string"],
  body_md: ["formattedText", "string"],
  summary: ["string", "formattedText"],
  client: ["string"],
  year: ["number", "date", "string"],
  role: ["string"],
  cover: ["image"],
  images: ["array"],
  link: ["link", "string"],
  tags: ["string"],
};
const MIME = {
  ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
  ".webp": "image/webp", ".gif": "image/gif", ".avif": "image/avif",
};

function planMapping(fields, override) {
  const used = new Set();
  return fields.map((f) => {
    let key = null;
    if (override && Object.hasOwn(override, f.name)) {
      key = override[f.name];
    } else {
      const lname = f.name.toLowerCase().trim();
      for (const [k, names] of Object.entries(NAMES)) {
        if (!used.has(k) && names.includes(lname) && FITS[k].includes(f.type)) {
          key = k;
          break;
        }
      }
    }
    if (key) used.add(key);
    return { field: f, key };
  });
}

function imagePath(c, file) {
  const p = join(c.images_dir, file);
  if (!existsSync(p)) die(`image not found: ${p}`);
  const mime = MIME[extname(p).toLowerCase()];
  if (!mime) die(`unsupported image type for Framer: ${p}`);
  return { p, mime };
}

async function upload(framer, c, file, cache) {
  if (cache.has(file)) return cache.get(file);
  const { p, mime } = imagePath(c, file);
  const bytes = new Uint8Array(readFileSync(p));
  const asset = await framer.uploadImage({ image: { bytes, mimeType: mime }, name: basename(p) });
  cache.set(file, asset.url);
  console.log(`  uploaded ${file}`);
  return asset.url;
}

async function entryFor(framer, c, field, key, cache) {
  const v = c[key];
  const altOf = (file) => c.images?.find((i) => i.file === file)?.alt ?? "";
  switch (key) {
    case "cover": {
      const file = c.cover ?? c.images?.[0]?.file;
      if (!file) return undefined;
      return { type: "image", value: await upload(framer, c, file, cache), alt: altOf(file) };
    }
    case "images": {
      const nested = field.fields?.find((f) => f.type === "image");
      if (!nested) {
        console.warn(`  skip "${field.name}": gallery field has no image sub-field`);
        return undefined;
      }
      const value = [];
      for (const img of c.images ?? []) {
        const url = await upload(framer, c, img.file, cache);
        value.push({ fieldData: { [nested.id]: { type: "image", value: url, alt: img.alt ?? "" } } });
      }
      return { type: "array", value };
    }
    case "link":
      if (!c.link?.url) return undefined;
      return field.type === "link"
        ? { type: "link", value: c.link.url }
        : { type: "string", value: c.link.url };
    case "tags":
      return v?.length ? { type: "string", value: v.join(", ") } : undefined;
    case "year":
      if (v == null) return undefined;
      if (field.type === "number") return { type: "number", value: Number(v) };
      if (field.type === "date") return { type: "date", value: `${v}-01-01T00:00:00.000Z` };
      return { type: "string", value: String(v) };
    default:
      if (v == null || v === "") return undefined;
      if (field.type === "formattedText") {
        return { type: "formattedText", value: String(v), contentType: "markdown" };
      }
      return { type: "string", value: String(v) };
  }
}

const framer = await connect(project, process.env.FRAMER_API_KEY);
try {
  // Stage 4: promote a specific, already-reviewed preview. Nothing else happens in this run.
  if (productionId) {
    const hosts = await framer.deploy(productionId);
    console.log(`deployed ${productionId} to production:`);
    for (const h of hosts) console.log(`  https://${h.hostname}  (${h.type}${h.isPrimary ? ", primary" : ""})`);
  } else {
    const c = JSON.parse(readFileSync(casePath, "utf8"));
    if (!c.slug || !c.title) die("case.json needs at least slug and title");
    c.images_dir = resolve(dirname(resolve(casePath)), c.images_dir ?? "images");

    const collections = await framer.getCollections();
    const wanted = opt("--collection");
    const collection = wanted && collections.find((x) => x.name.toLowerCase() === wanted.toLowerCase());
    if (!collection) {
      console.log(wanted ? `no collection named "${wanted}". Available:` : "collections in this project:");
      for (const x of collections) console.log(`  - ${x.name}`);
      console.log('\nre-run with --collection "<name>"');
      process.exitCode = wanted ? 1 : 0;
    } else {
      const override = opt("--map") ? JSON.parse(readFileSync(opt("--map"), "utf8")) : null;
      const plan = planMapping(await collection.getFields(), override);

      console.log(`\ncollection "${collection.name}" | slug "${c.slug}"\n`);
      for (const { field, key } of plan) {
        console.log(`  ${field.name.padEnd(26)} ${String(field.type).padEnd(14)} <- ${key ?? "(not set)"}`);
      }
      const unplaced = Object.keys(FITS).filter((k) => c[k] != null && !plan.some((p) => p.key === k));
      if (unplaced.length) console.log(`\n  case.json values with no field: ${unplaced.join(", ")} (use --map)`);

      // Check every image exists before touching anything remote.
      for (const img of c.images ?? []) imagePath(c, img.file);
      if (c.cover) imagePath(c, c.cover);

      const existing = (await collection.getItems()).find((i) => i.slug === c.slug);
      const live = flag("--live-item");
      console.log(`\n  ${existing ? "UPDATE existing item" : "CREATE new item"} | ${live ? "live (not draft)" : "draft"}`);

      if (!flag("--write")) {
        console.log("\ndry run: nothing written. Add --write to upload images and save the item as a draft.");
      } else {
        const cache = new Map();
        const fieldData = {};
        for (const { field, key } of plan) {
          if (!key) continue;
          const e = await entryFor(framer, c, field, key, cache);
          if (e) fieldData[field.id] = e;
        }
        const item = { slug: c.slug, fieldData, draft: !live };
        await collection.addItems([existing ? { ...item, id: existing.id } : item]);
        console.log(`\nsaved "${c.title}" (${live ? "live item" : "draft, excluded from publishing"})`);

        if (flag("--publish")) {
          if (!live) console.log("note: the item is a draft, so this preview will not include it. Use --live-item.");
          const result = await framer.publish();
          console.log(`\npreview published. deployment id: ${result.deployment.id}`);
          for (const h of result.hostnames ?? []) console.log(`  https://${h.hostname}  (${h.type})`);
          console.log("\nreview it, then promote this exact preview with:");
          console.log(`  node deploy.mjs --project "${project}" --production ${result.deployment.id}`);
        }
      }
    }
  }
} finally {
  await framer.disconnect();
}

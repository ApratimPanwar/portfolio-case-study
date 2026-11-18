#!/usr/bin/env python3
"""List Figma files in a team via the REST API (optional discovery path).

Usage:
    FIGMA_TOKEN=... python figma_list.py <team_id> [--match words] [--json out.json]

team_id: the number after /team/ in a Figma team URL
         (https://www.figma.com/files/team/<team_id>/...).

Needs a personal access token with the projects:read scope. Figma has been
inconsistent about offering that scope on new tokens; if this returns 403,
use the other discovery paths (links found in folders, or ask the user).
The token is read from the environment and never printed.
"""
import argparse, json, os, sys, urllib.request, urllib.error

API = "https://api.figma.com"


def get(path, token):
    req = urllib.request.Request(API + path, headers={"X-Figma-Token": token})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")[:300]
        if e.code == 403:
            sys.exit(f"403 from {path}: token lacks access or the projects:read scope.\n"
                     f"Fall back to Figma links found in folders, or ask the user for URLs.\n{body}")
        if e.code == 404:
            sys.exit(f"404 from {path}: wrong team id, or no access to that team.")
        if e.code == 429:
            sys.exit("429: Figma rate limit. Wait and retry.")
        sys.exit(f"HTTP {e.code} from {path}: {body}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("team_id")
    ap.add_argument("--match", nargs="*", default=[],
                    help="only files whose name contains any of these words")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    token = os.environ.get("FIGMA_TOKEN")
    if not token:
        sys.exit("set FIGMA_TOKEN (Figma > Settings > Security > Personal access tokens)")

    words = [w.lower() for w in a.match]
    projects = get(f"/v1/teams/{a.team_id}/projects", token).get("projects", [])
    rows = []
    for p in projects:
        for f in get(f"/v1/projects/{p['id']}/files", token).get("files", []):
            if words and not any(w in f["name"].lower() for w in words):
                continue
            rows.append({"project": p["name"], "name": f["name"], "key": f["key"],
                         "modified": f.get("last_modified", ""),
                         "url": f"https://www.figma.com/design/{f['key']}"})
    rows.sort(key=lambda r: r["modified"], reverse=True)

    print(f"\n{len(rows)} file(s) in {len(projects)} project(s)\n")
    for r in rows:
        print(f"{r['modified'][:10]}  {r['project'][:22]:<22}  {r['name'][:40]:<40}  {r['url']}")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(rows, fh, indent=2)
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    main()

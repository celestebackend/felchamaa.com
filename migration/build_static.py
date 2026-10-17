#!/usr/bin/env python3
"""Create a self-contained static copy of felchamaa.com in docs/."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BASE = "https://felchamaa.com"


def fetch_json(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "felchamaa-static-migration/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "felchamaa-static-migration/1.0"})
    with urllib.request.urlopen(req, timeout=120) as response:
        destination.write_bytes(response.read())


def clean_html(path: Path, canonical: str) -> None:
    text = path.read_text(encoding="utf-8")

    # Use stable asset names that work on GitHub Pages. wget otherwise stores
    # WordPress query strings as literal filename characters.
    replacements = {
        "main.min.css%3Fver=4.14.0.css": "main.min.css",
        "menu-animation.min.css%3Fver=4.14.0.css": "menu-animation.min.css",
        "frontend.min.js%3Fver=4.14.0": "frontend.min.js",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove WordPress and Hostinger discovery/telemetry elements that will no
    # longer exist after the static site becomes authoritative.
    text = re.sub(r"\s*<link[^>]+(?:cdn-reach\.hostinger\.com|googletagmanager\.com)[^>]*>\s*", "\n", text)
    text = re.sub(r"\s*<link[^>]+(?:/feed/|/comments/feed/|wp-json|xmlrpc\.php)[^>]*>\s*", "\n", text)
    text = re.sub(r"\s*<link[^>]+rel=[\"']shortlink[\"'][^>]*>\s*", "\n", text)
    text = re.sub(r"\s*<script[^>]+id=[\"']hostinger-reach-embed-js[\"'][^>]*></script>\s*", "\n", text)
    text = re.sub(r"\s*<script[^>]+type=[\"']speculationrules[\"'][^>]*>.*?</script>\s*", "\n", text, flags=re.S)
    text = re.sub(r"\s*<script[^>]+id=[\"']wp-emoji-settings[\"'][^>]*>.*?</script>\s*", "\n", text, flags=re.S)
    text = re.sub(r"\s*<script type=[\"']module[\"']>\s*/\*! This file is auto-generated \*/.*?</script>\s*", "\n", text, flags=re.S)

    # wget makes canonical URLs relative. Restore the public production URL.
    text = re.sub(
        r"<link rel=[\"']canonical[\"'] href=[\"'][^\"']+[\"']\s*/?>",
        f'<link rel="canonical" href="{canonical}" />',
        text,
        count=1,
    )

    path.write_text(text, encoding="utf-8")


def main() -> None:
    pages = fetch_json(f"{BASE}/wp-json/wp/v2/pages?per_page=100&context=view")
    urls = [page["link"] for page in pages if page.get("status") == "publish"]
    if not urls:
        raise RuntimeError("WordPress returned no published pages")

    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)

    url_file = ROOT / "migration" / "site-urls.txt"
    url_file.write_text("\n".join(urls) + "\n", encoding="utf-8")
    subprocess.run(
        [
            "wget",
            f"--input-file={url_file}",
            "--page-requisites",
            "--convert-links",
            "--adjust-extension",
            "--restrict-file-names=unix",
            "--no-host-directories",
            f"--directory-prefix={DOCS}",
            "--timeout=45",
            "--tries=3",
            "--wait=0.1",
        ],
        check=True,
    )

    uploads = DOCS / "wp-content" / "uploads"
    required_assets = [
        "What-Remains-1982-2026.pdf",
        "cropped-elchamaa-logo.png",
        "cropped-square-logo-180x180.png",
        "cropped-square-logo-270x270.png",
        "felchamaa-2019-2025-og.jpg",
        "felchamaa-about-og.jpg",
        "felchamaa-home-og.jpg",
        "felchamaa-paintings-og.jpg",
    ]
    for name in required_assets:
        download(f"{BASE}/wp-content/uploads/{name}", uploads / name)

    theme = DOCS / "wp-content" / "themes" / "astra" / "assets"
    renames = {
        theme / "css" / "minified" / "main.min.css?ver=4.14.0.css": theme / "css" / "minified" / "main.min.css",
        theme / "css" / "minified" / "menu-animation.min.css?ver=4.14.0.css": theme / "css" / "minified" / "menu-animation.min.css",
        theme / "js" / "minified" / "frontend.min.js?ver=4.14.0": theme / "js" / "minified" / "frontend.min.js",
    }
    for source, target in renames.items():
        if not source.exists():
            raise FileNotFoundError(source)
        source.rename(target)

    by_path = {urlparse(page["link"]).path: page for page in pages}
    for html_path in DOCS.glob("**/index.html"):
        rel = html_path.relative_to(DOCS)
        public_path = "/" if rel == Path("index.html") else "/" + str(rel.parent).replace("\\", "/") + "/"
        if public_path not in by_path:
            raise RuntimeError(f"No WordPress page metadata for {public_path}")
        clean_html(html_path, BASE + public_path)

    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    (DOCS / "CNAME").write_text("felchamaa.com\n", encoding="utf-8")
    (DOCS / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: https://felchamaa.com/sitemap.xml\n",
        encoding="utf-8",
    )

    sitemap_urls = []
    for page in sorted(pages, key=lambda item: item["link"]):
        if page.get("status") != "publish":
            continue
        loc = page["link"]
        modified = page.get("modified_gmt", "")[:10]
        sitemap_urls.append(f"  <url><loc>{loc}</loc><lastmod>{modified}</lastmod></url>")
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(sitemap_urls) + "\n</urlset>\n"
    (DOCS / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    # GitHub Pages uses this for unknown URLs. It keeps the site's identity and
    # offers a direct way back without depending on WordPress.
    (DOCS / "404.html").write_text(
        """<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><meta name=\"robots\" content=\"noindex\"><title>Page not found | Fadi Elchamaa</title><style>body{margin:0;font:16px Arial,sans-serif;color:#242424;min-height:100vh;display:grid;place-items:center;text-align:center}a{color:inherit}main{padding:2rem}h1{font-size:1.25rem;font-weight:400}</style></head><body><main><h1>Page not found</h1><p><a href=\"/\">Fadi Elchamaa</a></p></main></body></html>\n""",
        encoding="utf-8",
    )

    manifest = {
        "source": BASE,
        "pages": len(urls),
        "files": sum(1 for path in DOCS.rglob("*") if path.is_file()),
        "bytes": sum(path.stat().st_size for path in DOCS.rglob("*") if path.is_file()),
    }
    (ROOT / "migration" / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()

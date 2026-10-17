#!/usr/bin/env python3
"""Fail if an HTML page refers to a missing local file."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1] / "docs"


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls: list[str] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for name in ("href", "src", "poster"):
            if values.get(name):
                self.urls.append(values[name])
        if values.get("srcset"):
            self.urls.extend(item.strip().split()[0] for item in values["srcset"].split(","))


missing = []
for page in ROOT.glob("**/*.html"):
    parser = References()
    parser.feed(page.read_text(encoding="utf-8"))
    for url in parser.urls:
        split = urlsplit(url)
        if split.scheme or split.netloc or not split.path or split.path.startswith("#"):
            continue
        target = ROOT / unquote(split.path.lstrip("/")) if split.path.startswith("/") else page.parent / unquote(split.path)
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            missing.append((str(page.relative_to(ROOT)), url))

if missing:
    for page, url in missing:
        print(f"MISSING {page}: {url}")
    raise SystemExit(1)

print(f"Verified {len(list(ROOT.glob('**/*.html')))} HTML files: no missing local references")

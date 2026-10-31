#!/usr/bin/env python3
"""Check local href/src targets and HTML anchors in a generated Pages site."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("name"):
            self.ids.add(attrs["name"])
        for attribute in ("href", "src"):
            if attrs.get(attribute):
                self.links.append(attrs[attribute])

    handle_startendtag = handle_starttag


def check_site(directory, base_path):
    root = directory.resolve()
    pages = {
        path.resolve(): Page(path.read_text(encoding="utf-8"))
        for path in root.rglob("*.html")
    }
    errors = []
    if root / "index.html" not in pages:
        errors.append("Site must contain index.html")
    base_path = "/" + base_path.strip("/") if base_path.strip("/") else ""

    for source, page in sorted(pages.items()):
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            path = unquote(url.path)
            if path.startswith("/"):
                if base_path and not (path == base_path or path.startswith(base_path + "/")):
                    errors.append(f"{source.relative_to(root)}: outside base path: {link}")
                    continue
                target = root / path[len(base_path):].lstrip("/")
            elif path:
                target = source.parent / path
            else:
                target = source
            target = target.resolve()
            if not target.is_relative_to(root):
                errors.append(f"{source.relative_to(root)}: outside site: {link}")
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.is_file():
                errors.append(f"{source.relative_to(root)}: missing target: {link}")
                continue
            fragment = unquote(url.fragment)
            if fragment and target in pages and fragment not in pages[target].ids:
                errors.append(f"{source.relative_to(root)}: missing anchor: {link}")
    return len(pages), errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site_directory", type=Path)
    parser.add_argument("--base-path", default="/4os")
    args = parser.parse_args()
    count, errors = check_site(args.site_directory, args.base_path)
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print(f"Checked {count} HTML pages: internal links and anchors OK.")


if __name__ == "__main__":
    main()

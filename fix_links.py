#!/usr/bin/env python3

import os
import sys
from lxml import html
from urllib.parse import urlparse

if "-h" in sys.argv or "--help" in sys.argv:
    print("Usage: fix_internal_links.py <docpath>")
    sys.exit()

if len(sys.argv) > 1:
    docpath = os.path.abspath(os.sys.argv[1])
else:
    docpath = "Odin.docset/Contents/Resources/Documents"

reported = {}


def fix_ressource_link(depth, href):
    if not href.startswith("https://odin-lang.org"):
        return None

    path = os.path.basename(urlparse(href).path)

    return "".join(["../"] * depth) + "odin-org-res/" + path


def to_local_link(depth, current, href):
    if (href.startswith("http://") or href.startswith("https://")) and not (
        href.startswith("https://pkg.odin-lang.org/")
        or href.startswith("http://pkg.odin-lang.org/")
    ):
        # External link, don't touch
        return None

    href_path = urlparse(href).path.rstrip("/")

    if href_path.startswith("/"):
        pkg_path = os.path.join(docpath, href_path[1:])
    else:
        pkg_path = os.path.join(os.path.dirname(current), href_path)

    pkg_path = os.path.normpath(pkg_path)
    href_path = "".join(["../"] * depth) + os.path.relpath(pkg_path, docpath)
    assert len(href_path) > 0 and href_path[0] != "/"

    if os.path.isfile(pkg_path):
        return pkg_path, href_path

    elif os.path.isfile(pkg_path + ".html"):
        return pkg_path + ".html", href_path + ".html"

    elif os.path.isdir(pkg_path):
        if os.path.exists(pkg_path + "/index.html"):
            return pkg_path + "/index.html", href_path + "/index.html"

        if pkg_path not in reported:
            reported[pkg_path] = "is a directory"
        return None

    if pkg_path not in reported:
        reported[pkg_path] = "does not exist"
    return None


def process_page(depth, path):
    with open(path) as f:
        ast = html.fromstring(f.read())

    for link in ast.cssselect("script"):
        if "src" not in link.attrib:
            continue

        src = link.attrib["src"]

        res = fix_ressource_link(depth, src)
        if not res:
            continue

        link.attrib["src"] = res

    for link in ast.cssselect("link"):
        if "href" not in link.attrib:
            continue

        href = link.attrib["href"]

        res = fix_ressource_link(depth, href)
        if not res:
            continue

        link.attrib["href"] = res

    for link in ast.cssselect("a"):
        if "href" not in link.attrib:
            continue

        href = link.attrib["href"]

        res = to_local_link(depth, path, href)
        if not res:
            continue

        link_path, href = res

        link.attrib["href"] = href

    with open(path, "wb") as f:
        f.write(html.tostring(ast, pretty_print=True, encoding="utf-8"))


def process_tree(depth, target):
    for sub in os.listdir(target):
        if os.path.isdir(os.path.join(target, sub)):
            process_tree(depth + 1, os.path.join(target, sub))
        elif sub.endswith(".html"):
            print("Processing", os.path.join(target, sub))
            process_page(depth, os.path.join(target, sub))


process_tree(0, docpath)

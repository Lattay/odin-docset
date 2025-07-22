#!/usr/bin/env python3

import os, re, sqlite3
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.parse import urlparse

entity_to_type = {
    "pkg-Types": "Type",
    "pkg-Constants": "Constant",
    "pkg-Variables": "Variable",
    "pkg-Procedures": "Procedure",
    "pkg-Procedure Groups": "Procedure",
}

conn = sqlite3.connect("Odin.docset/Contents/Resources/docSet.dsidx")
cur = conn.cursor()

try:
    cur.execute("DROP TABLE searchIndex;")
except sqlite3.OperationalError:
    pass

cur.execute("CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);")
cur.execute("CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);")

docpath = "Odin.docset/Contents/Resources/Documents"

skipped = set()

def parse_packages(top_level_soup):
    current_directory = None
    for parent_pkg in top_level_soup.find_all("tr", {"class": "directory-pkg"}):
        pkg = parent_pkg.find("td", {"class": "pkg-name"})
        name = pkg.text.strip()
        if "directory-child" in parent_pkg["class"]:
            name = "{0}/{1}".format(current_directory, name)
        else:
            current_directory = name

        if not pkg.a:
            continue

        pkg_href = pkg.a.attrs["href"]
        href_path = urlparse(pkg_href).path.strip("/")
        if len(name) >= 1:
            pkg_path = os.path.join(docpath, href_path)
            if os.path.exists(pkg_path) and os.path.isfile(pkg_path):
                pass
            elif os.path.isdir(pkg_path):
                skipped.add((f"{pkg_path} is a dir", name, pkg_href))
                continue
            else:
                skipped.add((f"no path {pkg_path}", name, pkg_href))
                continue

            cur.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)", (name, "Package", href_path))
            print("package: %s, path: %s" % (name, pkg_path))

            pkg_page = open(pkg_path).read()
            pkg_soup = BeautifulSoup(pkg_page, features="lxml")

            current_type = ""
            for node in pkg_soup.find("section", {"class": "documentation"}):
                if node.name == "h2":
                    entity_type = node.attrs.get("id", "")
                    current_type = entity_to_type.get(entity_type, "")

                if node.name == "div":
                    if current_type == "":
                        continue

                    for entity in node.find_all("h3"):
                        entity_name = entity.attrs["id"]
                        pkg_path = urlparse(pkg_href).path.strip("/")
                        entity_href = f"{pkg_path}#{entity_name}"
                        prefixed_entity_name = "{0}.{1}".format(name, entity_name)
                        cur.execute("INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)", (prefixed_entity_name, current_type, entity_href))

page = open(os.path.join(docpath,"core.html")).read()
soup = BeautifulSoup(page, features="lxml")
parse_packages(soup)

page = open(os.path.join(docpath,"vendor.html")).read()
soup = BeautifulSoup(page, features="lxml")
parse_packages(soup)

page = open(os.path.join(docpath,"base.html")).read()
soup = BeautifulSoup(page, features="lxml")
parse_packages(soup)


conn.commit()
conn.close()

for reason, name, href in skipped:
    print(f"skipped: {name}, href: {href}, reason: {reason}")

#!/bin/bash

set -euo pipefail
root=$(dirname $(realpath $0))

if [[ ! -e pkg.odin-lang.org ]]
then
    wget --mirror \
        --page-requisites \
        --adjust-extension \
        --content-disposition \
        --convert-links \
        "https://pkg.odin-lang.org/"
fi

mkdir -p Odin.docset/Contents/Resources/Documents/odin-org-res
cp -R pkg.odin-lang.org/* Odin.docset/Contents/Resources/Documents/

pushd Odin.docset/Contents/Resources/Documents/odin-org-res
wget https://odin-lang.org/scss/custom.min.css
wget https://odin-lang.org/css/style.css
wget https://odin-lang.org/lib/highlight/styles/github-dark.min.css

wget https://odin-lang.org/lib/highlight/highlight.min.js
wget https://odin-lang.org/lib/bootstrap/js/bootstrap.min.js
wget https://odin-lang.org/js/script.js
popd

cp ${root}/icon.png Odin.docset/
cp ${root}/meta.json Odin.docset/
cp ${root}/Info.plist Odin.docset/Contents/

./fix_links.py
./generate_odin_docset.py

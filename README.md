# odin-docset
Odin docset generation for the odin pkgs to be used in Zeal / Dash / Velocity

## Setup

1. Download last version from [releases](https://github.com/drmargarido/odin-docset/releases) and
2. Copy the Odin.docset folder to your Zeal / Dash / Velocity docsets folder.
3. All done, it's ready to use!

## Generating the docset

Make sure you have `wget` as well as Python 3.
Then run these commands:
```sh
pip install bs4 lxml cssselect
./make_docset.sh
```

You can then copy the Odin.docset folder to your Zeal / Dash / Velocity docsets folder.

# Rebuilding RUH

The committed UFO is the editable production source. It contains curves, Unicode assignments, metrics, and the OpenType feature source. No image-generation account or network access is needed to rebuild fonts after installing the open-source dependencies.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
RUH_FONT_PYTHON=.venv/bin/python ./build.sh
```

Outputs are written to `fonts/ttf/RUH-Regular.ttf`, `fonts/otf/RUH-Regular.otf` and `fonts/webfonts/RUH-Regular.woff2`. The build uses fixed head timestamps and pinned dependencies. Compare SHA-256 values to `documentation/reproducible-build.json`.

A standard fontmake compatibility build is also available from the same UFO:

```sh
python3 -m pip install fontmake==3.12.1
fontmake -u sources/RUH.ufo -o ttf --output-dir fontmake-check
```

That command verifies the source is accepted by standard UFO/fontmake tooling. It is not expected to be byte-identical to the reviewed FontTools production build, whose metadata, hinting flags and table assembly are explicit in `sources/build_fonts.py`.

The TrueType font is not grid-hinted per glyph. It contains smart-dropout preparation and a gasp table enabling modern antialiasing flags. Real font rendering is reviewed at display sizes; it is not presented as a small-text face.

The owner authorized OFL 1.1 release. The 1.102 metadata identifies the verified public source repository, https://github.com/smelllikeruh/ruh-font. The exact uppercase family RUH requires a Google Fonts naming exception; applicable contributor agreement and catalog review remain pending.

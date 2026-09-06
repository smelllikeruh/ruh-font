#!/bin/sh
set -eu
project_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python_bin=${RUH_FONT_PYTHON:-python3}
"$python_bin" "$project_dir/sources/build_fonts.py" "$project_dir/fonts"

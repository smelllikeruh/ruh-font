#!/usr/bin/env python3
"""Check the licensed release outputs without changing any font or source file."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys

from fontTools.misc.fixedTools import floatToFixed
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parent.parent
STYLE = "Regular"
LICENSE_URL = "https://openfontlicense.org"
LICENSE_DESCRIPTION = (
    "This Font Software is licensed under the SIL Open Font License, Version 1.1. "
    "This license is available with a FAQ at: https://openfontlicense.org"
)
BRAND_CODEPOINTS = set(map(ord, "RŪḤ · Saint Noir · Fred Hampton Free Store"))
BRAND_CODEPOINTS.update(map(ord, "RU\u0304H\u0323"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def release_contract() -> tuple[str, str, str, dict[int, str], list[str]]:
    config = json.loads((ROOT / "sources" / "font-metadata.json").read_text(encoding="utf-8"))
    family = config["family"]
    basename = config["basename"]
    version = config["version"]
    names = config["names"]
    require(isinstance(family, str) and bool(family.strip()) and family == family.strip(),
            "JSON family must be a nonempty name without surrounding whitespace")
    require(isinstance(basename, str) and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]*", basename)),
            "JSON basename must be a valid font filename stem without a path or extension")
    require(isinstance(version, str) and re.fullmatch(r"\d+\.\d{3}", version),
            "JSON version must use the MAJOR.SIGNIFICANTMINORPATCH format")
    require(names["familyName"] == family and names["styleName"] == STYLE,
            "JSON name-table family must match the configured family and style must be Regular")
    require(names["psName"] == basename, "JSON PostScript name must match the output basename")
    require(names["fullName"] == f"{family} {STYLE}", "JSON full name must match family and style")
    require(names["version"] == f"Version {version}",
            "JSON name-table version disagrees with release version")
    require(version in names["uniqueFontIdentifier"],
            "JSON unique font identifier must contain the release version")
    require(names["licenseDescription"] == LICENSE_DESCRIPTION,
            "JSON license description must match the GF OFL 1.1 description")
    require(names["licenseInfoURL"] == LICENSE_URL,
            "JSON license URL must be https://openfontlicense.org")

    ofl_text = (ROOT / "OFL.txt").read_text(encoding="utf-8-sig")
    lines = ofl_text.splitlines()
    require(bool(lines), "OFL.txt is empty")
    require(lines[0] == names["copyright"],
            "OFL.txt first line and JSON copyright must be identical")
    require(bool(re.fullmatch(
        rf"Copyright \d{{4}}(?:-\d{{4}})? The {re.escape(family)} Project Authors \(https://[^\s<>]+\)",
        lines[0])), "Copyright must name the project authors and an HTTPS project URL without placeholders")
    require("SIL OPEN FONT LICENSE" in ofl_text and "Version 1.1" in ofl_text,
            "OFL.txt must include the OFL 1.1 license body")
    header = ofl_text.split("SIL OPEN FONT LICENSE", 1)[0]
    require(not re.search(r"\bwith Reserved Font Names?\b", header, re.IGNORECASE),
            "This release must not declare a Reserved Font Name")

    expected = {
        0: names["copyright"],
        1: family,
        2: STYLE,
        3: names["uniqueFontIdentifier"],
        4: f"{family} {STYLE}",
        5: f"Version {version}",
        6: basename,
        13: LICENSE_DESCRIPTION,
        14: LICENSE_URL,
    }
    warnings = []
    if family.isupper():
        warnings.append(
            f"The exact family name {family!r} is all capitals. Google Fonts naming "
            "review and an exception are required; a local release check does not "
            "establish approval. The checker preserves the configured name."
        )
    return family, basename, version, expected, warnings


def check_font(kind: str, path: Path, version: str,
               expected: dict[int, str]) -> tuple[dict, dict[int, str]]:
    require(path.is_file(), f"Missing release font: {path.relative_to(ROOT)}")
    with TTFont(path, lazy=False, recalcTimestamp=False) as font:
        font.ensureDecompiled()
        for name_id, value in expected.items():
            records = [record.toUnicode() for record in font["name"].names
                       if record.nameID == name_id]
            require(bool(records), f"Missing name ID {name_id}")
            require(set(records) == {value}, f"Incorrect or conflicting name ID {name_id}")

        require(floatToFixed(font["head"].fontRevision, 16)
                == floatToFixed(float(version), 16),
                "head.fontRevision disagrees with the JSON version")
        require(font["OS/2"].fsType == 0, "OFL fonts must allow installable embedding")
        require(font["OS/2"].usWeightClass == 400, "Regular style must have weight 400")
        require(font["post"].italicAngle == 0, "Regular style must not have an italic angle")

        if kind == "otf":
            require(font.sfntVersion == "OTTO" and "CFF " in font,
                    "OTF output must contain CFF outlines")
            top_dict = font["CFF "].cff.topDictIndex[0]
            require(top_dict.version == version, "CFF version disagrees with JSON version")
            require(top_dict.Notice == expected[0], "CFF Notice disagrees with copyright")
        else:
            require(font.sfntVersion == "\x00\x01\x00\x00" and "glyf" in font,
                    f"{kind} output must contain TrueType outlines")
        require(font.flavor == ("woff2" if kind == "woff2" else None),
                f"Unexpected container flavor for {kind}")

        cmap = font.getBestCmap() or {}
        glyph_names = set(font.getGlyphOrder())
        missing = sorted(cp for cp in BRAND_CODEPOINTS
                         if cmap.get(cp) in (None, ".notdef") or cmap[cp] not in glyph_names)
        require(not missing, "Missing brand characters: " + ", ".join(
            f"U+{cp:04X}" for cp in missing))
        return {
            "path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "encoded_characters": len(cmap),
            "glyphs": len(glyph_names),
            "status": "pass",
        }, cmap


def main() -> int:
    try:
        family, basename, version, expected, warnings = release_contract()
    except (OSError, KeyError, TypeError, ValueError) as error:
        print(json.dumps({"status": "fail", "error": str(error)}, indent=2))
        return 1

    results = []
    failures = []
    reference_cmap = None
    outputs = (
        ("ttf", ROOT / "fonts" / "ttf" / f"{basename}.ttf"),
        ("otf", ROOT / "fonts" / "otf" / f"{basename}.otf"),
        ("woff2", ROOT / "fonts" / "webfonts" / f"{basename}.woff2"),
    )
    for kind, path in outputs:
        try:
            result, cmap = check_font(kind, path, version, expected)
            if reference_cmap is None:
                reference_cmap = cmap
            require(cmap == reference_cmap, "Unicode cmap differs between release formats")
            results.append(result)
        except Exception as error:
            failures.append({"path": path.relative_to(ROOT).as_posix(), "error": str(error)})
    print(json.dumps({
        "status": "fail" if failures else "pass",
        "family": family,
        "basename": basename,
        "version": version,
        "files": results,
        "warnings": warnings,
        "failures": failures,
    }, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

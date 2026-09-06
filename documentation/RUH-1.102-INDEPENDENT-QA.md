# RUH 1.102 independent release QA

Checked 2026-09-06T09:09:04.516364+00:00. **Local release integrity passed; the Google Fonts binary profile has one unsuppressed failure.** No fonts, glyph sources, license text or metadata were changed by this QA run. The only existing source-repository file updated was `documentation/reproducible-build.json`. Earlier 1.100 and 1.101 reports are preserved.

## Rebuild, sanitizer and glyph continuity

A fresh temporary copy of the build inputs, with no preexisting font outputs, ran the unchanged `build.sh` under Python 3.12.8. Its exact dependencies were FontTools 4.64.0, defcon 0.12.2, Brotli 1.2.0 and Zopfli 0.4.3. All three native output hashes equal both the expected 1.102 hashes and the clean rebuild. OpenType Sanitizer 9.2.0 returned zero with successful sanitization for all three.

| Format | Native and rebuilt SHA-256 | Rebuild | OTS | Outline/layout comparison |
|---|---|---|---|---|
| TTF | `641d7b127c05881ded2256d55ce6701c6b2735ec9be429f28d296905c7b08a2a` | Pass | Pass | Unchanged |
| OTF | `ac7d8de3fb75a1829a51ddef62be198d49da6a908aa5c22768b0723db19c14df` | Pass | Pass | Unchanged |
| WOFF2 | `1c282abdf03abb1fe9de0222879f59d14fb199d18af033135f748c803a9e3fe6` | Pass | Pass | Unchanged |

The archived 1.100 binaries were verified against their recorded hashes before comparison. Each current format has 351 encoded codepoints and 365 glyphs. All 365 glyph drawings and glyph order match its corresponding archive; `cmap`, `hmtx`, `GSUB` and `GPOS` are byte-identical. Units per em and the checked horizontal-header/OS/2 vertical metrics also match. This confirms continuity of those glyph/layout structures, not a new visual usability test.

`check_release.py` returned zero. It parsed TTF, OTF and WOFF2, confirmed 1.102 version metadata, exact RUH / Regular naming, matching name-ID-0/OFL copyright, canonical OFL license description and URL, CFF notice/version, and the composed/decomposed RŪḤ brand characters. Its all-caps family-name review warning remains present.

## Full Google Fonts binary profile

FontBakery 1.1.0 is the current published version checked against the [official PyPI project page](https://pypi.org/project/fontbakery/). The complete default `googlefonts` profile ran on the exact release TTF with an unchanged copy of source `OFL.txt` beside it. No check IDs were excluded or selectively enabled. Network checks were enabled with a 20-second per-request timeout.

**236 executions: 112 PASS, 8 WARN, 8 INFO, 107 SKIP, 1 FAIL, 0 ERROR and 0 FATAL. Process exit status: 1.**

The sole failure is `googlefonts/family_name_compliance`, code `abbreviation`: the exact requested family name RUH requires review under the naming rules. It was neither renamed nor suppressed. FontBakery passing copyright, OFL body, OFL copyright, name license and name license-URL checks does not resolve that naming failure.

| Check | Result | Diagnostic code |
|---|---|---|
| `alt_caron` | WARN | decomposed-outline |
| `contour_count` | WARN | contour-count |
| `googlefonts/article/images` | WARN | lacks-article |
| `googlefonts/metadata/unreachable_subsetting` | WARN | unreachable-subsetting |
| `googlefonts/glyphsets/shape_languages` | WARN | warning-language-shaping |
| `googlefonts/family_name_compliance` | FAIL | abbreviation |
| `outline_colinear_vectors` | WARN | found-colinear-vectors |
| `outline_semi_vertical` | WARN | found-semi-vertical |
| `googlefonts/vendor_id` | WARN | unknown |

The outline and caron warnings remain candidates for type-design review. The language warning includes auxiliary orthography beyond the claimed Latin Core coverage; it does not establish full support for every inferred language. Subsetting must be reviewed during Google Fonts onboarding. The missing-article warning concerns the isolated binary fixture. No downstream `METADATA.pb`, description or article was fabricated, so conditional repository/metadata checks may skip. The vendor ID is not recognized by the tool; this does not prove a registration either way.

## Included evidence and limits

- [reproducible-build.json](reproducible-build.json): exact runtime, expected/rebuilt hashes, sanitizer and outline/layout equivalence results.
- [RUH-1.102-FontBakery-GoogleFonts.json](RUH-1.102-FontBakery-GoogleFonts.json): complete binary-profile results.
- [RUH-1.102-FontBakery-Summary.json](RUH-1.102-FontBakery-Summary.json): counts and outstanding issues.
- `sources/check_release.py` in the repository: reproducible release metadata validation.

This public copy links the evidence included in this repository. Machine-specific invocation paths and the owner's full archived comparison files remain in the separate complete Font Pack. Results and hashes are unchanged.

These are local macOS checks. The full Google Fonts binary profile ran on TTF; OTF and WOFF2 received independent parsing, OTS, hash and glyph/layout checks. Hosted Linux CI was not part of this local report; the repository's current Actions results are a separate record. Google Fonts listing, an accepted RUH naming exception and contributor/rights attestations remain external decisions, separate from these technical results.

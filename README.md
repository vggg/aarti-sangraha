# Aarti Sangraha

A printable booklet and a phone-friendly web page for six Marathi aartis — the Devanagari
verse, a syllable-by-syllable English pronunciation under every line, and a plain-English
meaning for each.

Made for families raising children outside Maharashtra, where the tune is remembered but the
script often isn't.

**Read the page:** https://vggg.github.io/aarti-sangraha/ — see [SETUP.md](SETUP.md)
**Print the booklet:** [`print/Aarti_Sangraha_A4_Booklet.pdf`](print/Aarti_Sangraha_A4_Booklet.pdf) — 5 A4 sheets, fold in half

| | |
|---|---|
| श्री गणपतीची आरती | सुखकर्ता दुःखहर्ता |
| श्री शंकराची आरती | लवथवती विक्राळा |
| श्री देवीची आरती | दुर्गे दुर्घट भारी |
| श्री दत्ताची आरती | त्रिगुणात्मक त्रैमूर्ति |
| घालीन लोटांगण | |
| मंत्रपुष्पांजली | |

## One source of truth

Everything here — three PDFs, the web page, the QR cards — is generated from
[`source/aarti_master.json`](source/aarti_master.json): 95 lines, each with a permanent ID,
the Devanagari, and its pronunciation.

That file is hashed. `build/build.py` recomputes the hash on every run and refuses to start
if it has moved, so no design change can quietly alter a verse. Changing the text means
changing the master and re-freezing the hash — there is no other path.

## The text is checked, not asserted

Ten photographs of a printed Aarti Sangrah edition were transcribed line by line at 3×
magnification. Where the printed edition and the standard published text disagree, the
standard text is used and the difference is recorded — all 27 of them, with reasons, in
[`notes/DIVERGENCES.md`](notes/DIVERGENCES.md). Some are substantive: that edition prints
`तोंड` where the standard has `सोंड`, and carries two broken Sanskrit readings in
Ghalin Lotangan that were corrected here.

Two acceptance tests run on every build:

- **`build/validate.py`** extracts the text layer back out of each generated PDF and asserts
  that all 95 Devanagari lines and all 95 Roman lines appear character for character. It also
  checks that no Devanagari character appears anywhere in the PDF that is not accounted for in
  the master, that page geometry is right, and that every font is embedded.
- **`build/check_imposition.py`** reads each half-sheet of the folded booklet separately and
  confirms it carries exactly the page that saddle-stitch order requires, with a character
  census proving the sheets and the source pages hold identical text.

Last results are in [`notes/`](notes/). Both pass.

## Layout

```
source/     the canonical text and its hash — read this first
build/      the pipeline. Nothing here writes to source/
print/      generated PDFs, QR cards, and printing instructions
docs/       the web page, served by GitHub Pages
notes/      divergences from the source photographs, validation output, hosting notes
make.sh     rebuild everything
```

## Building

Needs Python 3, [Playwright](https://playwright.dev/python/) with Chromium, `pypdf`,
`reportlab`, `Pillow`, and Poppler's `pdftotext` / `pdfinfo` / `pdftoppm` / `pdffonts`.

Fonts are looked up by filename in `build/fonts/` first, then in the usual system
directories. If one is missing the build says which and stops. You need
**Poppins** (Regular/Medium/Bold), **Caladea** (Regular/Bold) and **FreeSerif**.

```bash
SITE_URL="https://vggg.github.io/aarti-sangraha/" ./make.sh
```

That produces all three PDFs, the QR cards, and runs both acceptance tests.

To regenerate only the QR after moving the site:

```bash
python3 build/make_qr.py "https://your-new-url"
```

## Printing

[`print/PRINTING.md`](print/PRINTING.md) has the full settings. The short version: A4,
**landscape**, double-sided, **short-edge binding**, 5 sheets, fold the stack in half and
staple twice on the fold. Print sheet 1 alone first and check it folds correctly before
running the rest.

## Typography

The print edition sets Devanagari in **Poppins** — chosen because it was the only available
face with complete, correctly shaped conjuncts, verified glyph by glyph before use. Verse
markers use **FreeSerif**, because Poppins maps the Devanagari digits ०–९ to Latin digit
shapes. English is **Caladea**.

The web page uses **Noto Serif Devanagari** from Google Fonts — the traditional serif the
print build could not reach.

No artwork is imported anywhere. Every ornament is drawn as vector shapes, so there is no
image in the booklet that could contain generated lettering.

## Licence

Code under [MIT](LICENSE). The verses are traditional compositions in the public domain —
Sant Ramdas, Sant Eknath, Sant Namdev, and Vedic sources — and no claim is made over them.
The source photographs are not committed; the verses are public domain, that edition's
typesetting is not.

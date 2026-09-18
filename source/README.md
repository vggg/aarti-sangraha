# source

`aarti_master.json` is the single source of truth. 95 lines across six aartis, each with a
permanent ID (`GAN-001` …), the Devanagari, and a syllable-hyphenated Roman pronunciation.
Every output in this repo — the three PDFs and the web page — is generated from this file.

`aarti_master.sha256` is its hash. `build/build.py` recomputes it on every run and refuses
to start if it does not match, so a design change can never quietly alter the text.

To change the text, edit the JSON, then:

```
sha256sum aarti_master.json > aarti_master.sha256
```

and rebuild. The acceptance test in `build/validate.py` extracts the text layer back out of
each generated PDF and asserts every line appears character for character.

## Where the text came from

The verses follow the standard published Marathi and Sanskrit text. Ten photographs of a
printed Aarti Sangrah edition were transcribed at 3× magnification and used as a line-by-line
cross-check. All 27 places where the two differ are documented in `notes/DIVERGENCES.md`.

The photographs are deliberately not committed — see `.gitignore`. The verses are public
domain; that particular edition's typesetting is not.

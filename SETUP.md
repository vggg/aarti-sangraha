# Publishing this to GitHub Pages

From this folder:

```bash
git init -b main
git add -A
git commit -m "Aarti Sangraha: booklet, web page and build pipeline"
gh repo create aarti-sangraha --public --source=. --push
```

No `gh`? Create an empty **public** repo on github.com named `aarti-sangraha`, then:

```bash
git remote add origin https://github.com/YOUR-USERNAME/aarti-sangraha.git
git push -u origin main
```

Then in the repo: **Settings → Pages → Build and deployment**
Source: *Deploy from a branch* · Branch: **main** · Folder: **/docs** · Save.

A minute later the page is live at `https://YOUR-USERNAME.github.io/aarti-sangraha/`.

## The repo has to be public

GitHub Pages from a private repo needs a paid plan. It also has to be public for relatives
to open the link without a GitHub account. Nothing here is sensitive — the photographs are
gitignored and the verses are public domain.

## Then repoint the QR

The cards in `print/` currently point at a placeholder. Once Pages is live:

```bash
python3 build/make_qr.py "https://YOUR-USERNAME.github.io/aarti-sangraha/"
git add print && git commit -m "QR to live site" && git push
```

Scan it with a phone on cellular, signed out of everything, before printing a stack.

## Optional: your own domain

If these booklets will circulate for years, point the QR at a domain you own rather than a
`github.io` address, so you can move the site later without every printed code going dead.
Add a `CNAME` file in `docs/` containing the domain, point a CNAME DNS record at
`YOUR-USERNAME.github.io`, then set the custom domain under Settings → Pages.

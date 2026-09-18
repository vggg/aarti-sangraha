# Hosting the singing page

## Where it is now

`https://claude.ai/artifact/SqWFbZx2Vc2ijsRcL3qWNp` — hosted by Anthropic on claude.ai,
tied to your Claude account. Private until you share it from the page's Share menu.

## Why that is not good enough for a QR code

Anthropic's own documentation is explicit: for artifacts shared through the Share dialog,
**"A Claude account is required. People without a Claude account can't open or interact with
a shared artifact, even if they have the link."** Setting it to "Anyone with the link" does
not change that.

So a relative who scans the card and has no Claude account hits a sign-in wall. That defeats
the entire point of handing out QR codes at a gathering.

## What to use instead

`Aarti_Sangraha_standalone.html` is one self-contained file — no build step, no dependencies
beyond Google Fonts. Put it anywhere that serves static files and the QR works for anyone.

**Cloudflare Pages** — free. Create a project, drag the file in as `index.html`, you get
`something.pages.dev` immediately. No viewer login, no bandwidth limits worth worrying about.

**GitHub Pages** — free. Commit the file as `index.html` to a public repo, enable Pages in
Settings. URL is `username.github.io/reponame`.

**Netlify** — free. Same drag-and-drop idea.

Any of the three takes about five minutes. All three serve to anyone, no account.

## Then regenerate the QR

The cards currently point at the claude.ai URL. Once you have the real one:

```
python3 make_qr.py "https://your-real-url"
```

That rewrites `Aarti_QR.png` and `Aarti_QR_Cards.pdf`. Nothing else changes.

## A note on longevity

If these booklets are going to circulate for years, the URL matters more than the page. A
domain you control — even a cheap one pointed at Cloudflare Pages — means you can move or
rebuild the page later without every printed QR code going dead. A `pages.dev` or
`github.io` address is fine, but it belongs to that platform, not to you.

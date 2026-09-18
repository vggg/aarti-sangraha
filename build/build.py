# -*- coding: utf-8 -*-
"""Aarti Sangraha booklet builder.
Reads the frozen canonical master and emits HTML -> PDF.
The master is READ ONLY; this script never edits it."""
import json, re, html, hashlib, pathlib, sys

import os, sys, pathlib as _pl
_ROOT = _pl.Path(__file__).resolve().parent.parent
_FONTDIRS = [_ROOT/'build'/'fonts',
             _pl.Path('/usr/share/fonts/truetype/google-fonts'),
             _pl.Path('/usr/share/fonts/truetype/crosextra'),
             _pl.Path('/usr/share/fonts/truetype/freefont'),
             _pl.Path('/Library/Fonts'), _pl.Path.home()/'Library'/'Fonts',
             _pl.Path('/usr/share/fonts')]
def font(name):
    """Find a TTF by filename. Drop missing ones into build/fonts/."""
    for d in _FONTDIRS:
        if not d.exists():
            continue
        hit = d/name
        if hit.exists():
            return hit
        for f in d.rglob(name):
            return f
    sys.exit(f"Missing font {name}.\n"
             f"Put it in {_ROOT/'build'/'fonts'} and re-run.\n"
             f"Poppins and Noto Serif Devanagari: fonts.google.com. "
             f"Caladea: ships with LibreOffice. FreeSerif: GNU FreeFont.")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT, WORK = ROOT/'source', ROOT/'print', ROOT/'build'/'_work'
WORK.mkdir(parents=True, exist_ok=True); OUT.mkdir(exist_ok=True)
MASTER = SRC/'aarti_master.json'

# --- integrity gate -------------------------------------------------------
expected = (SRC/'aarti_master.sha256').read_text().split()[0]
actual = hashlib.sha256(MASTER.read_bytes()).hexdigest()
if expected != actual:
    sys.exit(f'MASTER HASH MISMATCH\n expected {expected}\n actual   {actual}')
D = json.loads(MASTER.read_text())

import os
PAGE = os.environ.get('PAGE','LETTER')          # LETTER | A5
if PAGE == 'A5':
    PW, PH, S = '148mm', '210mm', 0.686         # S scales every fixed dimension
else:
    PW, PH, S = '8.5in', '11in', 1.0
def u(v, unit='in'):                            # scaled fixed dimension
    return f'{v*S:.4f}{unit}'

DEVA = font("Poppins-Regular.ttf").as_uri()
DEVA_M = font("Poppins-Medium.ttf").as_uri()
DEVA_B = font("Poppins-Bold.ttf").as_uri()
SERIF  = font("Caladea-Regular.ttf").as_uri()
SERIF_B= font("Caladea-Bold.ttf").as_uri()
NUM   = font("FreeSerif.ttf").as_uri()

MARKER = re.compile(r'(॥[^॥]*॥)')

def split_marker(mr):
    """Wrap ॥..॥ markers in a span that uses a font with real Devanagari numerals.
    Text content is unchanged, so PDF text extraction still matches the master."""
    parts = MARKER.split(mr)
    out = []
    for p in parts:
        if not p:
            continue
        if p.startswith('॥'):
            out.append(f'<span class="mk">{html.escape(p)}</span>')
        else:
            out.append(html.escape(p))
    return ''.join(out)

CSS = f"""
@font-face{{font-family:Deva;src:url('{DEVA}');font-weight:400}}
@font-face{{font-family:Deva;src:url('{DEVA_M}');font-weight:500}}
@font-face{{font-family:Deva;src:url('{DEVA_B}');font-weight:700}}
@font-face{{font-family:Lora;src:url('{SERIF}');font-weight:400}}
@font-face{{font-family:Lora;src:url('{SERIF_B}');font-weight:700}}
@font-face{{font-family:Nums;src:url('{NUM}')}}

@page {{ size: {PW} {PH}; margin: 0; }}
* {{ box-sizing: border-box; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
html,body {{ margin:0; padding:0; background:#fff; }}

:root {{
  --cream:#FDF6E8; --cream2:#FBEFD9;
  --maroon:#8C1D2F; --charcoal:#23201C; --teal:#1B6E8C;
  --gold:#C99A2E; --muted:#7A6A55;
}}

.page {{
  position:relative; width:{PW}; height:{PH}; overflow:hidden;
  background:var(--cream); page-break-after:always; break-after:page;
  font-family:Lora, serif; color:var(--charcoal);
}}
.page:last-child {{ page-break-after:auto; break-after:auto; }}

/* frame */
.stripe {{ position:absolute; left:0; top:0; bottom:0; width:{u(.30)}; background:var(--ac); }}
.stripe:after {{ content:''; position:absolute; right:{u(-.055)}; top:0; bottom:0; width:{u(.035)}; background:var(--gold); opacity:.85; }}
.frame {{ position:absolute; left:{u(.56)}; right:{u(.46)}; top:{u(.36)}; bottom:{u(.36)};
  border:1.6px solid rgba(201,154,46,.55); border-radius:{u(.10)}; pointer-events:none; }}
.frame:before {{ content:''; position:absolute; left:{u(.055)}; right:{u(.055)}; top:{u(.055)}; bottom:{u(.055)};
  border:.9px solid rgba(201,154,46,.35); border-radius:{u(.07)}; }}

.page.recto .stripe {{ left:auto; right:0; }}
.page.recto .stripe:after {{ right:auto; left:{u(-.055)}; }}
.page.recto .pg {{ right:auto; left:{u(.64)}; }}
.page.recto .foot {{ left:{u(1.15)}; right:{u(.88)}; flex-direction:row-reverse; }}
.inner {{ position:absolute; left:{u(.88)}; right:{u(.78)}; top:{u(.58)}; bottom:{u(.62)}; display:flex; flex-direction:column; }}

/* title block */
.tt {{ text-align:center; margin-bottom:{u(.06)}; }}
.tt .mr {{ font-family:Deva; font-weight:500; font-size:{17*S:.2f}pt; color:var(--maroon); line-height:1.35; }}
.tt .en {{ font-family:Lora; font-size:{10*S:.2f}pt; letter-spacing:.15em; text-transform:uppercase;
  color:var(--ac); margin-top:{u(.055)}; }}
.tt .inc {{ font-family:Deva; font-size:{9.5*S:.2f}pt; color:var(--muted); margin-top:{u(.05)}; }}
.rule {{ width:{u(1.6)}; height:0; margin:{u(.07)} auto {u(.11)}; border-top:1.2px solid rgba(201,154,46,.75); position:relative; }}
.rule:after {{ content:'❖'; position:absolute; left:50%; top:{u(-.085)}; transform:translateX(-50%);
  background:var(--cream); padding:0 {u(.07)}; color:var(--gold); font-size:{9*S:.2f}pt; line-height:1; }}

/* verses */
.verses {{ flex:1 1 auto; display:flex; flex-direction:column;
  justify-content:space-between; gap:var(--gap); }}
.ln {{ margin-bottom:0; }}
.ln .mr {{ font-family:Deva; font-size:var(--fs); line-height:1.24; text-wrap:pretty; color:var(--charcoal); }}
.ln .ro {{ font-family:Lora; font-size:calc(var(--fs) * 0.82); line-height:1.2; text-wrap:pretty; color:var(--teal);
  letter-spacing:.006em; margin-top:{u(.022)}; }}
.mk {{ font-family:Nums; color:var(--maroon); font-size:.92em; }}

.ln.refrain {{ background:linear-gradient(0deg, var(--cream2), var(--cream2));
  border-left:3px solid var(--ac); border-radius:{u(.05)};
  padding:{u(.05)} {u(.10)} {u(.058)} {u(.12)}; margin-bottom:0; }}
.ln.refrain .mr {{ color:var(--maroon); font-weight:500; }}

/* footer */
.seal {{ text-align:center; font-family:Deva; font-size:{9.5*S:.2f}pt; color:var(--maroon);
  padding-top:{u(.02)}; margin-top:{u(.16)}; }}
.foot {{ position:absolute; left:{u(.88)}; right:{u(1.15)}; bottom:{u(.40)};
  display:flex; justify-content:space-between; align-items:center;
  font-family:Lora; font-size:{8.4*S:.2f}pt; color:var(--muted); letter-spacing:.055em; }}
.pg {{ position:absolute; right:{u(.64)}; bottom:{u(.30)}; width:{u(.30)}; height:{u(.30)}; border-radius:50%;
  background:var(--ac); color:#fff; font-family:Lora; font-size:{8.6*S:.2f}pt;
  display:flex; align-items:center; justify-content:center; }}

/* cover */
.cover {{ --ac:#C99A2E; }}
.cover .inner {{ align-items:center; justify-content:center; text-align:center; }}
.cv-mr {{ font-family:Deva; font-weight:500; font-size:{40*S:.2f}pt; color:var(--maroon); }}
.cv-en {{ font-family:Lora; font-size:{20*S:.2f}pt; letter-spacing:.30em; text-transform:uppercase;
  color:var(--ac); margin-top:{u(.12)}; }}
.cv-tag {{ font-family:Lora; font-size:{12.5*S:.2f}pt; letter-spacing:.14em; color:var(--teal); margin-top:{u(.20)}; }}
.cv-list {{ margin-top:{u(.55)}; font-family:Deva; font-size:{14*S:.2f}pt; color:var(--charcoal); line-height:2.05; }}
.cv-list b {{ font-weight:400; }}
.cv-list .en {{ font-family:Lora; font-size:{10.5*S:.2f}pt; color:var(--muted); letter-spacing:.09em; }}
.cv-foot {{ position:absolute; bottom:{u(1.05)}; left:0; right:0; text-align:center;
  font-family:Lora; font-size:{10*S:.2f}pt; color:var(--muted); letter-spacing:.06em; }}
.lotus {{ margin:{u(.30)} auto {u(.10)}; }}

/* prose pages */
.prose h2 {{ font-family:Lora; font-size:{14*S:.2f}pt; color:var(--maroon); margin:0 0 {u(.05)}; letter-spacing:.02em; }}
.prose .h-mr {{ font-family:Deva; font-size:{15*S:.2f}pt; color:var(--ac); margin-bottom:{u(.09)}; }}
.prose p {{ font-family:Lora; font-size:{11.4*S:.2f}pt; line-height:1.60; margin:0 0 {u(.30)}; color:#332F29; }}
.prose .blk {{ margin-bottom:{u(.34)}; }}
.note {{ background:var(--cream2); border-radius:{u(.07)}; padding:{u(.16)} {u(.20)}; margin-top:{u(.10)}; }}
.note h3 {{ font-family:Lora; font-size:{10.8*S:.2f}pt; color:var(--maroon); margin:0 0 {u(.07)}; letter-spacing:.06em; text-transform:uppercase; }}
.note li {{ font-family:Lora; font-size:{10.6*S:.2f}pt; line-height:1.55; margin-bottom:{u(.045)}; }}
.note ul {{ margin:0; padding-left:{u(.19)}; }}

.toc {{ display:flex; align-items:baseline; gap:{u(.08)}; margin-bottom:{u(.20)}; }}
.toc .mr {{ font-family:Deva; font-size:{13*S:.2f}pt; color:var(--charcoal); }}
.toc .en {{ font-family:Lora; font-size:{10*S:.2f}pt; color:var(--muted); letter-spacing:.08em; }}
.toc .dots {{ flex:1; border-bottom:1px dotted rgba(122,106,85,.5); }}
.tt .cont {{ font-family:Lora; text-transform:none; letter-spacing:.04em; color:var(--muted); }}
.closing .inner {{ align-items:center; justify-content:center; text-align:center; }}
.closing .a {{ font-family:Deva; font-size:{20*S:.2f}pt; color:var(--maroon); }}
.closing .b {{ font-family:Lora; font-size:{15*S:.2f}pt; color:var(--teal); line-height:1.75; margin-top:{u(.28)}; }}
.closing .c {{ font-family:Deva; font-size:{16*S:.2f}pt; color:var(--maroon); margin-top:{u(.62)}; }}
.closing .d {{ font-family:Lora; font-size:{10.8*S:.2f}pt; letter-spacing:.20em; text-transform:uppercase; color:var(--muted); margin-top:{u(.09)}; }}
"""

LOTUS = """<svg class="lotus" width="86" height="52" viewBox="0 0 86 52" fill="none">
<g stroke="#C99A2E" stroke-width="1.3" fill="none">
<path d="M43 48 C43 30 43 18 43 6 C49 16 52 30 43 48Z"/>
<path d="M43 48 C43 30 43 18 43 6 C37 16 34 30 43 48Z"/>
<path d="M43 48 C34 34 26 24 16 15 C18 27 26 40 43 48Z"/>
<path d="M43 48 C52 34 60 24 70 15 C68 27 60 40 43 48Z"/>
<path d="M43 48 C30 40 18 34 5 31 C13 40 26 48 43 48Z"/>
<path d="M43 48 C56 40 68 34 81 31 C73 40 60 48 43 48Z"/>
</g></svg>"""

def page(cls, ac, body, pageno=None, foot=True, side=None):
    if side is None and pageno is not None:
        side = 'recto' if pageno % 2 else 'verso'
    cls = f'{cls} {side}' if side else cls
    pg = f'<div class="pg">{pageno}</div>' if pageno else ''
    ft = ('<div class="foot"><span>Aarti Sangraha</span>'
          '<span>Read &nbsp;•&nbsp; Pronounce &nbsp;•&nbsp; Sing &nbsp;•&nbsp; Understand</span></div>') if foot else ''
    return (f'<section class="page {cls}" style="--ac:{ac}">'
            f'<div class="stripe"></div><div class="frame"></div>'
            f'<div class="inner">{body}</div>{ft}{pg}</section>')

pages = []

# ---- cover ---------------------------------------------------------------
items = ''.join(
    f'<div><b>{html.escape(a["title_mr"])}</b> &nbsp;<span class="en">{html.escape(a["title_en"])}</span></div>'
    for a in D['aartis'])
pages.append(page('cover', '#C99A2E',
    f'<div class="cv-mr">॥ आरती संग्रह ॥</div>'
    f'<div class="cv-en">Aarti Sangraha</div>'
    f'{LOTUS}'
    f'<div class="cv-tag">Read &nbsp;•&nbsp; Pronounce &nbsp;•&nbsp; Sing &nbsp;•&nbsp; Understand</div>'
    f'<div class="cv-list">{items}</div>'
    f'<div class="cv-foot">॥ सर्वे भवन्तु सुखिनः ॥ &nbsp;&nbsp;·&nbsp;&nbsp; May all be happy</div>',
    foot=False, side='recto'))

# ---- how to use ----------------------------------------------------------
pages.append(page('prose', '#C99A2E',
    '<div class="tt"><div class="mr">॥ या पुस्तिकेचा उपयोग ॥</div>'
    '<div class="en">How to use this book</div></div><div class="rule"></div>'
    '<p>Every aarti is set out the same way. The Marathi or Sanskrit line comes first, '
    'in dark type. Directly beneath it, in blue, is the same line written out in English '
    'letters and broken into syllables, so that anyone can sing along without reading '
    'Devanagari. The refrain — the line the whole room comes back to — sits in a tinted '
    'band so you can find it at a glance.</p>'
    '<p>The English meanings are gathered at the back of the book rather than beside the '
    'verses, so that the singing pages stay uncluttered. Read the meaning once; after that '
    'you will not need it.</p>'
    '<div class="note"><h3>A note on the text</h3><ul>'
    '<li>The Marathi and Sanskrit here follow the standard published text, checked line by '
    'line against a photographed Aarti Sangrah edition.</li>'
    '<li>The blue line is a pronunciation aid, not a transliteration scheme. Families sing '
    'these differently from region to region, and every one of those ways is correct.</li>'
    '<li>The English meanings are written to convey the sense of the verse, not to translate '
    'it word for word.</li>'
    '<li>Verse numbers and the ॥धृ॥ mark for the refrain follow the traditional printing.</li>'
    '</ul></div>', 2))

# ---- aarti pages ---------------------------------------------------------
SPREAD = os.environ.get('SPREAD','0') == '1'

def chunks(lines):
    """One page, or two balanced pages that never split a refrain pair."""
    if not SPREAD or len(lines) <= 10:
        return [lines]
    cut = (len(lines) + 1) // 2
    while 0 < cut < len(lines) and lines[cut]['type'] == 'refrain' \
          and lines[cut-1]['type'] == 'refrain':
        cut += 1
    return [lines[:cut], lines[cut:]]

n = 3
if SPREAD:
    # contents page, so that every two-page aarti opens as a facing spread
    toc = ''.join(
        f'<div class="toc"><span class="mr">{html.escape(a["title_mr"])}</span>'
        f'<span class="dots"></span>'
        f'<span class="en">{html.escape(a["title_en"])}</span></div>'
        for a in D['aartis'])
    pages.append(page('prose toc', '#C99A2E',
        '<div class="tt"><div class="mr">॥ अनुक्रमणिका ॥</div>'
        '<div class="en">Contents</div></div><div class="rule"></div>' + toc, n))
    n += 1

for a in D['aartis']:
    cs = chunks(a['lines'])
    for ci, chunk in enumerate(cs):
        lines = ''.join(
            f'<div class="ln{" refrain" if l["type"]=="refrain" else ""}">'
            f'<div class="mr">{split_marker(l["mr"])}</div>'
            f'<div class="ro">{html.escape(l["ro"])}</div></div>'
            for l in chunk)
        cont = len(cs) > 1 and ci > 0
        head = (f'<div class="tt"><div class="mr">॥ {html.escape(a["title_mr"])} ॥</div>'
                f'<div class="en">{html.escape(a["title_en"])}'
                + ('<span class="cont"> &nbsp;·&nbsp; continued</span>' if cont else '')
                + f'</div><div class="inc">{html.escape(a["incipit_mr"])}</div></div>')
        seal = (f'<div class="seal">{html.escape(a["seal"])}</div>'
                if ci == len(cs) - 1 else '<div class="seal">&nbsp;</div>')
        pages.append(page('aarti', a['accent'],
                          head + '<div class="rule"></div>'
                          + f'<div class="verses" data-fit="1">{lines}</div>' + seal, n))
        n += 1

# ---- meanings ------------------------------------------------------------
blocks = []
for a in D['aartis']:
    blocks.append(f'<div class="blk"><div class="h-mr" style="color:{a["accent"]}">'
                  f'{html.escape(a["title_mr"])}</div>'
                  f'<h2>{html.escape(a["title_en"])}</h2>'
                  f'<p>{html.escape(a["meaning"])}</p></div>')
first = True
for i in range(0, len(blocks), 2):
    head = ('<div class="tt"><div class="mr">॥ अर्थ ॥</div>'
            '<div class="en">The Meanings</div></div><div class="rule"></div>') if first else \
           ('<div class="tt"><div class="en">The Meanings &nbsp;·&nbsp; continued</div></div>'
            '<div class="rule"></div>')
    first = False
    pages.append(page('prose', '#8C1D2F', head + ''.join(blocks[i:i+2]), n))
    n += 1

# ---- closing -------------------------------------------------------------
pages.append(page('closing', '#C99A2E',
    '<div class="a">॥ सर्वे भवन्तु सुखिनः ॥</div>'
    '<div class="b">May these aartis bring peace to our homes,<br>'
    'strength to our hearts, and devotion to our lives.</div>'
    f'{LOTUS}'
    '<div class="c">भक्ती &nbsp;•&nbsp; संस्कृती &nbsp;•&nbsp; परिवार</div>'
    '<div class="d">Devotion &nbsp;•&nbsp; Culture &nbsp;•&nbsp; Family</div>', foot=False,
    side=('recto' if (len(pages)+1) % 2 else 'verso')))

# saddle stitch needs a multiple of 4; plain duplex only needs an even count
mult = 4 if SPREAD else 2
while len(pages) % mult:
    pages.append(page('blank', '#C99A2E', '', foot=False,
                      side='recto' if (len(pages)+1) % 2 else 'verso'))

FIT = """
<script>
var SCALE = %SCALE%;
/* Pass A: largest type size that fits EVERY verse page at base leading.
   Pass B: that one size everywhere, leading opened up so each page fills. */
var GAP_K = 0.0070*SCALE, GAP_MAX_MULT = 3.6, MIN_FS = 8.0, MAX_FS = %MAXFS%;

function fits(v){ var b=v.parentElement; return b.scrollHeight <= b.clientHeight; }
function setv(v, fs, gap){
  v.style.setProperty('--fs', fs.toFixed(3)+'pt');
  v.style.setProperty('--gap', gap.toFixed(4)+'in');
}
function maxFs(v){
  var lo=MIN_FS, hi=MAX_FS;
  for (var i=0;i<26;i++){
    var mid=(lo+hi)/2; setv(v, mid, mid*GAP_K);
    if (fits(v)) lo=mid; else hi=mid;
  }
  setv(v, lo, lo*GAP_K);
  return lo;
}
function fit(){
  var vs = Array.prototype.slice.call(document.querySelectorAll('[data-fit]'));
  var global = Math.min.apply(null, vs.map(maxFs));
  vs.forEach(function(v){
    setv(v, global, global*GAP_K);
    v.setAttribute('data-final', global.toFixed(2)+'pt min-gap '+(global*GAP_K).toFixed(3)+'in');
  });
  document.body.setAttribute('data-fitted','1');
}
document.fonts.ready.then(function(){ setTimeout(fit, 50); });
</script>"""

FIT = FIT.replace('%SCALE%', repr(S)).replace('%MAXFS%', '13.4' if PAGE=='A5' else '17.6')

doc = ('<!doctype html><html><head><meta charset="utf-8">'
       '<title>Aarti Sangraha</title><style>'+CSS+'</style></head><body>'
       + ''.join(pages) + FIT + '</body></html>')
out = WORK/('booklet_a5.html' if PAGE=='A5' else 'booklet.html')
out.write_text(doc, encoding='utf-8')
print(f'{PAGE}: {len(pages)} pages ->', out.name)

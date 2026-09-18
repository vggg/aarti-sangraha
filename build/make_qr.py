# -*- coding: utf-8 -*-
"""QR card for the Aarti Sangraha singing page."""
import sys, pathlib

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
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

URL = sys.argv[1] if len(sys.argv) > 1 else 'https://example.com'
ROOT = pathlib.Path(__file__).resolve().parent.parent/'print'

def matrix(url, level='H'):
    w = QrCodeWidget(url, barLevel=level)
    q = w.qr
    q.make()
    n = q.getModuleCount()
    return [[bool(q.isDark(r, c)) for c in range(n)] for r in range(n)], n

M, N = matrix(URL)
print(f'QR {N}x{N} modules, error correction H')

# --- crisp PNG, drawn module by module -----------------------------------
SCALE, QUIET = 24, 4
px = (N + 2*QUIET) * SCALE
img = Image.new('RGB', (px, px), '#FFFDF7')
pix = img.load()
for r in range(N):
    for c in range(N):
        if M[r][c]:
            for y in range(SCALE):
                for x in range(SCALE):
                    pix[(c+QUIET)*SCALE + x, (r+QUIET)*SCALE + y] = (0x24, 0x1F, 0x19)
img.save(ROOT/'Aarti_QR.png')
print('PNG', img.size)

# --- printable card sheet -------------------------------------------------
pdfmetrics.registerFont(TTFont('Dev', str(font('Poppins-Medium.ttf'))))
pdfmetrics.registerFont(TTFont('Ser', str(font('Caladea-Regular.ttf'))))
pdfmetrics.registerFont(TTFont('SerB', str(font('Caladea-Bold.ttf'))))

cream = HexColor('#FBF4E6'); ink = HexColor('#241F19'); maroon = HexColor('#8C1D2F')
gold = HexColor('#BE8F25'); teal = HexColor('#14607A'); muted = HexColor('#8A7659')

W, H = A4
c = canvas.Canvas(str(ROOT/'Aarti_QR_Cards.pdf'), pagesize=A4)
CW, CH = W/2, H/2

def card(ox, oy):
    m = 16
    c.setFillColor(cream)
    c.rect(ox+m, oy+m, CW-2*m, CH-2*m, fill=1, stroke=0)
    c.setStrokeColor(gold); c.setLineWidth(1.1)
    c.roundRect(ox+m+9, oy+m+9, CW-2*m-18, CH-2*m-18, 8, fill=0, stroke=1)
    c.setLineWidth(.6)
    c.roundRect(ox+m+14, oy+m+14, CW-2*m-28, CH-2*m-28, 6, fill=0, stroke=1)

    cx = ox + CW/2
    c.setFillColor(maroon); c.setFont('Dev', 19)
    c.drawCentredString(cx, oy+CH-m-62, '॥ आरती संग्रह ॥')
    c.setFillColor(gold); c.setFont('SerB', 10.5)
    c.drawCentredString(cx, oy+CH-m-82, 'A A R T I   S A N G R A H A')

    # QR
    box = 176
    qx, qy = cx - box/2, oy + CH/2 - box/2 - 14
    c.setFillColor(HexColor('#FFFDF7'))
    c.roundRect(qx-11, qy-11, box+22, box+22, 7, fill=1, stroke=0)
    step = box / N
    c.setFillColor(ink)
    for r in range(N):
        for k in range(N):
            if M[r][k]:
                c.rect(qx + k*step, qy + box - (r+1)*step, step*1.02, step*1.02,
                       fill=1, stroke=0)

    c.setFillColor(ink); c.setFont('SerB', 13)
    c.drawCentredString(cx, qy-34, 'Scan to sing along')
    c.setFillColor(teal); c.setFont('Ser', 10)
    c.drawCentredString(cx, qy-50, 'Marathi, pronunciation and meaning')
    c.setFillColor(muted); c.setFont('Ser', 8.4)
    c.drawCentredString(cx, oy+m+30, 'Read  •  Pronounce  •  Sing  •  Understand')

for ox, oy in ((0, CH), (CW, CH), (0, 0), (CW, 0)):
    card(ox, oy)

# faint cut guides
c.setStrokeColor(HexColor('#D8C8A8')); c.setLineWidth(.4); c.setDash(2, 4)
c.line(W/2, 0, W/2, H); c.line(0, H/2, W, H/2)
c.save()
print('PDF: 4 cards on A4')

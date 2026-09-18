# -*- coding: utf-8 -*-
"""Saddle-stitch imposition: A5 pages -> A4 landscape sheets, 2-up, fold in half."""
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import RectangleObject
import pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent/'print'
src = PdfReader(str(ROOT/'Aarti_A5_pages.pdf'))
N = len(src.pages)
assert N % 4 == 0, f'saddle stitch needs a multiple of 4 pages, got {N}'

A4W, A4H = 841.89, 595.28          # A4 landscape, points
pw = float(src.pages[0].mediabox.width)
ph = float(src.pages[0].mediabox.height)
gapx = (A4W - 2*pw) / 2            # even slack left and right
offy = (A4H - ph) / 2

# sheet i: front = (N-2i, 2i+1), back = (2i+2, N-2i-1); 1-indexed page numbers
order = []
for i in range(N // 4):
    order.append((N - 2*i, 2*i + 1))       # front of sheet i
    order.append((2*i + 2, N - 2*i - 1))   # back of sheet i

w = PdfWriter()
for left, right in order:
    sheet = w.add_blank_page(width=A4W, height=A4H)
    for slot, num in ((0, left), (1, right)):
        p = src.pages[num - 1]
        tx = gapx + slot * pw
        sheet.merge_transformed_page(p, Transformation().translate(tx, offy))
    sheet.mediabox = RectangleObject((0, 0, A4W, A4H))

out = ROOT/'Aarti_Sangraha_A4_Booklet.pdf'
with open(out, 'wb') as f:
    w.write(f)
print(f'{N} A5 pages -> {len(order)} A4 sheets ({N//4} sheets, printed both sides)')
print('sheet order:', ' | '.join(f'{l},{r}' for l, r in order))

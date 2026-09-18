# -*- coding: utf-8 -*-
"""Verify the imposed sheets: each half-sheet must carry exactly the A5 page
that saddle-stitch order says belongs there."""
import subprocess, unicodedata, re, pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent/'print'
A5=ROOT/'Aarti_A5_pages.pdf'; BK=ROOT/'Aarti_Sangraha_A4_Booklet.pdf'

def txt(pdf, page, crop=None):
    cmd=['pdftotext','-enc','UTF-8','-f',str(page),'-l',str(page)]
    if crop: cmd+=['-x',str(crop[0]),'-y',str(crop[1]),'-W',str(crop[2]),'-H',str(crop[3])]
    cmd+=[str(pdf),'-']
    out=subprocess.run(cmd,capture_output=True,text=True).stdout
    return re.sub(r'\s+','',unicodedata.normalize('NFC',out))

N=20
order=[]
for i in range(N//4):
    order.append((N-2*i, 2*i+1)); order.append((2*i+2, N-2*i-1))

PW=421; PH=596; GAP=int((841.89-2*419.53)/2)
bad=[]
print(f'{"sheet":>5} {"side":<5} {"left":>5} {"right":>6}   match')
for s,(l,r) in enumerate(order, start=1):
    side='front' if s%2 else 'back'
    got_l=txt(BK,s,(0,0,PW+GAP,PH))
    got_r=txt(BK,s,(PW+GAP,0,PW+GAP,PH))
    want_l=txt(A5,l); want_r=txt(A5,r)
    okl = want_l==got_l or (want_l and want_l in got_l)
    okr = want_r==got_r or (want_r and want_r in got_r)
    if not okl: bad.append(f'sheet {s} left slot should hold A5 p{l}')
    if not okr: bad.append(f'sheet {s} right slot should hold A5 p{r}')
    print(f'{(s+1)//2:>5} {side:<5} {l:>5} {r:>6}   {"OK" if okl and okr else "MISMATCH"}')

# and the combined content of every sheet must equal the whole booklet
allsheets=''.join(txt(BK,s) for s in range(1,len(order)+1))
allpages=''.join(txt(A5,p) for p in range(1,N+1))
same = sorted(allsheets)==sorted(allpages)
print(f'\ncharacter census across all sheets vs all pages: {"IDENTICAL" if same else "DIFFERS"}')
print('RESULT:', 'PASS' if not bad and same else 'FAIL')
for b in bad: print('  ',b)

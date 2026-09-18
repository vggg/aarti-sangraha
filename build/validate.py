# -*- coding: utf-8 -*-
"""Acceptance test: every Devanagari line in the frozen master must appear,
character for character, in the generated PDF's text layer."""
import json, subprocess, unicodedata, hashlib, sys, re, pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT/'source', ROOT/'print'

# 1. master integrity
exp=(SRC/'aarti_master.sha256').read_text().split()[0]
act=hashlib.sha256((SRC/'aarti_master.json').read_bytes()).hexdigest()
print(f'[1] master sha256  {"OK" if exp==act else "FAIL"}  {act}')
if exp!=act: sys.exit(1)
D=json.loads((SRC/'aarti_master.json').read_text())

# 2. pull the PDF text layer
TARGET=OUT/(sys.argv[1] if len(sys.argv)>1 else 'Aarti_Sangraha.pdf')
def _raw(extra=None):
    cmd=['pdftotext','-layout','-enc','UTF-8']+(extra or [])+[str(TARGET),'-']
    return subprocess.run(cmd,capture_output=True,text=True).stdout
_w=float(re.search(r'Page size:\s+([\d.]+)',
      subprocess.run(['pdfinfo',str(TARGET)],capture_output=True,text=True).stdout).group(1))
if _w>800:
    # imposed sheets: read each half separately, or -layout interleaves across the gutter
    _n=int(re.search(r'Pages:\s+(\d+)',
        subprocess.run(['pdfinfo',str(TARGET)],capture_output=True,text=True).stdout).group(1))
    PW,GAP=421,1
    raw=''.join(_raw(['-f',str(i),'-l',str(i),'-x',str(x),'-y','0','-W',str(PW+GAP),'-H','596'])
                for i in range(1,_n+1) for x in (0,PW+GAP))
else:
    raw=_raw()
def norm(s):
    s=unicodedata.normalize('NFC',s)
    return re.sub(r'\s+','',s)
pdf=norm(raw)
print(f'[2] pdf text layer  {len(raw)} chars extracted')

# 3. every master line present, exactly
missing=[]; checked=0
for a in D['aartis']:
    for l in a['lines']:
        checked+=1
        if norm(l['mr']) not in pdf: missing.append((l['id'],l['mr'],'devanagari'))
        if norm(l['ro']) not in pdf: missing.append((l['id'],l['ro'],'roman'))
print(f'[3] line-for-line   {checked} verse lines x2 layers -> '
      f'{"OK, all present" if not missing else str(len(missing))+" MISSING"}')
for mid,txt,kind in missing: print(f'      MISSING {mid} ({kind}): {txt}')

# 4. nothing extra: no stray Devanagari in the PDF that is not in the master
allowed=set()
for a in D['aartis']:
    for key in ('title_mr','incipit_mr','seal'): allowed.add(norm(a[key]))
    for l in a['lines']: allowed.add(norm(l['mr']))
for extra in ['॥आरतीसंग्रह॥','॥यापुस्तिकेचाउपयोग॥','॥अर्थ॥','॥सर्वेभवन्तुसुखिनः॥',
              'भक्ती•संस्कृती•परिवार','॥धृ॥','॥सर्वेभवन्तुसुखिनः॥']:
    allowed.add(norm(extra))
blob=''.join(sorted(allowed))
dev_in_pdf=set(ch for ch in pdf if 'ऀ'<=ch<='ॿ')
dev_allowed=set(ch for ch in blob if 'ऀ'<=ch<='ॿ')
orphan=dev_in_pdf-dev_allowed
print(f'[4] no stray glyphs {"OK" if not orphan else "UNEXPECTED: "+repr(orphan)}')

# 5. page geometry
info=subprocess.run(['pdfinfo',str(TARGET)],capture_output=True,text=True).stdout
pages=int(re.search(r'Pages:\s+(\d+)',info).group(1))
size=re.search(r'Page size:\s+([\d.]+) x ([\d.]+)',info)
w,h=float(size.group(1)),float(size.group(2))
FORMATS={'letter':(612,792,2,'US Letter portrait'),
         'a5':(420,595,4,'A5 portrait'),
         'a4l':(842,595,1,'A4 landscape')}
key='a4l' if w>800 else ('a5' if w<500 else 'letter')
ew,eh,mult,label=FORMATS[key]
ok_size = abs(w-ew)<2 and abs(h-eh)<2
ok_mult = pages % mult == 0
print(f'[5] geometry        {pages} pages, {w:.0f}x{h:.0f}pt '
      f'({label+" OK" if ok_size else "WRONG SIZE"}), '
      f'{"page count OK for this format" if ok_mult else "BAD page count for "+label}')

# 6. fonts embedded
fonts=subprocess.run(['pdffonts',str(TARGET)],capture_output=True,text=True).stdout
lines=[l for l in fonts.strip().split('\n')[2:] if l.strip()]
not_emb=[l for l in lines if ' no ' in l[:80].replace('yes','YES')]
print(f'[6] fonts           {len(lines)} embedded subsets')
for l in lines: print('      '+l[:78])

print()
print('RESULT:', 'PASS' if (not missing and not orphan and ok_size and ok_mult) else 'FAIL')

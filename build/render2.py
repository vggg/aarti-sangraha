from playwright.sync_api import sync_playwright
import pathlib, sys, os
ROOT=pathlib.Path(__file__).resolve().parent.parent
WORK, OUT = ROOT/'build'/'_work', ROOT/'print'
src, out, w, h = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
with sync_playwright() as p:
    b=p.chromium.launch(args=['--font-render-hinting=none'])
    pg=b.new_page()
    pg.goto((WORK/src).as_uri())
    pg.wait_for_function("document.body.getAttribute('data-fitted')==='1'", timeout=60000)
    print('fit:', pg.eval_on_selector_all('[data-fit]', "e=>e.map(x=>x.getAttribute('data-final'))")[0])
    print('overflow:', max(pg.eval_on_selector_all('.inner',"e=>e.map(x=>x.scrollHeight-x.clientHeight)")))
    pg.pdf(path=str(OUT/out), width=w, height=h, print_background=True,
           margin={'top':'0','bottom':'0','left':'0','right':'0'}, prefer_css_page_size=True)
    b.close()

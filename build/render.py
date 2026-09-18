from playwright.sync_api import sync_playwright
import pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
WORK, OUT = ROOT/'build'/'_work', ROOT/'print'
with sync_playwright() as p:
    b=p.chromium.launch(args=['--font-render-hinting=none'])
    pg=b.new_page(viewport={'width':816,'height':1056})
    pg.goto((WORK/'booklet.html').as_uri())
    pg.wait_for_function("document.body.getAttribute('data-fitted')==='1'", timeout=60000)
    sizes=pg.eval_on_selector_all('[data-fit]', "els=>els.map(e=>e.getAttribute('data-final'))")
    over=pg.eval_on_selector_all('.inner', "els=>els.map(e=>e.scrollHeight-e.clientHeight)")
    print('fitted sizes:', sizes)
    print('overflow px per page:', over)
    pg.pdf(path=str(OUT/'Aarti_Sangraha.pdf'), width='8.5in', height='11in',
           print_background=True, margin={'top':'0','bottom':'0','left':'0','right':'0'},
           prefer_css_page_size=True)
    b.close()
print('pdf written')

"""Real Chromium checks served over HTTP, including mobile and citation navigation."""
from pathlib import Path
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import datetime, json, sys, threading
ROOT=Path(__file__).resolve().parents[1]

def run():
 from playwright.sync_api import sync_playwright
 checks=[];errors=[]
 def check(name,condition,detail=''):
  checks.append({'name':name,'passed':bool(condition),'detail':detail})
 class Quiet(SimpleHTTPRequestHandler):
  def log_message(self,*args): pass
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT/'site')))
 thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch()
   page=browser.new_page(viewport={'width':1440,'height':1000},device_scale_factor=1)
   page.on('pageerror',lambda error:errors.append(str(error)))
   response=page.goto(base+'/slides.html')
   check('desktop HTTP 200',response.status==200)
   check('initial one visible slide',page.locator('.slide:visible').count()==1)
   check('first page counter',page.locator('#page-number').inner_text()=='1 / 14')
   check('previous disabled at first',page.locator('#prev').is_disabled())
   page.locator('#next').click();check('next button',page.locator('#page-number').inner_text()=='2 / 14')
   page.locator('#prev').click();check('previous button',page.locator('#page-number').inner_text()=='1 / 14')
   page.keyboard.press('ArrowRight');check('keyboard right',page.locator('#page-number').inner_text()=='2 / 14')
   page.keyboard.press('ArrowLeft');check('keyboard left',page.locator('#page-number').inner_text()=='1 / 14')
   page.keyboard.press('PageDown');check('keyboard PageDown',page.locator('#page-number').inner_text()=='2 / 14')
   page.keyboard.press('PageUp');check('keyboard PageUp',page.locator('#page-number').inner_text()=='1 / 14')
   page.keyboard.press('End');check('keyboard End',page.locator('#page-number').inner_text()=='14 / 14')
   check('next disabled at last',page.locator('#next').is_disabled())
   page.keyboard.press('Home');check('keyboard Home',page.locator('#page-number').inner_text()=='1 / 14')
   page.goto(base+'/slides.html#slide-13');check('hash deep link',page.locator('#page-number').inner_text()=='13 / 14')
   page.locator('[data-answer="wrong"]').click();check('quiz incorrect feedback','再想一想' in page.locator('.quiz-feedback').inner_text())
   page.locator('[data-answer="correct"]').click();check('quiz correct feedback','答對' in page.locator('.quiz-feedback').inner_text())
   page.goto(base+'/slides.html#slide-6');page.locator('.slide:visible .citations a').first.click()
   claim_id=page.url.split('#')[-1]
   check('citation navigates to existing Wiki claim',claim_id.startswith('C') and page.locator('#'+claim_id).count()==1)
   page.locator('#wiki-search').fill('TalkNet');check('Wiki search TalkNet',page.locator('.entry:visible').count()==1)
   page.locator('#wiki-search').fill('人臉追蹤');check('Wiki Chinese alias search',page.locator('.entry:visible').count()==1)
   page.locator('#wiki-search').fill('zzzznonexistent');check('Wiki no-result state',page.locator('.entry:visible').count()==0 and '0 個' in page.locator('#search-status').inner_text())
   page.goto(base+'/slides.html')
   for number in range(1,15):
    page.goto(base+f'/slides.html#slide-{number}')
    check(f'desktop slide {number} no horizontal overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
    check(f'desktop slide {number} above controls',page.locator('.slide:visible').bounding_box()['y']+page.locator('.slide:visible').bounding_box()['height'] <= page.locator('.controls').bounding_box()['y']+1)
   screenshots=ROOT/'tests'/'screenshots';screenshots.mkdir(parents=True,exist_ok=True)
   page.goto(base+'/slides.html#slide-9');page.screenshot(path=str(screenshots/'desktop-pipeline.png'),full_page=True,animations='disabled')
   check('slide opaque after entry animation',page.locator('.slide:visible').evaluate('(el) => Number(getComputedStyle(el).opacity) === 1'))
   page.set_viewport_size({'width':390,'height':844})
   for number in range(1,15):
    page.goto(base+f'/slides.html#slide-{number}')
    check(f'mobile slide {number} no horizontal overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
   page.goto(base+'/slides.html#slide-5');page.screenshot(path=str(screenshots/'mobile-tracking.png'),full_page=True,animations='disabled')
   page.goto(base+'/wiki.html');check('mobile Wiki no horizontal overflow',page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
   page.set_viewport_size({'width':1440,'height':1000});page.goto(base+'/slides.html#slide-1');page.screenshot(path=str(screenshots/'desktop-cover.png'),full_page=True,animations='disabled')
   check('zero JavaScript page errors',not errors,'; '.join(errors))
   browser.close()
 except Exception as e:
  check('browser execution completed',False,f'{type(e).__name__}: {e}')
 finally: server.shutdown();server.server_close();thread.join(timeout=3)
 report={'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'engine':'Playwright Chromium 141 / real headless browser','passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),'checks':checks,'javascript_errors':errors}
 (ROOT/'tests').mkdir(exist_ok=True)
 (ROOT/'tests'/'browser_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'browser_passed':report['passed'],'browser_failed':report['failed'],'failures':[c for c in checks if not c['passed']]},ensure_ascii=False))
 return report

if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8')
 sys.exit(1 if run()['failed'] else 0)

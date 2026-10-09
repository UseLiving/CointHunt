import os
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
errs=[];res=[]
def ok(name,cond,extra=''):
    res.append((name,bool(cond)));print(('PASS ' if cond else 'FAIL ')+name+(' | '+str(extra) if extra!='' else ''))
with sync_playwright() as p:
    br=p.chromium.launch()
    ctx=br.new_context(viewport={'width':1280,'height':900});pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(800);E=pg.evaluate;ids=E("__co.IDS")
    for rep in range(5):
        for gid in ids:
            pg.click('[data-play="%s"][data-mode=free]'%gid);pg.wait_for_timeout(60)
            if E("__co.Run")is None:errs.append('did not open '+gid)
            pg.keyboard.press('ArrowLeft');pg.keyboard.press('d');pg.click('#stClose');pg.wait_for_timeout(30)
    ok('40 open/close cycles through real clicks, nothing left running',not errs and E("__co.Run")is None and E("document.getElementById('stage').hidden") and not E("document.body.classList.contains('lock')"),errs[:3])
    ok('game objects released after closing',E("__co.GM.catcher.s")is None and E("__co.GM.snake.t")is None and E("__co.GM.crash.t")is None and E("__co.GM.sweeper.t")is None)
    ok('stage is a labelled modal dialog',E("document.getElementById('stage').getAttribute('role')")=='dialog')
    ok('every game button has an accessible name',E("[].every.call(document.querySelectorAll('[data-play]'),function(b){return (b.getAttribute('aria-label')||'').length>5})"))
    ok('no sideways scroll on desktop',not E("document.documentElement.scrollWidth>innerWidth"))
    ok('the sheet takes each game\'s own colour',(E("__co.openGame('sweeper','free')") or True) and E("getComputedStyle(document.getElementById('stage')).getPropertyValue('--gc').trim().toLowerCase()")=='#ffd23f' and E("getComputedStyle(document.querySelector('.cabx .top')).backgroundColor")!='rgba(0, 0, 0, 0)',E("getComputedStyle(document.getElementById('stage')).getPropertyValue('--gc')"));E("__co.closeStage(true)")
    # tile order fills the grid with no holes on desktop
    r=E("(function(){var t=[].map.call(document.querySelectorAll('#grid .gt'),function(e){var r=e.getBoundingClientRect();return [Math.round(r.left),Math.round(r.top+scrollY),Math.round(r.width),Math.round(r.height)]});return t})()")
    ok('bento grid: Moon Crash is the big tile, first in the grid',E("document.querySelector('#grid .gt h3').textContent")=='Moon Crash' and r[0][2]>500 and r[0][3]>r[1][3]*1.5,r[0])
    cover=E("(function(){var g=document.getElementById('grid').getBoundingClientRect();var a=0;[].forEach.call(document.querySelectorAll('#grid .gt'),function(e){var r=e.getBoundingClientRect();a+=r.width*r.height});return a/(g.width*g.height)})()")
    ok('tiles fill at least 93% of the grid area (no holes)',cover>.93,round(cover,3))
    ctx.close()
    ctx=br.new_context(viewport={'width':390,'height':844},has_touch=True,is_mobile=True);pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(900);E=pg.evaluate
    ok('phone: no sideways scroll',not E("document.documentElement.scrollWidth>innerWidth"))
    ok('phone: sound button stays on one line',E("document.getElementById('sndb').getBoundingClientRect().height")<40,E("document.getElementById('sndb').getBoundingClientRect().height"))
    for gid in ids:
        pg.evaluate("document.querySelector('[data-play=\"%s\"][data-mode=free]').scrollIntoView({block:'center'})"%gid);pg.tap('[data-play="%s"][data-mode=free]'%gid);pg.wait_for_timeout(250)
        r=E("(function(){var b=document.getElementById('stBody'),s=document.getElementById('stage');var wide=[].some.call(b.querySelectorAll('*'),function(e){var r=e.getBoundingClientRect();return r.right>innerWidth+1&&e.offsetParent!==null});return {wide:wide,sw:s.scrollWidth>s.clientWidth}})()")
        ok('phone: %s fits the screen'%gid,not r['wide'] and not r['sw'],r);E("__co.closeStage(true)")
    E("__co.openGame('snake','free')");ok('phone: on-screen arrow pad for touch',E("getComputedStyle(document.querySelector('#stBody .pad')).display")=='grid');E("__co.closeStage(true)")
    ok('phone: the game sheet slides up from the bottom edge',(E("__co.openGame('catcher','free')") or True) and E("getComputedStyle(document.getElementById('stage')).alignItems")=='flex-end');E("__co.closeStage(true)")
    ok('no page errors',not errs,errs[:3]);ctx.close()
    ctx=br.new_context(viewport={'width':1280,'height':900},reduced_motion='reduce');pg=ctx.new_page();pg.goto(URL);pg.wait_for_timeout(500)
    ok('reduced motion: animations are shortened to nothing',pg.evaluate("parseFloat(getComputedStyle(document.querySelector('.stage')).animationDuration)")<.001);ctx.close();br.close()
print('SUMMARY: %d/%d passed'%(sum(1 for _,c in res if c),len(res)))

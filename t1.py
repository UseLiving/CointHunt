import os
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import datetime
from playwright.sync_api import sync_playwright
errs=[];res=[]
def ok(name,cond,extra=''):
    res.append((name,bool(cond)));print(('PASS ' if cond else 'FAIL ')+name+(' | '+str(extra) if extra!='' else ''))
def ms(y,m,d,h=12):return int(datetime.datetime(y,m,d,h,tzinfo=datetime.timezone.utc).timestamp()*1000)
with sync_playwright() as p:
    br=p.chromium.launch()
    def page(init=''):
        c=br.new_context(viewport={'width':1280,'height':900});c.add_init_script(init);pg=c.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(900);return c,pg
    ctx,pg=page();E=pg.evaluate
    ok('title and brand',pg.title().startswith('CoinHunt') and 'coinhunt' in pg.inner_text('.brand').lower())
    ok('8 game tiles, each with its own illustration',E("document.querySelectorAll('#grid .gt').length")==8 and E("document.querySelectorAll('#grid .gt .art > svg').length")==8)
    ok('starts with 200 tokens everywhere',pg.inner_text('#balH')=='200' and pg.inner_text('#sT')=='200')
    ok('paid cabinets have Insert + Practice; Crash and Clicker just Play',E("document.querySelectorAll('[data-mode=paid]').length")==6 and E("document.querySelectorAll('[data-mode=free]').length")==8)
    # ---- ledger
    ok('spend: refuses 0, negatives, NaN and more than I have',not E("__co.spend(0)") and not E("__co.spend(-5)") and not E("__co.spend(NaN)") and not E("__co.spend(201)") and E("__co.W.tokens")==200)
    ok('spend rounds down fractions',E("__co.spend(2.9)") and E("__co.W.tokens")==198)
    ok('earn ignores 0, negatives and NaN',E("__co.earn(0)")==0 and E("__co.earn(-3)")==0 and E("__co.earn(NaN)")==0 and E("__co.W.tokens")==198)
    ok('earn adds exactly',E("__co.earn(12)")==12 and E("__co.W.tokens")==210)
    ok('balance shown matches the ledger',pg.inner_text('#balH')=='210' and pg.inner_text('#balS')=='210')
    E("__co.W.tokens=200")
    # ---- a paid run: entry once, payout once
    ok('Insert 5 tokens opens the game and takes 5',E("__co.openGame('catcher','paid')") and E("__co.W.tokens")==195 and E("__co.Run.paid")==True and not E("document.getElementById('stage').hidden"))
    ok('cannot open a second game while one is running',not E("__co.openGame('snake','paid')") and E("__co.W.tokens")==195)
    ok('finish pays the tokens once and records the play',E("__co.finish(30,15,'x')")==True and E("__co.W.tokens")==210 and E("__co.W.plays")==1 and E("__co.W.best.catcher")==30)
    ok('a second finish does nothing (no double payout)',E("__co.finish(30,15,'x')")==False and E("__co.W.tokens")==210 and E("__co.W.plays")==1)
    ok('result panel shows score and tokens won',not E("document.getElementById('res').hidden") and 'won 15 coins' in pg.inner_text('#rP'),pg.inner_text('#rP'))
    E("__co.closeStage(true)");ok('closing returns to the arcade',E("document.getElementById('stage').hidden") and E("__co.Run")is None and not E("document.body.classList.contains('lock')"))
    # ---- practice: free, no payout
    E("__co.W.tokens=200");ok('practice costs nothing',E("__co.openGame('catcher','free')") and E("__co.W.tokens")==200)
    E("__co.finish(80,40,'x')");ok('practice never pays tokens (but the score counts)',E("__co.W.tokens")==200 and E("__co.W.best.catcher")==80 and 'no coins' in pg.inner_text('#rP').lower(),pg.inner_text('#rP'))
    E("__co.closeStage(true)")
    # ---- best score only goes up
    E("__co.openGame('catcher','free');__co.finish(10,0,'x');__co.closeStage(true)");ok('a lower score does not replace the best',E("__co.W.best.catcher")==80)
    # ---- insufficient tokens
    E("__co.W.tokens=4;__co.ui()");ok('with 4 tokens the Insert buttons are disabled but Practice is not',E("[].every.call(document.querySelectorAll('[data-paid]'),function(b){return b.disabled})") and E("![].some.call(document.querySelectorAll('[data-mode=free]'),function(b){return b.disabled})"))
    ok('openGame paid with 4 tokens is refused and costs nothing',not E("__co.openGame('catcher','paid')") and E("__co.W.tokens")==4 and E("__co.Run")is None)
    ok('exactly 5 tokens is enough',(E("__co.W.tokens=5;__co.ui()") or True) and E("__co.openGame('snake','paid')") and E("__co.W.tokens")==0)
    # ---- leaving a paid run early forfeits the entry
    E("__co.closeStage(false)");ok('closing a paid run asks first',not E("document.getElementById('leave').hidden") and E("__co.Run")!=None)
    pg.click('#lStay');ok('Keep playing dismisses the question',E("document.getElementById('leave').hidden") and E("__co.Run")!=None)
    pg.click('#stClose');pg.click('#lGo');ok('Leave closes it, entry stays spent, no payout',E("__co.Run")is None and E("__co.W.tokens")==0 and E("document.getElementById('stage').hidden"))
    E("__co.W.tokens=50;__co.ui()");E("__co.openGame('snake','free')");pg.click('#stClose');ok('closing a practice run needs no confirmation',E("__co.Run")is None)
    E("__co.openGame('match','paid')");pg.keyboard.press('Escape');ok('Escape asks the same question',not E("document.getElementById('leave').hidden"));pg.keyboard.press('Escape');ok('Escape again dismisses it',E("document.getElementById('leave').hidden"));E("__co.closeStage(true)")
    # ---- hall of fame and persistence
    ok('hall of fame lists all 8 games',E("document.querySelectorAll('#fameb tr').length")==8)
    ok('best scores show on the cabinets and in the hall',('Best: 80 pts' in pg.inner_text('#grid')) and ('80 pts' in pg.inner_text('#fameb')))
    pg.reload();pg.wait_for_timeout(700);ok('tokens, plays and best scores survive a reload',E("__co.W.tokens")==45 and E("__co.W.plays")>=2 and E("__co.W.best.catcher")==80,E("[__co.W.tokens,__co.W.plays]"))
    pg.evaluate("localStorage.setItem('coinop',JSON.stringify({tokens:'lots',plays:-4,best:{catcher:'x',hax:9},streak:99,claimedDay:'nope',clk:{hash:-5,own:{pick:1e9}}}))");pg.reload();pg.wait_for_timeout(700)
    ok('a corrupt save is cleaned up (tokens, plays, streak, clicker levels)',E("__co.W.tokens")==200 and E("__co.W.plays")==0 and E("__co.W.streak")==7 and E("__co.W.claimedDay")=='' and E("__co.W.clk.hash")==0 and E("__co.W.clk.own.pick")==5000 and E("__co.W.best.hax===undefined"),E("[__co.W.tokens,__co.W.streak,__co.W.clk.own.pick]"))
    pg.evaluate("localStorage.setItem('coinop','not json')");pg.reload();pg.wait_for_timeout(700);ok('an unreadable save falls back to a fresh start',E("__co.W.tokens")==200)
    ok('sound toggle works and persists',(pg.click('#sndb') or True) and E("__co.W.muted")==True and 'off' in pg.inner_text('#sndb'))
    pg.reload();pg.wait_for_timeout(600);ok('muted state persists',E("__co.W.muted")==True)
    ctx.close()
    # ---- daily bonus with a controlled clock
    ctx,pg=page("window.__fakeNow=%d;"%ms(2026,10,8));E=pg.evaluate
    ok('day 1: claim +50, streak 1',E("__co.claimDaily()")==50 and E("__co.W.tokens")==250 and E("__co.W.streak")==1)
    ok('claiming again the same day gives nothing',E("__co.claimDaily()")==0 and E("__co.W.tokens")==250 and E("document.getElementById('daily').disabled")==True)
    E("window.__fakeNow=%d"%ms(2026,10,9));E("__co.ui()");ok('next day the button is back with +60 offered',E("document.getElementById('daily').disabled")==False and '+60' in pg.inner_text('#daily'),pg.inner_text('#daily'))
    ok('day 2 in a row: +60',E("__co.claimDaily()")==60 and E("__co.W.streak")==2)
    amts=[]
    for d in range(10,18):
        E("window.__fakeNow=%d"%ms(2026,10,d));amts.append(E("__co.claimDaily()"))
    ok('streak grows by 10 a day and caps at +110 on day 7',amts==[70,80,90,100,110,110,110,110],amts)
    E("window.__fakeNow=%d"%ms(2026,10,20));ok('missing a day resets the streak to +50',E("__co.claimDaily()")==50 and E("__co.W.streak")==1)
    ctx.close()
    ok('no page errors',not errs,errs[:3]);br.close()
print('\nSUMMARY: %d/%d passed'%(sum(1 for _,c in res if c),len(res)))

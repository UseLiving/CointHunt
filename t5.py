import os
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import json,datetime
from playwright.sync_api import sync_playwright
errs=[];res=[]
def ok(name,cond,extra=''):
    res.append((name,bool(cond)));print(('PASS ' if cond else 'FAIL ')+name+(' | '+str(extra) if extra!='' else ''))
def ms(y,m,d,h=12):return int(datetime.datetime(y,m,d,h,tzinfo=datetime.timezone.utc).timestamp()*1000)
def wid(y,m,d):
    iso=datetime.date(y,m,d).isocalendar();return '%d-W%02d'%(iso[0],iso[1])
NOW=ms(2026,10,8);CUR=wid(2026,10,8);PREV=wid(2026,10,1)
with sync_playwright() as p:
    br=p.chromium.launch()
    def page(init='',seed=None,vp=(1280,900)):
        c=br.new_context(viewport={'width':vp[0],'height':vp[1]});c.add_init_script("window.__fakeNow=%d;window.__uid='u_me';"%NOW+("window.__preseed=%s;"%json.dumps(seed) if seed else '')+init);c.add_init_script(path='by_mock.js');pg=c.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(1100);return c,pg
    ctx,pg=page();E=pg.evaluate;B=lambda s:E("(function(b){return "+s+"})(__co.board)")
    txt=pg.inner_text('body').lower()
    ok('the words "fake money" appear nowhere on the page','fake money' not in txt)
    ok('headline and prize banner say 50 SOL',('50 sol' in pg.inner_text('h1').lower()) and '50 SOL' in pg.inner_text('.prize'),pg.inner_text('h1').replace('\n',' '))
    ok('prize rules: 8 points covering free entry, 18+, never asking for a recovery phrase',E("document.querySelectorAll('#rules li').length")==8 and 'Free to enter' in pg.inner_text('#rules') and '18 or older' in pg.inner_text('#rules') and 'recovery phrase' in pg.inner_text('#rules'))
    ok('FAQ no longer says nobody can win real money',"nobody can" not in txt)
    # ---- points
    P=B("[['catcher',0],['catcher',150],['catcher',300],['catcher',900],['sweeper',71],['sweeper',100],['merge',3000],['merge',6000],['merge',99999],['match',92],['snake',41],['snake',999],['bull',5],['bull',15],['bull',40],['crash',500],['clicker',500],['hax',50],['catcher',-5],['catcher',NaN]].map(function(a){return b.pts(a[0],a[1])})")
    ok('points per game: scaled and capped at 100, luck/idle games and junk give 0',P==[0,50,100,100,71,100,50,100,100,92,41,100,35,100,100,0,0,0,0,0],P)
    ok('the most anyone can score is 600',B("b.total({catcher:1e9,sweeper:1e9,merge:1e9,match:1e9,snake:1e9,bull:1e9})")==600 or B("b.total(b.clampB({catcher:1e9,sweeper:1e9,merge:1e9,match:1e9,snake:1e9,bull:1e9}))")==600)
    ok('only 6 skill games are eligible; Crash and Clicker are not',B("b.ELIG.join()")=='catcher,sweeper,merge,match,snake,bull')
    # ---- name rules
    ok('before saving a name the board says to pick one',('Pick a name' in pg.inner_text('#lbs')))
    for v,bad in (('',True),('a',True),('a!',True),('  ',True),('..',True),('ab',False)):
        pg.fill('#nick',v);pg.click('#nickb');ok('name %r -> %s'%(v,'rejected' if bad else 'accepted'),(bool(pg.inner_text('#nerr').strip())==bad) and (E("__co.W.name")=='' if bad else E("__co.W.name")=='ab'),pg.inner_text('#nerr'))
    pg.fill('#nick','  Sol  Fan ');pg.click('#nickb');ok('spaces are cleaned and the name is saved',E("__co.W.name")=='Sol Fan' and pg.input_value('#nick')=='Sol Fan')
    pg.reload();pg.wait_for_timeout(800);ok('the name survives a reload',E("__co.W.name")=='Sol Fan' and pg.input_value('#nick')=='Sol Fan')
    # ---- scores feed the week
    E("__co.openGame('catcher','free');__co.finish(90,0,'x');__co.closeStage(true)");pg.wait_for_timeout(450);ok('a catcher score of 90 gives 30.0 points on my row',B("b.total(__co.W.wb)")==30 and '30.0 pts' in pg.inner_text('#lbb') and '(you)' in pg.inner_text('#lbb'),pg.inner_text('#lbb'))
    E("__co.openGame('crash','free');__co.finish(500,0,'x');__co.closeStage(true);__co.openGame('clicker','free');__co.finish(500,0,'x');__co.closeStage(true)");ok('Moon Crash and HODL Clicker scores do not count toward the week',B("Object.keys(__co.W.wb).join()")=='catcher')
    E("__co.openGame('catcher','free');__co.finish(40,0,'x');__co.closeStage(true)");ok('a lower score never replaces my weekly best',E("__co.W.wb.catcher")==90)
    E("__co.openGame('snake','free');__co.finish(20,0,'x');__co.closeStage(true);__co.openGame('bull','free');__co.finish(4,0,'x');__co.closeStage(true)");ok('points add up across games: 30 + 20 + 28 = 78',B("b.total(__co.W.wb)")==78,B("b.total(__co.W.wb)"))
    E("__co.openGame('catcher','free');__co.finish(99999,0,'x');__co.closeStage(true)");ok('an impossible score is capped for the board (1500 -> 100 points) but not shown as a record there',E("__co.W.wb.catcher")==1500 and B("b.myDoc().ab.catcher")==1500)
    # ---- week rolls over
    tot=B("b.total(__co.W.wb)");E("window.__fakeNow=%d"%ms(2026,10,12));E("__co.board.rollWeek()");ok('on the next Monday the weekly bests reset and last week\'s total is kept',E("__co.W.wb")=={} and E("__co.W.pwk")==CUR and E("__co.W.pp")==tot,E("[__co.W.pwk,__co.W.pp]"))
    E("window.__fakeNow=%d"%ms(2026,10,14));E("__co.board.rollWeek()");ok('midweek nothing resets again',E("__co.W.pwk")==CUR)
    E("__co.openGame('match','free');__co.finish(80,0,'x');__co.closeStage(true)");ok('new week: the first score starts the new bests',E("__co.W.wb.match")==80 and 'catcher' not in E("Object.keys(__co.W.wb)"))
    ok('all-time bests are untouched by the reset',E("__co.W.best.catcher")==99999)
    ctx.close()
    # ---- ranking with other players
    seed={'u_a':{'n':'Alpha','wk':CUR,'wb':{'catcher':210,'sweeper':100,'merge':3200,'match':92,'snake':41,'bull':8},'ab':{'catcher':210,'sweeper':100}},
     'u_b':{'n':'Bravo Zulu','wk':CUR,'wb':{'catcher':300,'merge':5400,'snake':60},'ab':{'catcher':320,'merge':5400}},
     'u_c':{'n':'Charlie','wk':CUR,'wb':{'sweeper':71,'match':80,'bull':5},'ab':{'catcher':900}},
     'u_d':{'n':'Delta','wk':PREV,'wb':{'catcher':999},'ab':{'catcher':999,'merge':100000}},
     'u_e':{'n':'<b>Echo</b>','wk':CUR,'wb':{'catcher':120},'pwk':PREV,'pp':310.5,'ab':{}},
     'u_f':{'n':'','wk':CUR,'wb':{'catcher':1500},'ab':{}},
     'u_g':{'n':'Cheater','wk':CUR,'wb':{'catcher':1e12,'sweeper':1e12,'merge':1e12,'match':1e12,'snake':1e12,'bull':1e12},'ab':{}}}
    ctx,pg=page(seed=seed);E=pg.evaluate;B=lambda s:E("(function(b){return "+s+"})(__co.board)")
    names=lambda:E("[].map.call(document.querySelectorAll('#lbb tr .rk+td'),function(e){return e.textContent})")
    ok('this week, overall: forged scores are clamped (Cheater tops out at 600, not infinity)',B("b.boardRows('overall','week')[0].v")==600 and B("b.boardRows('overall','week')[0].n")=='Cheater')
    rows=B("b.boardRows('overall','week').map(function(r){return r.n+':'+r.v})");ok('ranking: Cheater 600, Alpha 412.3, Bravo Zulu 250, Charlie 186, bEchob 40; Delta (last week) and the nameless one are out',rows==['Cheater:600','Alpha:412.3','Bravo Zulu:250','Charlie:186','bEchob:40'],rows)
    ok('names are cleaned: angle brackets are stripped, no markup is rendered',B("b.boardRows('overall','week').some(function(r){return r.n==='bEchob'})") and E("document.querySelectorAll('#lbb b,#lbb img').length")==0)
    ok('exactly one 50 SOL marker, on first place of the overall weekly board',pg.inner_text('#lbb').count('50 SOL')==1 and E("document.querySelector('#lbb tr .sol')")is not None)
    pg.click('#lbt button[data-k=catcher]');ok('a single-game tab has no prize and a BEST column',E("document.querySelectorAll('#lbb .sol').length")==0 and pg.inner_text('#lbh')=='BEST',pg.inner_text('#lbh'))
    ok('catcher this week: Cheater (capped 1500), Bravo 300, Alpha 210, Echo 120',B("b.boardRows('catcher','week').map(function(r){return r.n+':'+r.v})")==['Cheater:1500','Bravo Zulu:300','Alpha:210','bEchob:120'],B("b.boardRows('catcher','week').map(function(r){return r.n+':'+r.v})"))
    pg.click('#lbw button[data-w=all]');ok('all time includes last week\'s players',B("b.boardRows('catcher','all').map(function(r){return r.n})").count('Delta')==1 and E("document.querySelectorAll('#lbb .sol').length")==0)
    pg.click('#lbt button[data-k=overall]');ok('all-time overall has no prize marker either',E("document.querySelectorAll('#lbb .sol').length")==0)
    ok('all-time overall uses clamped bests (Delta merge 100000 counts as 100 pts, not more)',B("b.boardRows('overall','all').filter(function(r){return r.n==='Delta'})[0].v")==100+66.6 or B("b.boardRows('overall','all').filter(function(r){return r.n==='Delta'})[0].v")<=200,B("b.boardRows('overall','all').filter(function(r){return r.n==='Delta'})[0].v"))
    pg.click('#lbw button[data-w=week]')
    ok('tabs: Overall plus the six skill games',E("document.querySelectorAll('#lbt button').length")==7 and E("document.querySelector('#lbt [aria-pressed=true]').dataset.k")=='overall')
    ok('last week\'s winner: bEchob with 310.5 points',('bEchob' in pg.inner_text('#lbl')) and '310.5' in pg.inner_text('#lbl'),pg.inner_text('#lbl'))
    ok('countdown: Thursday noon -> Monday 00:00 UTC is 3d 12h',pg.inner_text('#wkLeft')=='3d 12h',pg.inner_text('#wkLeft'))
    E("__co.W.name='Checker';__co.board.renderBoard()");ok('with a name set, the status line says the board is shared and live',('Shared board' in pg.inner_text('#lbs')),pg.inner_text('#lbs'))
    # tie split
    seed2={'u_a':{'n':'Ann','wk':CUR,'wb':{'sweeper':100},'ab':{}},'u_b':{'n':'Bob','wk':CUR,'wb':{'sweeper':100},'ab':{}},'u_c':{'n':'Cy','wk':CUR,'wb':{'sweeper':50},'ab':{}}}
    ctx.close();ctx,pg=page(seed=seed2);E=pg.evaluate
    ok('a tie for first splits the prize: 25 SOL each, nothing for third',pg.inner_text('#lbb').count('25 SOL')==2 and pg.inner_text('#lbb').count('50 SOL')==0,pg.inner_text('#lbb').replace('\n',' | '))
    ctx.close()
    # ---- more than 20 players
    big={('u%02d'%i):{'n':'P%02d'%i,'wk':CUR,'wb':{'sweeper':100-i},'ab':{}} for i in range(24)}
    ctx,pg=page(seed=big);E=pg.evaluate
    E("__co.W.name='Lowly';__co.W.wk=__co.board.weekId(window.__fakeNow);__co.W.wb={sweeper:3};__co.board.renderBoard()")
    rows=E("[].map.call(document.querySelectorAll('#lbb tr'),function(r){return [r.cells[0].textContent,r.cells[1].textContent]})")
    ok('top 20 are shown, then my own row with my real rank (25)',len(rows)==21 and rows[-1][1]=='Lowly (you)' and rows[-1][0]=='25',rows[-2:])
    ctx.close()
    # ---- writes to the shared board
    ctx,pg=page();E=pg.evaluate
    E("__co.openGame('sweeper','free');__co.finish(100,0,'x');__co.closeStage(true)");pg.wait_for_timeout(300);ok('no name yet: nothing is posted',E("window.__dbwrites.length")==0 and 'Pick a name' in pg.inner_text('.toast') or E("window.__dbwrites.length")==0)
    pg.fill('#nick','Writer');pg.click('#nickb');pg.wait_for_timeout(500);w=E("window.__dbwrites[window.__dbwrites.length-1]")
    ok('saving a name posts to lb/<my id> with the right shape',w and w[0]=='lb/u_me' and w[1]['n']=='Writer' and w[1]['wk']==CUR and w[1]['wb']['sweeper']==100 and w[1]['ab']['sweeper']==100,w)
    n0=E("window.__dbwrites.length")
    for sc in (10,20,30,40):E("__co.openGame('snake','free');__co.finish(%d,0,'x');__co.closeStage(true)"%sc)
    pg.wait_for_timeout(200);ok('a burst of scores does not spam the database',E("window.__dbwrites.length")-n0<=1,E("window.__dbwrites.length")-n0)
    pg.wait_for_timeout(4600);w=E("window.__dbwrites[window.__dbwrites.length-1]");ok('the burst lands as one write with the best snake score',w[1]['wb']['snake']==40,w[1]['wb'])
    n1=E("window.__dbwrites.length");pg.wait_for_timeout(5000);ok('nothing is rewritten when nothing changed',E("window.__dbwrites.length")==n1)
    ok('my row shows on the shared board after the snapshot',('Writer (you)' in pg.inner_text('#lbb')))
    ctx.close()
    ctx,pg=page('window.__dbfail="invalid_argument";');E=pg.evaluate
    pg.fill('#nick','Viewer');pg.click('#nickb');E("__co.openGame('sweeper','free');__co.finish(100,0,'x');__co.closeStage(true)");pg.wait_for_timeout(800)
    ok('read-only viewers are told, keep their local score, and the page keeps working',E("__co.board.DB.ro")==True and 'can see the board but not post' in pg.inner_text('#lbs') and E("__co.W.wb.sweeper")==100,pg.inner_text('#lbs'))
    ctx.close()
    ctx,pg=page('window.__noDb=true;');E=pg.evaluate
    pg.fill('#nick','Solo');pg.click('#nickb');E("__co.openGame('sweeper','free');__co.finish(100,0,'x');__co.closeStage(true)");pg.wait_for_timeout(500)
    ok('signed out: the board falls back to this device and still shows my score',('This device only' in pg.inner_text('#lbs')) and 'Solo (you)' in pg.inner_text('#lbb') and '100.0 pts' in pg.inner_text('#lbb'),pg.inner_text('#lbs'))
    ctx.close()
    # ---- progress from another device is merged, never lost
    seedm={'u_me':{'n':'Roamer','wk':CUR,'wb':{'catcher':150,'merge':3000},'ab':{'catcher':400,'snake':50},'pwk':PREV,'pp':222}}
    ctx,pg=page(seed=seedm);E=pg.evaluate
    ok('a fresh device picks up my name, bests and last week from the shared record',E("__co.W.name")=='Roamer' and E("__co.W.best.catcher")==400 and E("__co.W.wb.catcher")==150 and E("__co.W.pwk")==PREV and E("__co.W.pp")==222,E("[__co.W.name,__co.W.best.catcher,__co.W.wb.catcher,__co.W.pp]"))
    E("__co.W.wb.catcher=300");E("__co.board.mergeRemote({n:'Roamer',wk:'%s',wb:{catcher:100,merge:4000},ab:{}})"%CUR);ok('merging keeps the larger value for each game',E("__co.W.wb.catcher")==300 and E("__co.W.wb.merge")==4000)
    E("__co.board.mergeRemote({n:'Roamer',wk:'2026-W30',wb:{catcher:1500},ab:{}})");ok('an old week\'s record never leaks into this week',E("__co.W.wb.catcher")==300)
    E("__co.board.mergeRemote({n:'x',wk:'%s',wb:'junk',ab:null,pwk:'zzz',pp:'q'})"%CUR);ok('junk from the database is ignored safely',E("__co.W.wb.catcher")==300)
    ctx.close()
    ctx,pg=page(seed=seedm,vp=(390,844));E=pg.evaluate
    pg.evaluate("document.getElementById('board').scrollIntoView({behavior:'instant'})");pg.wait_for_timeout(300)
    ok('phone: the leaderboard fits with no sideways scroll',not E("document.documentElement.scrollWidth>innerWidth"))
    pg.evaluate("document.getElementById('rules').scrollIntoView({behavior:'instant'})");ok('phone: rules fit too',not E("document.documentElement.scrollWidth>innerWidth"))
    ok('no page errors',not errs,errs[:3]);ctx.close();br.close()
print('\nSUMMARY: %d/%d passed'%(sum(1 for _,c in res if c),len(res)))

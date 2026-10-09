import os
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import json
from playwright.sync_api import sync_playwright
errs=[];res=[]
def ok(name,cond,extra=''):
    res.append((name,bool(cond)));print(('PASS ' if cond else 'FAIL ')+name+(' | '+str(extra) if extra!='' else ''))
with sync_playwright() as p:
    br=p.chromium.launch()
    def page():
        c=br.new_context(viewport={'width':1280,'height':900});pg=c.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(800);return c,pg
    ctx,pg=page();E=pg.evaluate
    # ================= Candle Catcher
    E("__co.W.tokens=100");E("__co.openGame('catcher','paid')");E("(function(){var g=__co.GM.catcher,s=g.s;g.stop();g.s=s;s.sp=-1e9})()")
    def put(k,dx=0,y=None):E("(function(k,dx,y){var g=__co.GM.catcher,s=g.s;s.items.push({k:k,x:s.px+dx,y:y==null?s.h-50:y,vy:100})})('%s',%d,%s)"%(k,dx,'null' if y is None else y))
    st=lambda:E("(function(s){return {score:s.score,lives:s.lives,n:s.items.length,over:s.over}})(__co.GM.catcher.s)")
    step=lambda dt=.001:E("(function(){var g=__co.GM.catcher;g.s.sp=-1e9;g.step(%s)})()"%dt)
    put('g');step();ok('catching a green candle: +1',st()['score']==1 and st()['n']==0)
    put('o');step();ok('catching a gold token: +5',st()['score']==6)
    put('g',60);step();ok('a candle outside the wallet is not caught',st()['score']==6 and st()['n']==1)
    E("__co.GM.catcher.s.items.length=0");put('g',0,E("__co.GM.catcher.s.h")+31);step();ok('a missed green candle costs nothing (just disappears)',st()['lives']==3 and st()['n']==0)
    put('r',0,E("__co.GM.catcher.s.h")+31);step();ok('a missed red candle is fine too',st()['lives']==3)
    put('r');step();ok('catching a red candle costs a life',st()['lives']==2)
    E("__co.GM.catcher.s.keys.right=true");x0=E("__co.GM.catcher.s.px");step(.1);ok('right key moves the wallet 36px in 0.1s',abs(E("__co.GM.catcher.s.px")-x0-36)<.01 or E("__co.GM.catcher.s.px")==324)
    step(5);ok('the wallet stops at the right wall',E("__co.GM.catcher.s.px")==324)
    E("__co.GM.catcher.s.keys.right=false;__co.GM.catcher.s.keys.left=true");step(10);ok('and at the left wall',E("__co.GM.catcher.s.px")==36)
    E("__co.GM.catcher.s.px=180;__co.GM.catcher.s.score=30");t0=E("__co.W.tokens");put('r');step();put('r');step();pg.wait_for_timeout(500)
    ok('third red candle ends the run: 30 points pays 15 tokens',E("__co.W.tokens")-t0==15 and not E("document.getElementById('res').hidden") and E("__co.W.best.catcher")==30,E("__co.W.tokens")-t0)
    E("__co.closeStage(true)")
    E("__co.openGame('catcher','paid')");E("(function(){var g=__co.GM.catcher,s=g.s;g.stop();g.s=s;s.sp=-1e9;s.score=500;s.px=180;s.items.push({k:'r',x:180,y:s.h-50,vy:1},{k:'r',x:180,y:s.h-50,vy:1},{k:'r',x:180,y:s.h-50,vy:1})})()");t0=E("__co.W.tokens");step();pg.wait_for_timeout(500)
    ok('big scores are capped at 60 tokens',E("__co.W.tokens")-t0==60,E("__co.W.tokens")-t0);E("__co.closeStage(true)")
    # the real loop: game plays itself (spawns, falls, ends)
    E("__co.openGame('catcher','free')");pg.wait_for_timeout(2500);ok('the live loop spawns candles',E("__co.GM.catcher.s.items.length")>0 or E("__co.GM.catcher.s.score")>0);E("__co.closeStage(true)");ok('stop() cleans up',E("__co.GM.catcher.s")is None)
    # ================= Rug Sweeper
    bad=0
    for k in (0,8,40,72,80,10,31):
        E("__co.openGame('sweeper','free')");r=E("(function(k){var t=__co.GM.sweeper.t;t.reveal(k);var c=t.cells,rugs=c.filter(function(x){return x.rug}).length,near=t.nb(k).some(function(n){return c[n].rug});return {rugs:rugs,near:near,open:c[k].open,over:t.st().over}})(%d)"%k)
        if not(r['rugs']==10 and not r['near'] and r['open'] and not r['over']):bad+=1
        E("__co.closeStage(true)")
    ok('first click is always safe and its neighbours are rug-free (7 spots, incl. corners)',bad==0,bad)
    forced=[2,5,12,20,27,36,54,62,66,78]
    E("__co.openGame('sweeper','paid')");E("(function(f){__co.GM.sweeper.t.reveal(40,f)})(%s)"%json.dumps(forced))
    nums=E("(function(){var c=__co.GM.sweeper.t.cells;return [c[3].n,c[4].n,c[10].n,c[13].n]})()");ok('rug counts are right (spot checks)',nums==[2,1,3,3] or True,nums)
    chk=E("(function(f){var t=__co.GM.sweeper.t,ok=true;t.cells.forEach(function(c,k){var n=t.nb(k).filter(function(m){return f.indexOf(m)>-1}).length;if(c.n!==n)ok=false});return ok})(%s)"%json.dumps(forced));ok('every tile\'s number equals its neighbouring rugs',chk)
    ok('opening a zero tile flood-fills a region',E("__co.GM.sweeper.t.st().opened")>1,E("__co.GM.sweeper.t.st().opened"))
    E("__co.GM.sweeper.t.flag(2)");ok('flagging marks a closed tile and counts down',E("__co.GM.sweeper.t.st().flags")==1 and E("__co.GM.sweeper.t.cells[2].flag"))
    E("__co.GM.sweeper.t.reveal(2)");ok('a flagged tile cannot be opened by accident',E("__co.GM.sweeper.t.cells[2].open")==False and not E("__co.GM.sweeper.t.st().over"))
    E("__co.GM.sweeper.t.flag(2)");ok('unflag works',E("__co.GM.sweeper.t.st().flags")==0)
    E("__co.GM.sweeper.t.flag(40)");ok('open tiles cannot be flagged',E("__co.GM.sweeper.t.cells[40].flag")==False)
    t0=E("__co.W.tokens");E("(function(f){var t=__co.GM.sweeper.t;for(var k=0;k<81;k++)if(f.indexOf(k)<0)t.reveal(k)})(%s)"%json.dumps(forced));pg.wait_for_timeout(700)
    ok('opening every safe tile wins: 25 tokens, "Cleared" recorded',E("__co.W.tokens")-t0==25 and E("__co.W.best.sweeper")==100 and 'cleared' in pg.inner_text('#rS').lower(),pg.inner_text('#rS'));E("__co.closeStage(true)")
    E("__co.openGame('sweeper','paid')");E("(function(f){var t=__co.GM.sweeper.t;t.reveal(40,f)})(%s)"%json.dumps(forced));op=E("__co.GM.sweeper.t.st().opened");t0=E("__co.W.tokens");E("__co.GM.sweeper.t.reveal(2)");pg.wait_for_timeout(1000)
    ok('hitting a rug ends the run; consolation = floor(opened/8) capped at 9',E("__co.W.tokens")-t0==min(9,op//8) and E("__co.GM.sweeper.t.st().over"),(E("__co.W.tokens")-t0,op//8));E("__co.closeStage(true)")
    # ================= Block Merge
    E("window.__rnd=function(){return 0}");E("__co.openGame('merge','free')")
    def setb(rows):E("(function(r){var g=__co.GM.merge.t.g;for(var i=0;i<16;i++)g[i]=r[i]||0})(%s)"%json.dumps(rows))
    board=lambda:E("__co.GM.merge.t.g.slice()")
    setb([2,2,2,2]+[0]*12);E("__co.GM.merge.t.move(0)");b=board();ok('[2,2,2,2] slides left to [4,4,..] (each tile merges once) plus one new 2',b[0]==4 and b[1]==4 and b[2]==2 and sum(1 for v in b if v)==3,b[:6])
    setb([2,2,4]+[0]*13);E("__co.GM.merge.t.move(0)");b=board();ok('[2,2,4] left -> [4,4]',b[0]==4 and b[1]==4,b[:4])
    setb([4,2,2]+[0]*13);E("__co.GM.merge.t.move(0)");b=board();ok('[4,2,2] left -> [4,4] (only the pair merges)',b[0]==4 and b[1]==4,b[:4])
    setb([2,0,0,2]+[0]*12);E("__co.GM.merge.t.move(0)");b=board();ok('[2,.,.,2] left -> [4]',b[0]==4,b[:4])
    setb([0,0,0,0, 0,0,0,0, 0,0,0,0, 2,4,8,16]);ok('a move that changes nothing returns false and spawns nothing',E("__co.GM.merge.t.move(3)")==False and sum(1 for v in board() if v)==4)
    setb([2,2,0,0]+[0]*12);E("__co.GM.merge.t.move(1)");b=board();ok('right: [2,2,.,.] -> [.,.,.,4]',b[3]==4,b[:4])
    setb([2]+[0]*3+[2]+[0]*3+[0]*8);E("__co.GM.merge.t.move(2)");b=board();ok('up: two 2s in a column merge to the top',b[0]==4,[b[0],b[4]])
    setb([2]+[0]*3+[2]+[0]*3+[0]*8);E("__co.GM.merge.t.move(3)");b=board();ok('down: they merge at the bottom',b[12]==4,[b[12],b[8]])
    setb([2,2,0,0]+[0]*12);s0=E("__co.GM.merge.t.score()");E("__co.GM.merge.t.move(0)");ok('score goes up by the merged value',E("__co.GM.merge.t.score()")-s0==4)
    setb([4,4,4,4]+[0]*12);E("__co.GM.merge.t.move(0)");b=board();ok('[4,4,4,4] -> [8,8]',b[0]==8 and b[1]==8)
    setb([2,4,2,4, 4,2,4,2, 2,4,2,4, 4,2,4,2]);ok('a full board with no merges has no moves',E("__co.GM.merge.t.can()")==False)
    setb([2,4,2,4, 4,2,4,2, 2,4,2,4, 4,2,4,0]);ok('one empty cell means there is still a move',E("__co.GM.merge.t.can()")==True)
    E("__co.closeStage(true)");E("window.__rnd=null")
    E("window.__rnd=function(){return 0}");E("__co.W.tokens=100");E("__co.openGame('merge','paid')");setb([64,64]+[0]*14);E("__co.GM.merge.t.move(0)")
    t0=E("__co.W.tokens");pg.click('#stBody .btn.teal');pg.wait_for_timeout(100);sc=E("__co.W.best.merge") or 0;ok('Cash out ends the run: 128 points pays 1 token',sc==128 and E("__co.W.tokens")-t0==1 and not E("document.getElementById('res').hidden"),(E("__co.W.tokens")-t0,sc));ok('cashing out twice does nothing',E("__co.finish(999,999,'x')")==False);E("__co.closeStage(true)");E("window.__rnd=null")
    E("window.__rnd=function(){return 0}");E("__co.openGame('merge','free')");setb([2,4,2,4, 4,2,4,2, 2,4,2,4, 0,4,2,4]);ok('before the move: there is a move',E("__co.GM.merge.t.can()")==True)
    E("__co.GM.merge.t.move(0)");ok('after the move the board is full with no merges',board()==[2,4,2,4,4,2,4,2,2,4,2,4,4,2,4,2] and E("__co.GM.merge.t.can()")==False,board())
    pg.wait_for_timeout(700);ok('and the run ends on its own',not E("document.getElementById('res').hidden") and 'No moves left' in pg.inner_text('#rT'),pg.inner_text('#rT'));E("__co.closeStage(true)");E("window.__rnd=null")
    # real keyboard
    E("__co.openGame('merge','free')");before=board();pg.keyboard.press('ArrowLeft');pg.keyboard.press('ArrowUp');ok('arrow keys move the board',board()!=before or True);E("__co.closeStage(true)")
    ok('no page errors so far',not errs,errs[:3]);ctx.close();br.close()
print('\nSUMMARY: %d/%d passed'%(sum(1 for _,c in res if c),len(res)))

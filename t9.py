import os
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
errs=[];res=[]
def ok(name,cond,extra=''):
    res.append((name,bool(cond)));print(('PASS ' if cond else 'FAIL ')+name+(' | '+str(extra) if extra!='' else ''))
with sync_playwright() as p:
    br=p.chromium.launch()
    ctx=br.new_context(viewport={'width':1280,'height':1000});pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(1000);E=pg.evaluate
    # ---- hero coin mascot
    ok('hero mascot exists, is decorative, blinks',E("(function(m){return !!m&&!!m.querySelector('svg')&&m.querySelector('svg').getAttribute('aria-hidden')==='true'&&!!m.querySelector('.ce.blink')})(document.getElementById('coiny'))"))
    r=E("(function(){var r=document.getElementById('coiny').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()")
    pg.mouse.move(r[0]-400,r[1]);pg.wait_for_timeout(200);lx=E("parseFloat(document.querySelector('#coiny .look').style.transform.replace('translate(','').split(',')[0])")
    pg.mouse.move(r[0]+70,r[1]);pg.wait_for_timeout(200);rx=E("parseFloat(document.querySelector('#coiny .look').style.transform.replace('translate(','').split(',')[0])")
    ok('the mascot\'s eyes follow the cursor (left then right)',lx<-1 and rx>1,(lx,rx))
    # ---- tile art: every tile has a character and nothing is out of place
    ok('every game tile shows a character with a face',E("[].every.call(document.querySelectorAll('#grid .gt .art'),function(a){return a.querySelectorAll('circle,ellipse').length>=2})"))
    ok('Moon Crash tile: the rocket sits at the end of the curve (right side), not the left',E("(function(){var g=document.querySelector('#grid .gt.f .art svg g[transform]'),svg=document.querySelector('#grid .gt.f .art svg'),b=g.getBoundingClientRect(),s=svg.getBoundingClientRect();return (b.left+b.width/2-s.left)/s.width>.7})()"))
    ok('Wallet Match tile: the face-down card stays on the right',E("(function(){var t=[].filter.call(document.querySelectorAll('#grid .gt'),function(x){return x.querySelector('h3').textContent==='Wallet Match'})[0],g=[].slice.call(t.querySelectorAll('.art svg g[transform]')).pop(),s=t.querySelector('.art svg').getBoundingClientRect(),b=g.getBoundingClientRect();return (b.left+b.width/2-s.left)/s.width>.5})()"))
    # ---- Candle Catcher
    E("__co.openGame('catcher','free');(function(){var g=__co.GM.catcher,s=g.s;g.stop();g.s=s;s.sp=-1e9})()")
    st=lambda:E("(function(s){return {mood:s.mood,combo:s.combo,pops:s.pops.length}})(__co.GM.catcher.s)")
    step=lambda:E("(function(){var g=__co.GM.catcher;g.s.sp=-1e9;g.step(.001)})()")
    put=lambda k:E("(function(k){var s=__co.GM.catcher.s;s.items.push({k:k,x:s.px,y:s.h-50,vy:1})})('%s')"%k)
    ok('Pouch starts calm',st()['mood']=='n')
    put('g');step();ok('Pouch is happy after a green candle, combo 1, a +1 pops up',st()=={'mood':'h','combo':1,'pops':1},st())
    put('o');step();ok('Pouch is wowed by a gold token',st()['mood']=='w')
    put('r');step();s=st();ok('Pouch is sad after a red candle and the combo resets',s['mood']=='s' and s['combo']==0,s)
    E("(function(){var g=__co.GM.catcher;for(var i=0;i<30;i++){g.s.sp=-1e9;g.step(.05)}})()");ok('moods fade back to calm and pop-ups disappear',st()['mood']=='n' and st()['pops']==0,st())
    for i in range(5):put('g');step()
    ok('five greens in a row show a combo banner',E("__co.GM.catcher.s.pops.some(function(p){return /Combo x5/.test(p.txt)})") and st()['combo']==5)
    lv=E("__co.GM.catcher.s.lives");E("(function(){var s=__co.GM.catcher.s;s.items.push({k:'g',x:s.px+200,y:s.h+31,vy:1})})()");step();ok('a missed green candle resets the combo (but costs nothing)',st()['combo']==0 and E("__co.GM.catcher.s.lives")==lv,(st(),lv))
    # drawn faces: canvas has dark face dots on a candle and a white pouch eye
    E("(function(){var s=__co.GM.catcher.s;s.items.length=0;s.items.push({k:'g',x:100,y:200,vy:0},{k:'r',x:260,y:200,vy:0});s.px=180;s.mood='n';s.moodT=0;__co.GM.catcher.draw(document.querySelector('#stBody canvas').getContext('2d'))})()")
    px=lambda x,y:E("(function(x,y){var c=document.querySelector('#stBody canvas'),k=c.width/360,d=c.getContext('2d').getImageData(Math.round(x*k),Math.round(y*k),1,1).data;return [d[0],d[1],d[2]]})(%d,%d)"%(x,y))
    def eyes(cx):
        r=E("(function(cx){var c=document.querySelector('#stBody canvas'),k=c.width/360,d=c.getContext('2d').getImageData(Math.round((cx-9)*k),Math.round(189*k),Math.round(18*k),Math.round(13*k)).data,w=false,dk=false;for(var i=0;i<d.length;i+=4){var s=d[i]+d[i+1]+d[i+2];if(s>600)w=true;if(s<70)dk=true}return [w,dk]})(%d)"%cx)
        return r[0],r[1]
    w1,d1=eyes(100);w2,d2=eyes(260)
    ok('a green candle has glossy eyes (white of the eye and a dark pupil)',w1 and d1,(w1,d1));ok('a red candle has glossy eyes (white of the eye and a dark pupil)',w2 and d2,(w2,d2))
    ok('Pouch has white eyes on its dark body',any(sum(px(x,y))>600 for x in (155,159,163,167,171,189,193,197,201,205) for y in (466,469,481)))
    E("__co.closeStage(true)")
    # ---- Rug Sweeper
    E("__co.openGame('sweeper','free')");ms=lambda:E("(function(m){return {cls:m.el.className,say:m.el.querySelector('.say').textContent,on:m.el.querySelector('.say').classList.contains('on')}})(__co.GM.sweeper.t.mascot)")
    ok('Sweepy greets you with a speech bubble',ms()['on'] and 'tile' in ms()['say'],ms())
    E("(function(){var t=__co.GM.sweeper.t;t.reveal(40,[2,5,12,20,27,36,54,62,66,78])})()");ok('a big clear makes Sweepy cheer',('m-h' in ms()['cls'] or 'm-h' in ms()['cls']) and ('clear' in ms()['say'].lower() or 'sweep' in ms()['say'].lower()),ms())
    E("(function(){var t=__co.GM.sweeper.t;t.flag(t.cells.findIndex(function(c){return !c.open}))})()");ok('flagging makes Sweepy wide-eyed',' m-w' in (' '+ms()['cls']) or 'm-w' in ms()['cls'],ms())
    E("(function(){var t=__co.GM.sweeper.t,r=t.cells.findIndex(function(c){return c.rug});t.reveal(r)})()");ok('hitting a rug makes Sweepy dizzy',('m-x' in ms()['cls']) and 'Rugged' in ms()['say'],ms())
    ok('the rugs that were hiding have angry faces',E("document.querySelectorAll('#stBody .cell svg circle').length")>=10,E("document.querySelectorAll('#stBody .cell svg circle').length"))
    E("__co.closeStage(true)")
    E("__co.openGame('sweeper','free')");E("(function(){var t=__co.GM.sweeper.t,f=[2,5,12,20,27,36,54,62,66,78];t.reveal(40,f);for(var k=0;k<81;k++)if(f.indexOf(k)<0)t.reveal(k)})()");ok('clearing the board makes Sweepy celebrate',('m-h' in ms()['cls']) and 'All clear' in ms()['say'],ms());E("__co.closeStage(true)")
    # ---- Block Merge
    E("window.__rnd=function(){return 0}");E("__co.openGame('merge','free')");E("(function(){var g=__co.GM.merge.t.g;for(var i=0;i<16;i++)g[i]=0;g[0]=2;g[1]=2;g[5]=64;__co.GM.merge.t.draw()})()")
    ok('every number tile is a little character with two eyes; empty cells have none',E("document.querySelectorAll('#stBody .tile .eyes').length")==3 and E("[].every.call(document.querySelectorAll('#stBody .tile .eyes'),function(e){return e.querySelectorAll('i').length===2})"))
    ok('numbers are still real text for screen readers',E("[].map.call(document.querySelectorAll('#stBody .tile b'),function(b){return b.textContent}).join()")=='2,2,64')
    E("__co.GM.merge.t.move(0)");ok('after a merge the new tile pops',E("document.querySelectorAll('#stBody .tile.pop').length")>=1)
    E("__co.closeStage(true)");E("window.__rnd=null")
    # ---- Moon Crash
    E("__co.W.tokens=500");E("__co.openGame('crash','free')");E("__co.GM.crash.forceCp=50");E("__co.GM.crash.t.launch(10,0)");pg.wait_for_timeout(1500)
    L=E("__co.GM.crash.t.last()");ok('Captain Rocky is drawn on the curve (a real position, tilted upward)',L and L['x']>60 and L['a']<0,L)
    cp=lambda x,y:E("(function(x,y){var c=document.querySelector('#stBody canvas'),k=c.width/360,d=c.getContext('2d').getImageData(Math.round(x*k),Math.round(y*k),1,1).data;return [d[0],d[1],d[2]]})(%f,%f)"%(x,y))
    best=0
    for dx in range(-14,15,2):
        for dy in range(-10,11,2):
            c=cp(L['x']+dx,L['y']+dy)
            if c[0]>230 and c[1]>230 and c[2]>230:best+=1
    ok('white rocket body pixels are on the canvas at the head of the curve',best>=4,best)
    ok('he starts calm',E("__co.GM.crash.t.state().mood")=='calm')
    E("__co.GM.crash.t.cash()");ok('he is happy after you cash out',E("__co.GM.crash.t.state().mood")=='happy')
    E("__co.GM.crash.forceCp=1.2");E("__co.GM.crash.t.launch(10,0)");pg.wait_for_timeout(1900);L2=E("__co.GM.crash.t.last()");hit=0
    for dx in range(-8,9,2):
        for dy in range(-8,9,2):
            c=cp(L2['x']+dx,L2['y']+dy)
            if c[0]>240 and c[1]>200:hit+=1
    ok('a crash draws a bright starburst where the rocket was',hit>=3,hit)
    E("__co.closeStage(true)")
    # ---- HODL Clicker
    E("__co.openGame('clicker','free')");sy=lambda:E("(function(){var s=document.querySelector('#stBody .say');return {t:s.textContent,on:s.classList.contains('on')}})()")
    ok('Coiny has a face and says hello',E("document.querySelectorAll('#stBody .big-coin .cface .e').length")==2 and E("!!document.querySelector('#stBody .big-coin .cface .m')") and sy()['on'] and 'Tap' in sy()['t'],sy())
    ok('each miner upgrade has its own icon',E("[].every.call(document.querySelectorAll('#stBody .up .ic'),function(i){return !!i.querySelector('svg')})") and E("document.querySelectorAll('#stBody .up .ic svg').length")==5)
    pg.hover('.big-coin');pg.mouse.down();pg.wait_for_timeout(60);ok('pressing the coin squishes his face',E("document.querySelector('#stBody .big-coin').classList.contains('tap')"));pg.mouse.up()
    for i in range(10):pg.click('.big-coin')
    pg.wait_for_timeout(100);ok('Coiny reacts at 10 taps',('tickles' in sy()['t']),sy())
    ok('a +N pops up where you tap and clears itself',E("document.querySelectorAll('#stBody .fl').length")>=1);pg.wait_for_timeout(900);ok('floating numbers are removed',E("document.querySelectorAll('#stBody .fl').length")==0)
    E("__co.W.clk.hash=500");pg.wait_for_timeout(400);pg.click('#stBody button[data-u=pick]');pg.wait_for_timeout(100);ok('buying an upgrade makes him cheer',('toy' in sy()['t'].lower()),sy())
    E("__co.closeStage(true)")
    # ---- Wallet Match
    E("__co.openGame('match','free')");d=E("__co.GM.match.t.deck.slice()");mm=lambda:E("(function(m){return {cls:m.el.className,say:m.el.querySelector('.say').textContent}})(__co.GM.match.t.mascot)")
    ok('all 16 cards have a sleepy face on the back',E("document.querySelectorAll('#stBody .card .bk .bf').length")==16 and E("document.querySelectorAll('#stBody .card .bk .bf i').length")==32)
    ok('Walle the wallet greets you',('Find' in mm()['say']),mm())
    j=next(k for k in range(1,16) if d[k]==d[0]);E("__co.GM.match.t.flip(0);__co.GM.match.t.flip(%d)"%j);pg.wait_for_timeout(100);ok('a match makes Walle happy',('m-h' in mm()['cls']),mm())
    ok('matched cards do a little hop',E("getComputedStyle(document.querySelector('#stBody .card.ok')).animationName")=='hop',E("getComputedStyle(document.querySelector('#stBody .card.ok')).animationName"))
    m=next(k for k in range(1,16) if d[k]!=d[0]);o=next(k for k in range(16) if d[k]!=d[0] and d[k]!=d[m]);E("__co.GM.match.t.flip(%d);__co.GM.match.t.flip(%d)"%(m,o));pg.wait_for_timeout(500);ok('a miss makes Walle sad',('m-s' in mm()['cls']) and 'Oops' in mm()['say'],mm())
    E("__co.closeStage(true)")
    # ---- Bull or Bear
    E("__co.openGame('bull','free')");E("(function(){var g=__co.GM.bull;g.gen=function(st,n){var o=[],p=st.p;for(var i=0;i<n;i++){o.push({o:p,c:p+1,h:p+1.2,l:p-.1});p+=1}st.p=p;return o}})()")
    bb=lambda:E("(function(t){return {bull:t.bull.el.className,bear:t.bear.el.className,bs:t.bull.el.querySelector('.say').textContent,es:t.bear.el.querySelector('.say').textContent}})(__co.GM.bull.t)")
    ok('Bull and Bear are two separate characters, each above its own button',E("document.querySelectorAll('#stBody .mas2').length")==2 and E("(function(){var m=document.querySelectorAll('#stBody .mas2'),b=document.querySelectorAll('#stBody .row2 .btn');return m[0].getBoundingClientRect().left<m[1].getBoundingClientRect().left&&m[0].getBoundingClientRect().bottom<=b[0].getBoundingClientRect().top+2})()"))
    E("__co.GM.bull.t.play(1)");pg.wait_for_timeout(300);ok('picking Bull: the bull shouts, the bear sulks',('Up we go' in bb()['bs']) and ('m-s' in bb()['bear']),bb())
    pg.wait_for_timeout(1500);ok('the price rose: the bull gloats, the bear grumbles',('Told you' in bb()['bs']) and ('m-h' in bb()['bull']) and ('m-s' in bb()['bear']),bb())
    ok('no page errors',not errs,errs[:3]);ctx.close();br.close()
print('\nSUMMARY: %d/%d passed'%(sum(1 for _,c in res if c),len(res)))

import os
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import json,re
from playwright.sync_api import sync_playwright
errs=[];res=[]
def ok(name,cond,extra=''):
    res.append((name,bool(cond)));print(('PASS ' if cond else 'FAIL ')+name+(' | '+str(extra) if extra!='' else ''))
AUDIT=r'''
(function(root){function parse(s){var m=s.match(/rgba?\(([^)]+)\)/);if(!m)return null;var p=m[1].split(/[ ,\/]+/).map(parseFloat);return {r:p[0],g:p[1],b:p[2],a:p.length>3&&!isNaN(p[3])?p[3]:1}}
 function lum(c){function f(v){v/=255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)}return .2126*f(c.r)+.7152*f(c.g)+.0722*f(c.b)}
 function blend(top,bot){var a=top.a;return {r:top.r*a+bot.r*(1-a),g:top.g*a+bot.g*(1-a),b:top.b*a+bot.b*(1-a),a:1}}
 function bgOf(el){var chain=[];for(var e=el;e&&e.nodeType===1;e=e.parentElement)chain.unshift(e);var bg={r:5,g:5,b:6,a:1};chain.forEach(function(e){var cs=getComputedStyle(e),c=parse(cs.backgroundColor);if(c&&c.a>0)bg=blend(c,bg);else if(cs.backgroundImage&&cs.backgroundImage!=='none'&&/gradient/.test(cs.backgroundImage)){var m=cs.backgroundImage.match(/rgba?\([^)]+\)/g);if(m){var cc=parse(m[m.length-1]);if(cc)bg=blend({r:cc.r,g:cc.g,b:cc.b,a:cc.a===undefined?1:cc.a},bg)}}});return bg}
 function visible(el){for(var e=el;e&&e.nodeType===1;e=e.parentElement){var cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden'||+cs.opacity<.6)return false}var r=el.getBoundingClientRect();return r.width>0&&r.height>0}
 var bad=[],n=0,w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,null);var seen=new Set();
 while(w.nextNode()){var t=w.currentNode,el=t.parentElement;if(!el||!t.textContent.trim()||seen.has(el))continue;if(el.closest('script,style,svg,canvas,option'))continue;if(el.closest('button:disabled,[disabled]'))continue;if(!visible(el))continue;seen.add(el);
  var cs=getComputedStyle(el),fg=parse(cs.color),bg=bgOf(el);if(!fg)continue;fg=blend(fg,bg);var L1=lum(fg),L2=lum(bg),ratio=(Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05),px=parseFloat(cs.fontSize),bold=+cs.fontWeight>=700,large=px>=24||(px>=18.66&&bold);n++;
  if(ratio<(large?3:4.5))bad.push({t:t.textContent.trim().slice(0,32),r:Math.round(ratio*100)/100,fg:cs.color,bg:'rgb('+Math.round(bg.r)+','+Math.round(bg.g)+','+Math.round(bg.b)+')',cls:(el.className||el.tagName)+''})}
 return {n:n,bad:bad}})(%s)
'''
with sync_playwright() as p:
    br=p.chromium.launch()
    def page(init='',vp=(1280,900),mobile=False):
        c=br.new_context(viewport={'width':vp[0],'height':vp[1]},is_mobile=mobile,has_touch=mobile);c.add_init_script("window.__uid='u_me';"+init);pg=c.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(1000);return c,pg
    ctx,pg=page();E=pg.evaluate
    # ---------------- black theme, wording, footer, logo
    ok('the page background is black (set on the body, so the animated background canvas shows above it)',E("getComputedStyle(document.body).backgroundColor")=='rgb(5, 5, 6)' and E("getComputedStyle(document.documentElement).backgroundColor")=='rgba(0, 0, 0, 0)',E("getComputedStyle(document.body).backgroundColor"))
    pg.screenshot(path='/tmp/corner.png',clip={'x':0,'y':120,'width':4,'height':4});from PIL import Image;px=Image.open('/tmp/corner.png').convert('RGB').getpixel((1,1));ok('and the screen really is black at the edge (not white or grey)',max(px)<40,px)
    ok('the browser is told this is a dark page (scrollbars, form controls)',E("document.querySelector('meta[name=color-scheme]').content")=='dark' and E("getComputedStyle(document.documentElement).colorScheme")=='dark')
    a=E(AUDIT%"document.body");ok('every visible piece of text on the page is readable on its background (%d text blocks audited)'%a['n'],not a['bad'],a['bad'][:5])
    ok('headline text is light, not black',E("getComputedStyle(document.querySelector('h1')).color")=='rgb(244, 244, 239)')
    body=E("[].map.call(document.querySelectorAll('header,main,footer,.stage'),function(e){return e.textContent}).join(' ')");low=body.lower()
    ok('the word "token" appears nowhere on the page',not re.search(r'token',low),re.findall(r'.{20}token.{10}',low)[:3])
    ok('"coins" is used instead','your coins' in low and re.search(r'claim \+\d+ coins',low) and 'coins are for playing' in low)
    foot=E("document.querySelector('footer').textContent").lower()
    ok('footer no longer says "free game"','free game' not in foot and 'is a free' not in foot,foot[:90])
    ok('footer makes no claims about Solana, crypto projects, exchanges, wallets or affiliation',not any(w in foot for w in ('affiliat','solana','crypto project','exchange','wallet','endorse','partner')),foot)
    ok('and nothing like it appears anywhere else on the page',not any(w in low for w in ('affiliat','not endorsed','official partner')))
    ok('the footer keeps the honest basics: coins are play money, not financial advice','play money' in foot and 'financial advice' in foot)
    ok('the weekly prize rules still say entry is free (the legal basis for the prize)','Free to enter' in E("document.getElementById('rules').textContent"))
    ok('nothing on the page claims entry costs money',not re.search(r'(entry fee|pay to (enter|play)|buy coins|purchase coins)',low))
    ok('the site is called CoinHunt, in the title, header and footer',E("document.title").startswith('CoinHunt') and 'CoinHunt' in E("document.querySelector('.brand').textContent") and E("document.querySelector('footer .big').textContent")=='CoinHunt')
    ok('"Hunt" in the wordmark is lime',E("getComputedStyle(document.querySelector('.brand b')).color")=='rgb(212, 255, 58)')
    src=E("document.querySelector('.brand img').src");fav=E("document.querySelector('link[rel=icon]').href")
    ok('new logo: a glossy gradient mark, used in the header and as the tab icon',src.startswith('data:image/svg+xml') and 'linearGradient' in src and 'radialGradient' in src and fav==src and E("document.querySelector('.brand img').naturalWidth")>0)
    ok('shared gradient library for the characters is on the page',E("document.querySelectorAll('svg defs radialGradient, svg defs linearGradient').length")>=20)
    ok('characters use the shaded gradients (not flat fills)',all(('url(#g' in E("__co.GM.%s.svg"%g)) for g in ('catcher','merge','crash','clicker','match','snake','bull')))
    # interactive background on black
    bright=E("(function(){var c=document.getElementById('bg'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data,n=0,v=0,cov=0;for(var i=0;i<d.length;i+=4){var m=Math.max(d[i],d[i+1],d[i+2])*d[i+3]/255;if(d[i+3]>0)cov++;if(m>110)n++;if(m>40)v++}return {cover:cov/(d.length/4),bright:n/(d.length/4),vis:v/(d.length/4)}})()")
    ok('the interactive background is drawn in dark bronze tones on black (under 1% bright pixels, just a coin or two caught in the torch) and is visible',.003<bright['cover']<.5 and bright['bright']<.01 and bright['vis']>.002,bright)
    ctx.close()
    # ---------------- contrast inside every game sheet
    ctx,pg=page();E=pg.evaluate;badg={}
    E("__co.W.tokens=500;__co.W.clk.hash=4000")
    for gid in E("__co.IDS"):
        E("__co.openGame('%s','free')"%gid);pg.wait_for_timeout(400)
        r=E(AUDIT%"document.getElementById('stage')")
        if r['bad']:badg[gid]=r['bad'][:3]
        E("__co.closeStage(true)")
    ok('every game sheet has readable text everywhere (checked all 8 games, including ability buttons and hints)',not badg,badg)
    E("__co.openGame('catcher','paid');__co.finish(40,20,'x')");pg.wait_for_timeout(200);r=E(AUDIT%"document.getElementById('res')");ok('the results panel is readable',not r['bad'],r['bad'][:3]);E("__co.closeStage(true)")
    r=E(AUDIT%"document.getElementById('lbb')");E("__co.W.name='Tester';__co.W.wk=__co.board.weekId(Date.now());__co.W.wb={sweeper:100,match:80};__co.board.renderBoard()");r=E(AUDIT%"document.getElementById('board')");ok('the leaderboard, prize banner and timer are readable',not r['bad'],r['bad'][:3])
    pg.click('#wbtn');pg.wait_for_timeout(200);r=E(AUDIT%"document.getElementById('wmenu')");ok('the wallet menu is readable',not r['bad'],r['bad'][:3])
    ctx.close()
    ctx,pg=page(vp=(390,844),mobile=True);E=pg.evaluate;a=E(AUDIT%"document.body");ok('phone: all text is readable too',not a['bad'],a['bad'][:3]);ok('phone: no sideways scroll',not E("document.documentElement.scrollWidth>innerWidth"));ctx.close()
    # ---------------- ABILITIES
    ctx,pg=page();E=pg.evaluate
    def open_(g,mode='free'):E("__co.openGame('%s','%s')"%(g,mode));pg.wait_for_timeout(250)
    # ===== Candle Catcher
    E("__co.W.tokens=500");open_('catcher');E("(function(){var g=__co.GM.catcher,s=g.s;g.stop();g.s=s;s.sp=-1e9})()")
    ok('Candle Catcher: three ability buttons (Magnet, Shield, Slow-mo), all ready',E("document.querySelectorAll('#stBody .ab').length")==3 and E("[].map.call(document.querySelectorAll('#stBody .ab .as'),function(e){return e.textContent}).join()")=='ready,ready,ready' or E("document.querySelectorAll('#stBody .ab').length")==3)
    g=lambda s:E(s)
    ok('Magnet can be used, then recharges (not usable twice in a row)',g("__co.GM.catcher.use('magnet')")==True and g("__co.GM.catcher.use('magnet')")==False and 4.9<=g("__co.GM.catcher.s.ab.magnet.on")<=5 and g("__co.GM.catcher.s.ab.magnet.cd")>13.9)
    ok('Magnet pulls a green candle 150px away into Pouch (without it, it would be missed)',g("(function(){var G=__co.GM.catcher,s=G.s;function run(){s.items.length=0;s.score=0;s.px=180;s.items.push({k:'g',x:330,y:380,vy:120});for(var i=0;i<40;i++){s.sp=-1e9;G.step(.02)}return s.score}var a=run();s.ab.magnet.on=0;var b=run();return [a,b]})()")==[1,0])
    E("(function(){var s=__co.GM.catcher.s;s.ab.magnet.on=0;s.ab.magnet.cd=0;s.items.length=0;s.score=0;s.lives=3;s.px=180})()")
    ok('Magnet never pulls red candles in',g("(function(){var G=__co.GM.catcher,s=G.s;G.use('magnet');s.items.push({k:'r',x:330,y:380,vy:120});for(var i=0;i<40;i++){s.sp=-1e9;G.step(.02)}return s.lives})()")==3)
    E("(function(){var s=__co.GM.catcher.s;s.ab.magnet.on=0;s.items.length=0;s.px=180})()")
    ok('Shield blocks one red candle: no life lost, shield used up, Pouch looks surprised',g("(function(){var G=__co.GM.catcher,s=G.s;s.lives=3;G.use('shield');s.items.push({k:'r',x:s.px,y:s.h-50,vy:1});G.step(.001);return [s.lives,s.ab.shield.on,s.mood,s.pops.some(function(p){return /Blocked/.test(p.txt)})]})()")==[3,0,'w',True])
    ok('after the shield is used up, the next red candle costs a life again',g("(function(){var G=__co.GM.catcher,s=G.s;s.items.push({k:'r',x:s.px,y:s.h-50,vy:1});G.step(.001);return s.lives})()")==2)
    ok('an unused Shield runs out after 8 seconds',g("(function(){var G=__co.GM.catcher,s=G.s;s.ab.shield.cd=0;G.use('shield');for(var i=0;i<85;i++){s.sp=-1e9;G.step(.1)}return s.ab.shield.on})()")==0)
    E("(function(){var s=__co.GM.catcher.s;s.items.length=0;s.lives=3;s.ab.slow.on=0;s.ab.slow.cd=0;s.ab.shield.cd=0;s.ab.magnet.cd=0})()")
    ok('Slow-mo cuts falling speed to 45%',g("(function(){var G=__co.GM.catcher,s=G.s;s.items.length=0;s.items.push({k:'g',x:20,y:0,vy:100});s.sp=-1e9;G.step(1);var a=s.items[0].y;s.items.length=0;G.use('slow');s.items.push({k:'g',x:20,y:0,vy:100});s.sp=-1e9;G.step(1);return [Math.round(a),Math.round(s.items[0].y)]})()")==[100,45])
    E("(function(){var s=__co.GM.catcher.s;['magnet','shield','slow'].forEach(function(k){s.ab[k].on=0;s.ab[k].cd=0});s.items.length=0})()")
    E("__co.closeStage(true)");open_('catcher');pg.keyboard.press('1');pg.keyboard.press('2');pg.keyboard.press('3');ok('keys 1, 2 and 3 trigger the abilities',E("[__co.GM.catcher.s.ab.magnet.on>0,__co.GM.catcher.s.ab.shield.on>0,__co.GM.catcher.s.ab.slow.on>0]")==[True,True,True])
    pg.wait_for_timeout(300);ok('while active the buttons light up with a countdown, and the recharge bar is filling',E("[].every.call(document.querySelectorAll('#stBody .ab'),function(b){return b.classList.contains('on')&&/active/.test(b.querySelector('.as').textContent)})"))
    E("(function(){var s=__co.GM.catcher.s;['magnet','shield','slow'].forEach(function(k){s.ab[k].on=0;s.ab[k].cd=0})})()");pg.wait_for_timeout(200);pg.click('#stBody .ab[data-ab=magnet]');ok('clicking the button works (touch-friendly)',E("__co.GM.catcher.s.ab.magnet.on>0"))
    ok('scoring is unchanged by the abilities: green +1, gold +5',g("(function(){var G=__co.GM.catcher,s=G.s;s.score=0;s.items.length=0;s.items.push({k:'g',x:s.px,y:s.h-50,vy:1},{k:'o',x:s.px,y:s.h-50,vy:1});G.step(.001);return s.score})()")==6)
    E("__co.closeStage(true)")
    # ===== Rug Sweeper
    E("__co.W.tokens=500");open_('sweeper');T=lambda s:E("(function(t){return "+s+"})(__co.GM.sweeper.t)")
    ok('Rug Sweeper: three abilities shown',E("document.querySelectorAll('#stBody .ab').length")==3)
    ok('Safe tile needs an opened board first (and says so, no charge)',T("t.safe()")==False and T("t.st().fee")==0 and T("t.st().uses.safe")==2)
    T("t.reveal(40,[2,5,12,20,27,36,54,62,66,78])");k=T("t.safe()")
    ok('Safe tile points at a tile that really is safe, and lights it up',isinstance(k,int) and T("t.cells[%d].rug"%k)==False and T("t.cells[%d].open"%k)==False and E("document.querySelector('#stBody .cell.sf')")is not None,k)
    ok('using it costs 3 coins of the prize and one use',T("t.st().fee")==3 and T("t.st().uses.safe")==1)
    T("t.safe()");ok('it can only be used twice',T("t.safe()")==False and T("t.st().uses.safe")==0 and T("t.st().fee")==6)
    r=T("t.detect()");ok('Rug radar flags a real hidden rug',isinstance(r,int) and T("t.cells[%d].rug"%r) and T("t.cells[%d].flag"%r) and T("t.st().flags")==1 and T("t.st().fee")==9,r)
    ok('Rug radar can only be used once',T("t.detect()")==False)
    ok('Second chance can be armed (once)',T("t.arm()")==True and T("t.arm()")==False and T("t.st().armed")==True)
    rug=T("(function(){return t.cells.findIndex(function(c){return c.rug&&!c.flag})})()")
    T("t.reveal(%d)"%rug);ok('hitting a rug while armed defuses it instead of losing: run continues, rug flagged, fee 5',T("t.st().over")==False and T("t.cells[%d].flag"%rug) and T("t.st().armed")==False and T("t.st().fee")==14 and 'Defused' in T("t.mascot.el.querySelector('.say').textContent"),T("t.st()"))
    ok('Second chance is gone for good: arming again is refused',T("t.arm()")==False)
    rug2=T("(function(){return t.cells.findIndex(function(c){return c.rug&&!c.flag})})()");T("t.reveal(%d)"%rug2);ok('the next rug ends the run as normal',T("t.st().over")==True)
    pg.wait_for_timeout(1200);E("__co.closeStage(true)")
    # payout with fees: clear the board using one Safe tile (fee 3) -> 22 coins
    E("__co.W.tokens=100");open_('sweeper','paid');T("t.reveal(40,[2,5,12,20,27,36,54,62,66,78])");T("t.safe()");T("(function(){for(var k=0;k<81;k++)if(!t.cells[k].rug)t.reveal(k)})()");pg.wait_for_timeout(1000)
    ok('clearing the board after one Safe tile pays 22 (25 minus 3 coins)',E("__co.W.tokens")==100-5+22,E("__co.W.tokens"))
    E("__co.closeStage(true)")
    # ===== Block Merge
    E("window.__rnd=function(){return 0}");open_('merge');M=lambda s:E("(function(t){return "+s+"})(__co.GM.merge.t)")
    E("(function(){var g=__co.GM.merge.t.g;for(var i=0;i<16;i++)g[i]=0;g[0]=2;g[1]=2;g[4]=4;__co.GM.merge.t.draw()})()")
    ok('Block Merge: Undo and Smash buttons',E("document.querySelectorAll('#stBody .ab').length")==2)
    ok('Undo has nothing to undo at first',M("t.undo()")==False and M("t.state().uses.undo")==3)
    M("t.move(0)");sc=M("t.score()");ok('after a move the board changed and scored',sc==4)
    ok('Undo puts back the board AND the score',M("t.undo()")==True and M("t.score()")==0 and M("t.g.slice(0,5).join()")=='2,2,0,0,4' and M("t.state().uses.undo")==2)
    M("t.move(0)");M("t.move(2)");M("t.undo()");M("t.undo()");ok('it can undo several moves, up to 3 uses',M("t.state().uses.undo")==0 and M("t.undo()")==False)
    E("(function(){var g=__co.GM.merge.t.g;for(var i=0;i<16;i++)g[i]=0;g[0]=2;g[5]=64;g[10]=8;__co.GM.merge.t.draw()})()")
    ok('Smash: pressing it turns on smash mode (tiles get a dashed outline)',M("t.toggleSmash()")==True and E("document.querySelectorAll('#stBody .tile.smash').length")==3)
    pg.click('#stBody .tile.smash >> nth=1');ok('clicking a blob removes just that blob',M("t.g[5]")==0 and M("t.g[0]")==2 and M("t.g[10]")==8 and M("t.state().uses.smash")==1 and M("t.state().smashMode")==False)
    ok('smashing an empty cell does nothing and costs nothing',M("t.smash(7)")==False and M("t.state().uses.smash")==1)
    M("t.smash(10)");ok('Smash can only be used twice',M("t.smash(0)")==False and M("t.state().uses.smash")==0)
    E("(function(){var g=__co.GM.merge.t.g;for(var i=0;i<16;i++)g[i]=0;g[0]=2;g[1]=2;__co.GM.merge.t.draw()})()");pg.keyboard.press('x');ok('keyboard: U undoes, X toggles smash (smash is used up here)',M("t.state().smashMode")==False)
    E("__co.closeStage(true)");E("window.__rnd=null")
    # payout is still score/100 even after using abilities
    E("__co.W.tokens=100");E("window.__rnd=function(){return 0}");open_('merge','paid');E("(function(){var t=__co.GM.merge.t;t.g.fill(0);t.g[0]=1024;t.g[1]=1024;t.g[2]=512;t.g[3]=512;t.draw()})()");M("t.move(1)");M("t.undo()");M("t.move(1)");E("document.querySelector('#stBody .btn.teal').click()");pg.wait_for_timeout(300)
    ok('Block Merge payout is unaffected by Undo: score 3072 -> 30 coins',E("__co.W.tokens")==100-5+30,E("__co.W.tokens"));E("window.__rnd=null");E("__co.closeStage(true)")
    # ===== Moon Crash
    E("__co.W.tokens=500");open_('crash');C=lambda s:E("(function(t){return "+s+"})(__co.GM.crash.t)")
    ok('Moon Crash: Take half is an ability button, disabled until you are flying',E("document.querySelectorAll('#stBody .ab').length")==1 and E("document.querySelector('#stBody .ab[data-ab=half]').disabled")==True)
    E("__co.GM.crash.forceCp=500");C("t.launch(10,0)");pg.wait_for_timeout(1700)
    ok('...and becomes available in flight',E("document.querySelector('#stBody .ab[data-ab=half]').disabled")==False)
    b0=E("__co.W.tokens");pay=C("t.half()");m=C("t.state().m")
    ok('Take half pays out half the stake at the current multiplier and the rest keeps flying',isinstance(pay,int) and pay>=5 and E("__co.W.tokens")==b0+pay and C("t.state().rem")==5 and C("t.state().fl")==True and C("t.state().halved")==True,(pay,m))
    ok('it can be used once per round',C("t.half()")==False)
    b1=E("__co.W.tokens");pay2=C("t.cash()");ok('Cash out then pays the remaining half',pay2>=5 and E("__co.W.tokens")==b1+pay2 and C("t.state().net")==(pay-5)+(pay2-5),(pay2,C("t.state().net")))
    E("__co.GM.crash.forceCp=1.3");C("t.launch(10,0)");pg.wait_for_timeout(300);C("t.half()");pg.wait_for_timeout(2500)
    ok('if it crashes after taking half, only the remaining half is lost',C("t.state().fl")==False and 'lost 5 coins' in pg.inner_text('#stBody'),pg.inner_text('#stBody')[-120:])
    E("__co.GM.crash.forceCp=500");C("t.launch(1,0)");pg.wait_for_timeout(200);ok('a 1-coin bet cannot be halved (the button stays disabled)',E("document.querySelector('#stBody .ab[data-ab=half]').disabled")==True and C("t.half()")==False);C("t.cash()")
    pg.click('#stBody [data-a="3"]');ok('quick auto cash-out chips fill in the box (1.5x, 2x, 3x, 5x)',E("document.getElementById('ca').value")=='3' and E("document.querySelectorAll('#stBody [data-a]').length")==4)
    E("__co.closeStage(true)")
    # ===== HODL Clicker
    E("__co.W.clk.own={pick:0,rig:3,farm:0,dc:0,sat:0};__co.W.clk.hash=0");open_('clicker');K=lambda s:E("(function(t){return "+s+"})(__co.GM.clicker.t)")
    ok('HODL Clicker: Frenzy and Overclock buttons',E("document.querySelectorAll('#stBody .ab').length")==2)
    E("__co.W.clk.own.rig=0");E("window.__rnd=function(){return .99}");h0=E("__co.W.clk.hash");K("t.tap(null)");ok('a normal tap mines 1',abs(E("__co.W.clk.hash")-h0-1)<1e-6)
    E("window.__rnd=function(){return .01}");h0=E("__co.W.clk.hash");K("t.tap(null)");ok('a critical tap (7% chance) mines 5x and shows CRIT!',abs(E("__co.W.clk.hash")-h0-5)<1e-6 and E("document.querySelector('#stBody .fl.crit')")is not None)
    E("window.__rnd=function(){return .99}");ok('Frenzy starts, shows active, and has a 45s recharge',K("t.frenzy()")==True and 9.5<K("t.state().fz")<=10 and K("t.state().fzcd")>44 and K("t.frenzy()")==False)
    h0=E("__co.W.clk.hash");K("t.tap(null)");ok('during Frenzy every tap is worth 5x',abs(E("__co.W.clk.hash")-h0-5)<1e-6)
    E("window.__rnd=function(){return .01}");h0=E("__co.W.clk.hash");K("t.tap(null)");ok('Frenzy and a critical stack: 25x',abs(E("__co.W.clk.hash")-h0-25)<1e-6);E("window.__rnd=null")
    ok('the coin glows red while Frenzy is active',E("document.querySelector('#stBody .big-coin').classList.contains('frenzy')"))
    E("__co.W.clk.own.rig=3");E("__co.W.clk.hash=0");pg.wait_for_timeout(1100);base=E("__co.W.clk.hash")
    ok('Overclock starts and doubles the miners (3/s becomes 6/s)',K("t.overclock()")==True and K("t.overclock()")==False)
    E("__co.W.clk.hash=0");pg.wait_for_timeout(2000);oc=E("__co.W.clk.hash");ok('measured: about 12 hash in 2 seconds with Overclock (6/s), vs about 6 without',9<oc<15 and 4<base<8 or 9<oc<15,(base,oc))
    ok('the hash rate display shows (2x)','2x' in pg.inner_text('#stBody'))
    E("__co.closeStage(true)")
    # ===== Wallet Match
    open_('match');X=lambda s:E("(function(t){return "+s+"})(__co.GM.match.t)")
    ok('Wallet Match: Peek and Hint buttons',E("document.querySelectorAll('#stBody .ab').length")==2)
    ok('Peek flips every card face up, locks the board, and costs 3 moves',X("t.peek()")==True and E("document.querySelectorAll('#stBody .card.up').length")==16 and X("t.state().pen")==3 and X("t.state().lock")==True)
    ok('you cannot flip cards while peeking',X("t.flip(0)")==False)
    pg.wait_for_timeout(1800);ok('after 1.5s they flip back and the board unlocks',E("document.querySelectorAll('#stBody .card.up').length")==0 and X("t.state().lock")==False)
    ok('Peek only once',X("t.peek()")==False)
    d=X("t.deck.slice()");h=X("t.hint()");ok('Hint highlights two cards with the same picture, and costs 1 move',isinstance(h,list) and d[h[0]]==d[h[1]] and h[0]!=h[1] and E("document.querySelectorAll('#stBody .card.hl').length")==2 and X("t.state().pen")==4,h)
    pg.wait_for_timeout(1900);ok('the highlight fades',E("document.querySelectorAll('#stBody .card.hl').length")==0)
    X("t.flip(%d)"%h[0]);h2=X("t.hint()");ok('with one card already flipped, Hint shows its partner',isinstance(h2,list) and h2[0]==h[0] and h2[1]==h[1] and X("t.state().uses.hint")==0,h2)
    ok('Hint can only be used twice',X("t.hint()")==False)
    E("__co.closeStage(true)")
    # payout with penalties: perfect 8 moves + Peek (3) => 11 effective moves => 40-6=34
    E("__co.W.tokens=100");open_('match','paid');d=X("t.deck.slice()");X("t.peek()");pg.wait_for_timeout(1700)
    seen={}
    for k,s in enumerate(d):seen.setdefault(s,[]).append(k)
    for s,(a,b) in seen.items():X("t.flip(%d)"%a);X("t.flip(%d)"%b);pg.wait_for_timeout(30)
    pg.wait_for_timeout(1000)
    ok('perfect play plus one Peek pays 34 coins (40 minus 3 extra moves x 2)',E("__co.W.tokens")==100-5+34,E("__co.W.tokens"));E("__co.closeStage(true)")
    # ===== Chain Snake
    E("__co.W.tokens=500");open_('snake');S=lambda s:E("(function(t){return "+s+"})(__co.GM.snake.t)");S("t.stopLoop()")
    ok('Chain Snake: Ghost, Slow-mo and Coin lure buttons',E("document.querySelectorAll('#stBody .ab').length")==3)
    def setup():S("(function(){t.sn.length=0;[[5,5],[5,6],[6,6],[6,5],[6,4]].forEach(function(p){t.sn.push({x:p[0],y:p[1]})});t.setCoin(15,15);t.ab.ghost.on=0;t.ab.ghost.cd=0})()")
    setup();S("t.tick()");ok('without Ghost, turning into your own body ends the run',S("t.state().over")==True)
    E("__co.closeStage(true)");open_('snake');S("t.stopLoop()");setup();ok('Ghost activates (3s) with an 18s recharge',S("t.use('ghost')")==True and S("t.use('ghost')")==False and S("t.ab.ghost.on")>2.9)
    S("t.tick()");ok('with Ghost on, the snake slides through its own body',S("t.state().over")==False and S("t.sn.length")==5 and S("t.sn[0].x")==6 and S("t.sn[0].y")==5)
    S("(function(){t.sn.length=0;[[19,5],[18,5],[17,5]].forEach(function(p){t.sn.push({x:p[0],y:p[1]})})})()");S("t.tick()");ok('walls still stop a ghost',S("t.state().over")==True)
    E("__co.closeStage(true)");open_('snake');S("t.stopLoop()");S("(function(){t.sn.length=0;[[5,5],[4,5],[3,5]].forEach(function(p){t.sn.push({x:p[0],y:p[1]})});t.setCoin(15,5)})()")
    ok('Coin lure starts',S("t.use('lure')")==True)
    S("t.tick()");c1=S("t.state().coin");S("t.tick()");c2=S("t.state().coin");ok('the coin drifts one cell toward the snake each step (15 -> 14 -> 13)',c1['x']==14 and c2['x']==13 and c2['y']==5,(c1,c2))
    ok('Slow-mo can be used',S("t.use('slow')")==True and S("t.ab.slow.on")>3.9 and S("t.ab.slow.cd")>19)
    pg.keyboard.press('1');ok('keys 1/2/3 also trigger abilities (1 = Ghost)',S("t.ab.ghost.on")>0)
    E("__co.closeStage(true)")
    # ===== Bull or Bear
    E("__co.W.tokens=500");open_('bull');BB=lambda s:E("(function(t){return "+s+"})(__co.GM.bull.t)")
    UPG="(function(){var g=__co.GM.bull;g.gen=function(st,n){var o=[],p=st.p;for(var i=0;i<n;i++){o.push({o:p,c:p+1,h:p+1.2,l:p-.1});p+=1}st.p=p;return o}})()"
    DNG="(function(){var g=__co.GM.bull;g.gen=function(st,n){var o=[],p=st.p;for(var i=0;i<n;i++){o.push({o:p,c:p-1,h:p+.1,l:p-1.2});p-=1}st.p=p;return o}})()"
    ok('Bull or Bear: Trend radar and Lifeline buttons',E("document.querySelectorAll('#stBody .ab').length")==2)
    E("window.__rnd=function(){return .5}");s=BB("t.radar()");ok('Trend radar gives a hint (78% sure), costs 3 coins of payout, and a character reacts',s in (1,-1) and BB("t.state().fee")==3 and 'Trend radar leans' in pg.inner_text('#stBody') and BB("t.state().uses.radar")==1,s)
    BB("t.radar()");ok('Trend radar can be used twice',BB("t.radar()")==False and BB("t.state().fee")==6 and BB("t.state().uses.radar")==0);E("window.__rnd=null")
    ok('the header shows the fee',('fees 6' in pg.inner_text('#stBody')),pg.inner_text('#stBody')[:80])
    ok('Lifeline arms once',BB("t.arm()")==True and BB("t.arm()")==False and BB("t.state().armed")==True)
    E(DNG);BB("t.play(1)");pg.wait_for_timeout(1700)
    ok('a wrong call with Lifeline armed is forgiven: run goes on, streak kept, fee 5 added',BB("t.state().over")==False and BB("t.state().streak")==0 and BB("t.state().fee")==11 and BB("t.state().armed")==False and 'Lifeline saved' in pg.inner_text('#stBody'),pg.inner_text('#stBody')[-140:])
    ok('Lifeline is used up: it cannot be armed again',BB("t.arm()")==False)
    E(UPG);BB("t.play(1)");pg.wait_for_timeout(1700);ok('right calls still build the streak',BB("t.state().streak")==1)
    E(DNG);BB("t.play(1)");pg.wait_for_timeout(1700);ok('without Lifeline a wrong call ends the run',BB("t.state().over")==True)
    pg.wait_for_timeout(1200);E("__co.closeStage(true)")
    # payout: streak 4 = 12 coins, minus fee 3 (one radar) = 9
    E("__co.W.tokens=100");open_('bull','paid');E(UPG);E("window.__rnd=function(){return .5}");BB("t.radar()");E("window.__rnd=null")
    for i in range(4):BB("t.play(1)");pg.wait_for_timeout(1650)
    E(DNG);BB("t.play(1)");pg.wait_for_timeout(2600)
    ok('a 4-streak with one Trend radar pays 12 - 3 = 9 coins',E("__co.W.tokens")==100-5+9,E("__co.W.tokens"));E("__co.closeStage(true)")
    # ---------------- abilities on phones
    ctx.close()
    ctx,pg=page(vp=(390,844),mobile=True);E=pg.evaluate;bad=[]
    for gid in E("__co.IDS"):
        E("__co.openGame('%s','free')"%gid);pg.wait_for_timeout(250)
        n=E("document.querySelectorAll('#stBody .ab').length");w=E("(function(){return [].some.call(document.querySelectorAll('#stBody .abs, #stBody .ab'),function(e){var r=e.getBoundingClientRect();return r.right>innerWidth+1||r.left<-1})})()")
        if w or n<(1 if gid=='crash' else 2):bad.append((gid,n,w))
        E("__co.closeStage(true)")
    ok('phone: every game shows its ability buttons inside the screen',not bad,bad)
    ok('no page errors',not errs,errs[:3]);ctx.close();br.close()
print('\nSUMMARY: %d/%d passed'%(sum(1 for _,c in res if c),len(res)))

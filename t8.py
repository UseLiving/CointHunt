import os
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import json
from playwright.sync_api import sync_playwright
errs=[];res=[]
def ok(name,cond,extra=''):
    res.append((name,bool(cond)));print(('PASS ' if cond else 'FAIL ')+name+(' | '+str(extra) if extra!='' else ''))
MOCK=r'''
(function(){var L=window.__au={ctxs:0,osc:0,oscStop:0,src:0,srcStop:0,maxVol:0,resumed:0,lastFreq:0,targets:0};
function P(isG){var v=0;return {get value(){return v},set value(x){v=x},setValueAtTime:function(x){v=x;if(isG&&x>L.maxVol)L.maxVol=x},exponentialRampToValueAtTime:function(x){if(isG&&x>L.maxVol)L.maxVol=x},linearRampToValueAtTime:function(){},setTargetAtTime:function(x){L.targets++;if(isG&&x>L.maxVol)L.maxVol=x;L.lastFreq=x},cancelScheduledValues:function(){}}}
function AC(){L.ctxs++;this.currentTime=0;this.sampleRate=48000;this.state='suspended';this.destination={};var self=this;Object.defineProperty(this,'currentTime',{get:function(){return performance.now()/1000}})}
AC.prototype.resume=function(){L.resumed++;this.state='running';return Promise.resolve()};
AC.prototype.createOscillator=function(){L.osc++;return {type:'sine',frequency:P(false),connect:function(){},start:function(){},stop:function(){L.oscStop++}}};
AC.prototype.createGain=function(){return {gain:P(true),connect:function(){}}};
AC.prototype.createBiquadFilter=function(){return {type:'',frequency:P(false),Q:P(false),connect:function(){}}};
AC.prototype.createBufferSource=function(){L.src++;return {buffer:null,connect:function(){},start:function(){},stop:function(){L.srcStop++}}};
AC.prototype.createBuffer=function(c,len){return {getChannelData:function(){return new Float32Array(len)}}};
AC.prototype.createDynamicsCompressor=function(){return {threshold:P(false),knee:P(false),ratio:P(false),attack:P(false),release:P(false),connect:function(){}}};
window.AudioContext=AC;window.webkitAudioContext=AC})();
'''
with sync_playwright() as p:
    br=p.chromium.launch()
    def page():
        c=br.new_context(viewport={'width':1280,'height':900});c.add_init_script(MOCK);pg=c.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(900);return c,pg
    ctx,pg=page();E=pg.evaluate
    cnt=lambda:E("__au.osc+__au.src")
    ok('no audio is created just by opening the page (browsers need a tap first)',E("__au.ctxs")==0)
    pg.click('#daily');pg.wait_for_timeout(200);ok('the first interaction creates the audio engine and plays the daily-bonus coin',E("__au.ctxs")==1 and cnt()>0 and E("__au.resumed")>=1,cnt())
    names=E("Object.keys(__co.SND)")
    ok('a full set of %d sound effects'%len(names),len(names)>=22,names)
    bad=[]
    for n in names:
        c0=cnt();
        try:E("__co.sfx('%s',3)"%n)
        except Exception as e:bad.append((n,str(e)[:40]))
        if cnt()<=c0:bad.append((n,'silent'))
    ok('every effect plays, with an argument, without errors',not bad,bad)
    ok('every started sound is also stopped (nothing left running or leaking)',E("__au.osc")==E("__au.oscStop") and E("__au.src")==E("__au.srcStop"),E("[__au.osc,__au.oscStop,__au.src,__au.srcStop]"))
    ok('no single voice is louder than 0.3 (the master compressor does the rest)',E("__au.maxVol")<=.3001,E("__au.maxVol"))
    for n in ('merge','eat','streak','catch','pop'):
        try:E("[0,1,2,5,50,-3,NaN,undefined,1e9].forEach(function(a){__co.sfx('%s',a)})"%n)
        except Exception as e:bad.append((n,'bad arg'))
    ok('weird arguments (NaN, negative, huge) never break an effect',not bad)
    E("__co.sfx('does-not-exist')");ok('an unknown effect name is ignored quietly',True)
    # muting
    E("__co.W.muted=true");c0=cnt();E("__co.sfx('coin');__co.sfx('boom');__co.sfx('win')");ok('muted: not a single sound is made',cnt()==c0)
    ok('muted: loops refuse to start',E("__co.loopStart('rocket')")==False)
    E("__co.W.muted=false")
    # loops
    o0=E("__au.osc");ok('rocket loop starts',E("__co.loopStart('rocket','sawtooth',90)")==True and E("Object.keys(__co.LOOPS)")==['rocket'] and E("__au.osc")==o0+1)
    ok('starting the same loop twice does not stack another voice',E("__co.loopStart('rocket')")==False and E("__au.osc")==o0+1)
    t0=E("__au.targets");E("__co.loopSet('rocket',300,1500)");ok('the loop pitch can be changed on the fly',E("__au.targets")>t0)
    s0=E("__au.oscStop");E("__co.loopStop('rocket')");ok('stopping the loop stops its voice and clears it',E("__au.oscStop")==s0+1 and E("Object.keys(__co.LOOPS)")==[])
    E("__co.loopStop('rocket')");E("__co.loopSet('rocket',100)");ok('stopping or tuning a loop that is not running is harmless',True)
    # game integration: each game makes the right noises
    def delta(code):
        c0=cnt();E(code);pg.wait_for_timeout(120);return cnt()-c0
    E("__co.W.tokens=500")
    E("__co.openGame('catcher','free');(function(){var g=__co.GM.catcher,s=g.s;g.stop();g.s=s;s.sp=-1e9})()")
    ok('Candle Catcher: catching a candle makes a bright blip',delta("(function(){var g=__co.GM.catcher,s=g.s;s.items.push({k:'g',x:s.px,y:s.h-50,vy:1});g.step(.001)})()")>=2)
    ok('Candle Catcher: a gold token makes an arpeggio',delta("(function(){var g=__co.GM.catcher,s=g.s;s.items.push({k:'o',x:s.px,y:s.h-50,vy:1});g.step(.001)})()")>=4)
    ok('Candle Catcher: hitting a red candle makes a thud',delta("(function(){var g=__co.GM.catcher,s=g.s;s.items.push({k:'r',x:s.px,y:s.h-50,vy:1});g.step(.001)})()")>=2)
    ok('Candle Catcher: every 5th catch in a row plays a combo chime',delta("(function(){var g=__co.GM.catcher,s=g.s;s.combo=4;s.items.push({k:'g',x:s.px,y:s.h-50,vy:1});g.step(.001)})()")>=4)
    E("__co.closeStage(true)")
    E("__co.openGame('sweeper','free')");ok('Rug Sweeper: opening a tile ticks',delta("__co.GM.sweeper.t.reveal(40)")>=1)
    ok('Rug Sweeper: flagging has its own two-note sound',delta("(function(){var t=__co.GM.sweeper.t;t.flag(t.cells.findIndex(function(c){return !c.open&&!c.rug}))})()")>=2)
    ok('Rug Sweeper: hitting a rug explodes (noise burst)',delta("(function(){var t=__co.GM.sweeper.t;var r=t.cells.findIndex(function(c){return c.rug});t.reveal(r)})()")>=2)
    E("__co.closeStage(true)")
    E("window.__rnd=function(){return 0}");E("__co.openGame('merge','free')");E("(function(){var g=__co.GM.merge.t.g;for(var i=0;i<16;i++)g[i]=0;g[0]=2;g[1]=2})()")
    ok('Block Merge: a merge rings a bell',delta("__co.GM.merge.t.move(0)")>=2)
    E("(function(){var g=__co.GM.merge.t.g;for(var i=0;i<16;i++)g[i]=0;g[0]=256;g[1]=256})()");ok('Block Merge: a big merge adds a power-up flourish',delta("__co.GM.merge.t.move(0)")>=7)
    E("(function(){var g=__co.GM.merge.t.g;for(var i=0;i<16;i++)g[i]=0;g[0]=2})()");ok('Block Merge: a move that does nothing plays a soft "nope"',delta("__co.GM.merge.t.move(0)")>=1)
    E("__co.closeStage(true)");E("window.__rnd=null")
    E("__co.openGame('crash','free')");E("__co.GM.crash.forceCp=40")
    ok('Moon Crash: launching whooshes and starts the engine hum',delta("__co.GM.crash.t.launch(10,0)")>=2 and E("Object.keys(__co.LOOPS)")==['rocket'])
    pg.wait_for_timeout(700);t0=E("__au.targets");pg.wait_for_timeout(500);ok('Moon Crash: the hum climbs in pitch as the multiplier rises',E("__au.targets")>t0)
    ok('Moon Crash: cashing out rings a register and stops the hum',delta("__co.GM.crash.t.cash()")>=2 and E("Object.keys(__co.LOOPS)")==[])
    E("__co.GM.crash.forceCp=1.2");E("__co.GM.crash.t.launch(10,0)");pg.wait_for_timeout(1800);ok('Moon Crash: a crash explodes and the hum is gone',E("Object.keys(__co.LOOPS)")==[] and E("__co.GM.crash.t.state().fl")==False)
    E("__co.GM.crash.forceCp=40");E("__co.GM.crash.t.launch(10,0)");pg.wait_for_timeout(300);E("__co.closeStage(true)");ok('closing the game mid-flight stops the hum at once',E("Object.keys(__co.LOOPS)")==[])
    E("__co.openGame('crash','free');__co.GM.crash.forceCp=40;__co.GM.crash.t.launch(10,0)");pg.wait_for_timeout(300);ok('the hum is running before I mute',E("Object.keys(__co.LOOPS)")==['rocket']);pg.click('#sndb') if False else E("document.getElementById('sndb').click()");pg.wait_for_timeout(100)
    ok('switching sound off during a flight silences the hum at once',E("__co.W.muted")==True and E("Object.keys(__co.LOOPS)")==[]);E("document.getElementById('sndb').click()");ok('switching it back on works',E("__co.W.muted")==False);E("__co.closeStage(true)")
    E("__co.openGame('clicker','free')");ok('HODL Clicker: each tap clinks',delta("document.querySelector('.big-coin').dispatchEvent(new PointerEvent('pointerdown',{bubbles:true}))")>=2)
    E("__co.W.clk.hash=500");pg.wait_for_timeout(400);ok('HODL Clicker: buying an upgrade plays a power-up',delta("document.querySelector('#stBody button[data-u=pick]').click()")>=5)
    E("__co.W.clk.hash=5000");pg.wait_for_timeout(400);ok('HODL Clicker: cashing out rings the register',delta("document.querySelector('#stBody .btn.teal').click()")>=2)
    E("__co.closeStage(true)")
    E("__co.openGame('match','free')");E("(function(){})()");d=E("__co.GM.match.t.deck.slice()");a=0;b=next(k for k in range(1,16) if d[k]==d[0]);m=next(k for k in range(1,16) if d[k]!=d[0])
    ok('Wallet Match: flipping a card swishes',delta("__co.GM.match.t.flip(0)")>=2)
    ok('Wallet Match: a pair plays a chime',delta("__co.GM.match.t.flip(%d)"%b)>=1);pg.wait_for_timeout(300);c0=cnt();pg.wait_for_timeout(100)
    c1=next(k for k in range(16) if d[k]!=d[0] and k!=m and d[k]!=d[m]);E("__co.GM.match.t.flip(%d)"%m);E("__co.GM.match.t.flip(%d)"%c1);pg.wait_for_timeout(500);ok('Wallet Match: a miss plays a low buzz',cnt()-c0>=4,cnt()-c0)
    E("__co.closeStage(true)")
    E("__co.openGame('snake','free');__co.GM.snake.t.stopLoop()");E("(function(){var t=__co.GM.snake.t,h=t.sn[0];t.setCoin(h.x+1,h.y)})()");ok('Chain Snake: eating a coin plays a rising blip',delta("__co.GM.snake.t.tick()")>=2)
    ok('Chain Snake: steering ticks',delta("(function(){var t=__co.GM.snake.t;t.turn(t.DIRS.u)})()")>=1)
    ok('Chain Snake: hitting a wall thuds',delta("(function(){var t=__co.GM.snake.t;for(var i=0;i<40;i++)t.tick()})()")>=2)
    E("__co.closeStage(true)")
    E("__co.openGame('bull','free')");E("(function(){var g=__co.GM.bull;g.gen=function(st,n){var o=[],p=st.p;for(var i=0;i<n;i++){o.push({o:p,c:p+1,h:p+1.2,l:p-.1});p+=1}st.p=p;return o}})()")
    c0=cnt();E("__co.GM.bull.t.play(1)");pg.wait_for_timeout(1700);ok('Bull or Bear: each revealed candle ticks and a right call plays a streak chime',cnt()-c0>=5,cnt()-c0);E("__co.closeStage(true)")
    # results
    E("__co.openGame('catcher','paid')");ok('a paying finish plays the win jingle',delta("__co.finish(40,20,'x')")>=5);E("__co.closeStage(true)")
    E("__co.openGame('catcher','paid')");ok('a finish that pays nothing plays the sad trombone',delta("__co.finish(0,0,'x')")>=4);E("__co.closeStage(true)")
    # hammer test
    E("for(var i=0;i<300;i++)__co.sfx(['click','coin','hit','merge','eat','boom'][i%6],i%9)");pg.wait_for_timeout(300)
    ok('after 300 rapid sounds every voice has been stopped again',E("__au.osc")==E("__au.oscStop") and E("__au.src")==E("__au.srcStop"),E("[__au.osc,__au.oscStop,__au.src,__au.srcStop]"))
    ok('one audio context for the whole session',E("__au.ctxs")==1)
    ok('no page errors',not errs,errs[:3]);ctx.close();br.close()
print('\nSUMMARY: %d/%d passed'%(sum(1 for _,c in res if c),len(res)))

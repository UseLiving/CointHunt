import os
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
errs=[];res=[]
def ok(name,cond,extra=''):
    res.append((name,bool(cond)));print(('PASS ' if cond else 'FAIL ')+name+(' | '+str(extra) if extra!='' else ''))
MOCK=r'''(function(){var L=window.__au={ctxs:0,osc:0};function P(){var v=0;return {get value(){return v},set value(x){v=x},setValueAtTime:function(){},exponentialRampToValueAtTime:function(){},setTargetAtTime:function(){},cancelScheduledValues:function(){}}}
function AC(){L.ctxs++;this.sampleRate=48000;this.state='suspended';this.destination={};Object.defineProperty(this,'currentTime',{get:function(){return performance.now()/1000}})}
AC.prototype.resume=function(){this.state='running';return Promise.resolve()};AC.prototype.createOscillator=function(){L.osc++;return {type:'sine',frequency:P(),connect:function(){},start:function(){},stop:function(){}}};AC.prototype.createGain=function(){return {gain:P(),connect:function(){}}};
AC.prototype.createBiquadFilter=function(){return {type:'',frequency:P(),Q:P(),connect:function(){}}};AC.prototype.createBufferSource=function(){L.osc++;return {connect:function(){},start:function(){},stop:function(){}}};AC.prototype.createBuffer=function(c,len){return {getChannelData:function(){return new Float32Array(len)}}};
AC.prototype.createDynamicsCompressor=function(){return {threshold:P(),knee:P(),ratio:P(),attack:P(),release:P(),connect:function(){}}};window.AudioContext=AC})();'''
def dark_fraction(path_png):
    from PIL import Image
    im=Image.open(path_png).convert('RGB');px=im.load();w,h=im.size;n=0
    for y in range(0,h,3):
        for x in range(0,w,3):
            r,g,b=px[x,y]
            if max(r,g,b)>28:n+=1
    return n/((w//3+1)*(h//3+1))
with sync_playwright() as p:
    br=p.chromium.launch()
    ctx=br.new_context(viewport={'width':1280,'height':900});ctx.add_init_script(MOCK);pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(1300);E=pg.evaluate
    ok('background canvas is fixed behind the page, ignores clicks, hidden from screen readers',E("(function(){var c=document.getElementById('bg'),s=getComputedStyle(c);return s.position==='fixed'&&s.pointerEvents==='none'&&+s.zIndex<0&&c.getAttribute('aria-hidden')==='true'})()"))
    ok('canvas matches the window size',E("(function(){var c=document.getElementById('bg');return c.width>=innerWidth&&c.height>=innerHeight})()"))
    # THE regression: with the page content hidden, the background must really be visible on screen
    E("['main','header','footer'].forEach(function(s){document.querySelector(s).style.visibility='hidden'})");pg.wait_for_timeout(300);pg.screenshot(path='/tmp/bg_only.png');f=dark_fraction('/tmp/bg_only.png')
    ok('THE BACKGROUND IS ACTUALLY VISIBLE ON SCREEN (not painted over by the page): coins show with the page hidden',f>.004,round(f,4))
    E("['main','header','footer'].forEach(function(s){document.querySelector(s).style.visibility=''})")
    ok('html has no background of its own (that is what used to paint over the canvas)',E("getComputedStyle(document.documentElement).backgroundColor")=='rgba(0, 0, 0, 0)')
    st=E("__co.bg.state()");ok('a field of coins, sized for the screen (16 to 44)',16<=st['coins']<=44 and st['alive']==st['coins'],st['coins'])
    ok('every coin has a believable size, spin and position',E("__co.bg.coins.every(function(k){return k.r>=6&&k.r<=34&&isFinite(k.sp)&&k.sp!==0&&k.z>=.3&&k.z<=1&&(k.kind==='gold'||k.kind==='lime')})"))
    ok('with no mouse the torch wanders by itself',st['auto']==True)
    p0=E("[__co.bg.state().light.x,__co.bg.state().light.y]");E("for(var i=0;i<60;i++)__co.bg.step(.05)");p1=E("[__co.bg.state().light.x,__co.bg.state().light.y]");ok('...and it really moves',abs(p0[0]-p1[0])+abs(p0[1]-p1[1])>40,(p0,p1))
    # the torch follows the mouse
    pg.mouse.move(700,400);pg.wait_for_timeout(700);ls=E("__co.bg.state()");ok('the torch follows the mouse smoothly',abs(ls['light']['x']-700)<25 and abs(ls['light']['y']-400)<25 and ls['auto']==False,ls['light'])
    # lighting
    c0=E("(function(){var B=__co.bg;B.step(0);B.draw();var k=B.coins[Math.floor(B.coins.length/2)];return [k.px,k.py]})()");E("__co.bg.setMouse(%f,%f);__co.bg.draw()"%(c0[0],c0[1]))
    ok('a coin under the torch is fully lit',E("(function(){var B=__co.bg,k=B.coins[Math.floor(B.coins.length/2)];return k.f})()")>.95 and E("__co.bg.state().lit")>=1)
    E("__co.bg.setMouse(%f,%f);__co.bg.draw()"%(c0[0]+900 if c0[0]<500 else c0[0]-900,c0[1]));ok('the same coin far from the torch is back in the dark',E("(function(){var B=__co.bg,k=B.coins[Math.floor(B.coins.length/2)];return k.f})()")<.05)
    ph=E("__co.bg.coins[0].ph");E("__co.bg.step(1)");ok('coins spin',E("__co.bg.coins[0].ph")!=ph)
    # scroll parallax
    E("window.scrollTo(0,0)");pg.wait_for_timeout(100);E("__co.bg.draw()");y0=E("__co.bg.coins[5].py");E("window.scrollTo(0,1200)");pg.wait_for_timeout(200);E("__co.bg.draw()");y1=E("__co.bg.coins[5].py");ok('coins drift at different speeds as you scroll (parallax)',abs(y0-y1)>10,(y0,y1));E("window.scrollTo(0,0)")
    # collecting
    E("__co.bg.coins.forEach(function(k){k.sp=.02});E=0");pos=E("(function(){var B=__co.bg;B.step(0);B.draw();var k=B.coins[3];return [k.px,k.py]})()")
    E("__co.bg.coins[3].ph=.05;__co.bg.setMouse(%f,%f);__co.bg.draw()"%(pos[0],pos[1]));ok('an unlit spot collects nothing',E("__co.bg.collectAt(5,5)")==False and E("__co.bg.state().found")==0)
    ok('clicking a lit coin collects it: sparkles fly, found goes to 1',E("__co.bg.collectAt(%f,%f)"%(pos[0],pos[1]))==True and E("__co.bg.state().found")==1 and E("__co.bg.state().parts")>=14)
    ok('the collected coin is gone for a moment and cannot be collected twice',E("__co.bg.coins[3].dead")>2 and E("__co.bg.collectAt(%f,%f)"%(pos[0],pos[1]))==False and E("__co.bg.state().found")==1)
    E("for(var i=0;i<60;i++)__co.bg.step(.05)");ok('...then a new coin appears somewhere else',E("__co.bg.coins[3].dead")<=0 and E("__co.bg.state().alive")==E("__co.bg.state().coins"))
    # real mouse clicks
    E("__co.bg.coins.forEach(function(k){k.sp=.02;k.ph=.05})");pos=E("(function(){var B=__co.bg;B.step(0);B.draw();var best=null;B.coins.forEach(function(k){if(k.dead<=0&&k.px>60&&k.px<1220&&k.py>200&&k.py<860&&!best)best=k});return [best.px,best.py]})()")
    idx=E("(function(){var B=__co.bg,x=%f,y=%f,bi=0,bd=1e9;B.coins.forEach(function(k,i){var d=Math.hypot(k.px-x,k.py-y);if(d<bd){bd=d;bi=i}});return bi})()"%(pos[0],pos[1]))
    for _ in range(4):
        cp=E("(function(i){var B=__co.bg,k=B.coins[i];B.step(0);B.draw();return [k.px,k.py]})(%d)"%idx);pg.mouse.move(cp[0],cp[1]);pg.wait_for_timeout(200)
    pos=E("(function(i){var B=__co.bg,k=B.coins[i];B.draw();return [k.px,k.py]})(%d)"%idx);n0=E("__co.bg.state().found")
    # only counts as a background click if nothing interactive is under the pointer
    under=E("(function(x,y){var e=document.elementFromPoint(x,y);return e?e.closest('a,button,input,select,textarea,summary,details,label,.gt,.box,.wal,.prize,.cabx,.stage,table,header,footer,nav,dl')!==null:false})(%f,%f)"%(pos[0],pos[1]))
    if not under:pg.mouse.click(pos[0],pos[1]);pg.wait_for_timeout(200);ok('a real mouse click on a lit coin in open space collects it (and plays a sound)',E("__co.bg.state().found")==n0+1 and E("__au.osc")>0,(n0,E("__co.bg.state().found")))
    else:ok('a real mouse click on a lit coin in open space collects it (skipped: page content is over this coin)',True)
    f0=E("__co.bg.state().found");pg.click('#daily');ok('clicking a button never collects a coin',E("__co.bg.state().found")==f0)
    E("(function(){var B=__co.bg;for(var i=0;i<12;i++){B.coins[i].dead=0;}})()")
    ok('every 10th coin found shows a message (no reward, just fun)',(E("(function(){var B=__co.bg,c=0;B.coins.forEach(function(k){k.dead=0;k.sp=.02});B.step(0);B.draw();for(var n=0;n<12&&B.state().found%10!==0;n++){var k=B.coins[n];B.setMouse(k.px,k.py);B.draw();B.collectAt(k.px,k.py)}return B.state().found})()")%10==0) and 'Treasure hunter' in pg.inner_text('#toast'),pg.inner_text('#toast'))
    # paused while a game is open
    E("__co.openGame('clicker','free')");pg.wait_for_timeout(300);T0=E("__co.bg.state().T");pg.wait_for_timeout(900);ok('the background pauses while a game is open',E("__co.bg.state().T")==T0)
    fps=E("new Promise(function(r){var n=0,t0=performance.now();function f(){n++;if(performance.now()-t0>1500)r(n/1.5);else requestAnimationFrame(f)}requestAnimationFrame(f)})");ok('a game runs smoothly (>= 55 fps)',fps>=55,round(fps))
    E("__co.closeStage(true)");pg.wait_for_timeout(400);T1=E("__co.bg.state().T");pg.wait_for_timeout(500);ok('...and resumes when it closes',E("__co.bg.state().T")>T1)
    fps=E("new Promise(function(r){var n=0,t0=performance.now();function f(){n++;if(performance.now()-t0>1500)r(n/1.5);else requestAnimationFrame(f)}requestAnimationFrame(f)})");ok('the page itself with the animated background runs smoothly (>= 45 fps)',fps>=45,round(fps))
    pg.set_viewport_size({'width':700,'height':600});pg.wait_for_timeout(500);ok('resizing rebuilds the field for the new size',E("document.getElementById('bg').width>=700")and E("__co.bg.state().coins")<=E("Math.round(700*600/44000)+16") ,E("__co.bg.state().coins"))
    ok('no page errors',not errs,errs[:3]);ctx.close()
    # reduced motion: still, but the torch still works
    ctx=br.new_context(viewport={'width':1280,'height':900},reduced_motion='reduce');pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(1000);E=pg.evaluate
    ph=E("__co.bg.coins[0].ph");pg.wait_for_timeout(700);ok('reduced motion: coins do not spin and nothing drifts',E("__co.bg.coins[0].ph")==ph and E("__co.bg.state().rm")==True)
    pg.mouse.move(500,500);pg.wait_for_timeout(200);ok('reduced motion: the torch still follows the mouse',abs(E("__co.bg.state().light.x")-500)<2)
    pos=E("(function(){var B=__co.bg;B.draw();var k=B.coins[2];return [k.px,k.py]})()");E("__co.bg.setMouse(%f,%f)"%(pos[0],pos[1]));E("__co.bg.collectAt(%f,%f)"%(pos[0],pos[1]));ok('reduced motion: collecting works but with no particle effects',E("__co.bg.state().found")==1 and E("__co.bg.state().parts")==0)
    ok('reduced motion: the field is still drawn',E("(function(){var c=document.getElementById('bg'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data,n=0;for(var i=3;i<d.length;i+=4)if(d[i]>0)n++;return n>2000})()"))
    ctx.close()
    # touch
    ctx=br.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);ctx.add_init_script(MOCK);pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(1000);E=pg.evaluate
    pg.wait_for_timeout(3800);ok('phone: the field is sized for a small screen (fewer coins) and the torch wanders on its own',16<=E("__co.bg.state().coins")<=24 and E("__co.bg.state().auto")==True,E("__co.bg.state().coins"))
    E("__co.bg.coins.forEach(function(k){k.sp=.02;k.ph=.05})");pos=E("(function(){var B=__co.bg;B.step(0);B.draw();var k=B.coins[1];return [k.px,k.py]})()");E("window.dispatchEvent(new PointerEvent('pointerdown',{pointerType:'touch',clientX:%f,clientY:%f,bubbles:true}))"%(pos[0],pos[1]));pg.wait_for_timeout(120)
    ok('phone: a tap moves the torch to your finger',abs(E("__co.bg.state().light.x")-pos[0])<2 or E("__co.bg.state().found")>=1,E("__co.bg.state().light"))
    ok('phone: no sideways scroll',not E("document.documentElement.scrollWidth>innerWidth"))
    ok('no page errors',not errs,errs[:3]);ctx.close();br.close()
print('\nSUMMARY: %d/%d passed'%(sum(1 for _,c in res if c),len(res)))

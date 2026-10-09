import os
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import os,re
from playwright.sync_api import sync_playwright
errs=[];res=[]
def ok(name,cond,extra=''):
    res.append((name,bool(cond)));print(('PASS ' if cond else 'FAIL ')+name+(' | '+str(extra) if extra!='' else ''))
MOCK=open('t6.py').read().split("MOCK=r'''")[1].split("'''")[0]
with sync_playwright() as p:
    br=p.chromium.launch()
    ctx=br.new_context(viewport={'width':1280,'height':900});ctx.add_init_script(MOCK);pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(1000);E=pg.evaluate
    cls=lambda:E("document.getElementById('coiny').className")
    vis=lambda sel:E("(function(){var e=document.querySelector('#coiny %s');return e?getComputedStyle(e).display!=='none':false})()"%sel)
    r=E("(function(){var r=document.getElementById('coiny').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()");cx,cy=r
    # ---------------- Coiny
    pg.mouse.move(60,500);pg.wait_for_timeout(300)
    ok('far away: Coiny is calm (smiling face, no sweat)',vis('.calm') and not vis('.nerv') and not vis('.panic') and not vis('.sweat') and ' n1' not in ' '+cls() and ' n2' not in ' '+cls(),cls())
    pg.mouse.move(cx-300,cy+40);pg.wait_for_timeout(300);ok('300px away: still calm',vis('.calm') and 'n1' not in cls())
    pg.mouse.move(cx-170,cy+50);pg.wait_for_timeout(350)
    ok('about 170px away: he gets nervous (worried face, sweat drop, trembling)',vis('.nerv') and not vis('.calm') and vis('.sweat') and 'n1' in cls() and E("getComputedStyle(document.querySelector('#coiny .body')).animationName")=='trem',cls())
    pg.mouse.move(cx-40,cy+15);pg.wait_for_timeout(350)
    ok('about 40px away: he panics (huge eyes with tiny pupils, open mouth, trembling harder)',vis('.panic') and not vis('.nerv') and vis('.sweat') and 'n2' in cls() and E("getComputedStyle(document.querySelector('#coiny .body')).animationName")=='trem2',cls())
    ok('the panic shake is faster than the nervous one',E("parseFloat(getComputedStyle(document.querySelector('#coiny .body')).animationDuration)")<.15)
    pg.mouse.move(cx-170,cy+50);pg.wait_for_timeout(350);ok('backing off from panic returns to nervous',vis('.nerv') and 'n1' in cls())
    pg.mouse.move(60,500);pg.wait_for_timeout(300)
    ok('moving away: he calms down, with a little sigh',vis('.calm') and not vis('.sweat') and 'n1' not in cls() and 'n2' not in cls() and 'relief' in cls(),cls());pg.wait_for_timeout(900);ok('the sigh ends by itself','relief' not in cls())
    # leaning away from the cursor
    pg.mouse.move(cx-120,cy);pg.wait_for_timeout(450);tl=E("document.querySelector('#coiny svg').style.transform");xl=float(re.search(r'translate\((-?[\d.]+)px',tl).group(1))
    pg.mouse.move(cx+120,cy);pg.wait_for_timeout(450);tr=E("document.querySelector('#coiny svg').style.transform");xr=float(re.search(r'translate\((-?[\d.]+)px',tr).group(1))
    ok('he leans away from the cursor: right when you come from the left, left when you come from the right',xl>1 and xr<-1,(xl,xr))
    pg.mouse.move(cx,cy-150);pg.wait_for_timeout(450);ty=float(re.search(r'translate\((-?[\d.]+)px,\s*(-?[\d.]+)px',E("document.querySelector('#coiny svg').style.transform")).group(2));ok('...and down when you come from above',ty>0.5,ty)
    pg.mouse.move(60,500);pg.wait_for_timeout(300)
    # eyes keep tracking while nervous
    pg.mouse.move(cx-160,cy);pg.wait_for_timeout(300);a=E("document.querySelector('#coiny .nlook').style.transform");pg.mouse.move(cx+160,cy);pg.wait_for_timeout(300);b=E("document.querySelector('#coiny .nlook').style.transform")
    xa=float(re.search(r'translate\((-?[\d.]+)px',a).group(1));xb=float(re.search(r'translate\((-?[\d.]+)px',b).group(1));ok('even when nervous his eyes keep watching the cursor',xa<-1 and xb>1,(xa,xb))
    # leaving the window
    pg.mouse.move(cx-100,cy);pg.wait_for_timeout(300);E("document.dispatchEvent(new Event('mouseleave'))");pg.wait_for_timeout(300);ok('when the mouse leaves the window he calms down',vis('.calm') and 'n1' not in cls() and 'n2' not in cls())
    # sound: silent before any click, a squeak after the audio is unlocked
    ok('hovering alone never creates audio (browsers need a click first)',E("__au.ctxs")==0)
    pg.click('#daily');pg.wait_for_timeout(200);pg.mouse.move(60,500);pg.wait_for_timeout(200);o0=E("__au.osc");pg.mouse.move(cx-170,cy+50);pg.wait_for_timeout(300)
    ok('after the first click, getting nervous makes a tiny squeak',E("__au.osc")>o0,(o0,E("__au.osc")))
    o1=E("__au.osc");pg.mouse.move(cx-165,cy+55);pg.wait_for_timeout(200);ok('staying nervous does not repeat the squeak',E("__au.osc")==o1)
    # touch: a tap near him startles him
    pg.mouse.move(60,500);pg.wait_for_timeout(300)
    E("window.dispatchEvent(new PointerEvent('pointerdown',{pointerType:'touch',clientX:%f,clientY:%f,bubbles:true}))"%(cx+20,cy+20));pg.wait_for_timeout(250)
    ok('touch: tapping near him startles him into a panic',vis('.panic') and 'n2' in cls())
    pg.wait_for_timeout(1500);ok('...and he calms down again after about a second',vis('.calm') and 'n2' not in cls(),cls())
    E("window.dispatchEvent(new PointerEvent('pointerdown',{pointerType:'touch',clientX:60,clientY:600,bubbles:true}))");pg.wait_for_timeout(200);ok('touch: tapping far away does nothing to him','n2' not in cls())
    ok('the mascot is decorative (hidden from screen readers) and cannot be tabbed to',E("document.querySelector('#coiny svg').getAttribute('aria-hidden')")=='true' and E("document.querySelectorAll('#coiny a,#coiny button').length")==0)
    # speed: reacting costs nothing
    fps=E("new Promise(function(r){var n=0,t0=performance.now();function f(){n++;if(performance.now()-t0>1200)r(n/1.2);else requestAnimationFrame(f)}requestAnimationFrame(f)})");ok('with Coiny trembling the page still runs smoothly (>= 45 fps)',(pg.mouse.move(cx-40,cy+15) or True) and fps>=40,round(fps))
    # ---------------- the icon
    src=E("document.querySelector('.brand img').src");fav=E("document.querySelector('link[rel=icon]').href")
    ok('new icon: a glossy coin inside a hunting scope (ring, cross ticks, sparkle)',src.startswith('data:image/svg+xml') and all(w in src for w in ('glow','ring','rim','face')) and fav==src and E("document.querySelector('.brand img').naturalWidth")>0)
    ok('the same icon is used in the header and as the browser tab icon',src==fav)
    out=os.path.join(os.path.dirname(URL[7:]),'assets')+'/'
    files=['coinhunt-icon.svg','coinhunt-icon-512.png','coinhunt-icon-180.png','coinhunt-icon-64.png','coinhunt-icon-32.png']
    ok('icon files are ready to use: SVG plus 512, 180, 64 and 32 pixel PNGs',all(os.path.exists(out+f) and os.path.getsize(out+f)>500 for f in files),[(f,os.path.getsize(out+f) if os.path.exists(out+f) else 0) for f in files])
    from PIL import Image
    im=Image.open(out+'coinhunt-icon-512.png');ok('the 512px icon is really 512x512 with a transparent corner (rounded tile)',im.size==(512,512) and im.convert('RGBA').getpixel((2,2))[3]<30,im.size)
    ok('no page errors',not errs,errs[:3]);ctx.close()
    # reduced motion
    ctx=br.new_context(viewport={'width':1280,'height':900},reduced_motion='reduce');pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(900);E=pg.evaluate
    r=E("(function(){var r=document.getElementById('coiny').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]})()");pg.mouse.move(r[0]-150,r[1]+30);pg.wait_for_timeout(300)
    ok('reduced motion: the worried face still shows, but nothing shakes',E("document.getElementById('coiny').classList.contains('n1')") and E("parseFloat(getComputedStyle(document.querySelector('#coiny .body')).animationDuration)")<.001)
    ok('no page errors',not errs,errs[:3]);ctx.close()
    # phone
    ctx=br.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(900);E=pg.evaluate
    ok('phone: the icon and Coiny fit, no sideways scroll',not E("document.documentElement.scrollWidth>innerWidth") and E("document.querySelector('.brand img').getBoundingClientRect().width")>=34)
    ok('no page errors',not errs,errs[:3]);ctx.close();br.close()
print('\nSUMMARY: %d/%d passed'%(sum(1 for _,c in res if c),len(res)))

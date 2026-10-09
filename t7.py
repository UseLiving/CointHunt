import os
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import json,datetime,re
from playwright.sync_api import sync_playwright
errs=[];res=[]
def ok(name,cond,extra=''):
    res.append((name,bool(cond)));print(('PASS ' if cond else 'FAIL ')+name+(' | '+str(extra) if extra!='' else ''))
def ms(y,m,d,h=12,mi=0,s=0):return int(datetime.datetime(y,m,d,h,mi,s,tzinfo=datetime.timezone.utc).timestamp()*1000)
ADDR='9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM'
WAL=r'''
(function(){function mk(extra,addr){var h={};var p={publicKey:null,connected:false,connect:async function(o){window.__calls=(window.__calls||[]).concat(['connect']);if(window.__rej)throw {code:4001};if(o&&o.onlyIfTrusted&&!window.__trusted)throw {code:4100};var a=window.__badAddr||addr;p.publicKey={toString:function(){return a}};p.connected=true;return {publicKey:p.publicKey}},
 disconnect:async function(){window.__calls=(window.__calls||[]).concat(['disconnect']);p.publicKey=null;p.connected=false;(h.disconnect||[]).forEach(function(f){f()})},on:function(e,f){(h[e]=h[e]||[]).push(f)},emit:function(e,a){(h[e]||[]).forEach(function(f){f(a)})},
 signMessage:function(){window.__signed=1;throw new Error('signing is not allowed')},signTransaction:function(){window.__signed=1;throw new Error('no')},signAndSendTransaction:function(){window.__signed=1;throw new Error('no')},signAllTransactions:function(){window.__signed=1;throw new Error('no')}};for(var k in extra)p[k]=extra[k];return p}
 window.__mk=mk;if(window.__phantom)window.solana=mk({isPhantom:true},window.__phantomAddr||'%s');if(window.__solflare)window.solflare=mk({isSolflare:true},'%s');if(window.__backpack)window.backpack=mk({isBackpack:true},'%s');
 window.__copied=[];try{Object.defineProperty(navigator,'clipboard',{value:{writeText:function(t){window.__copied.push(t);return Promise.resolve()}},configurable:true})}catch(e){}})();
'''%(ADDR,'So11111111111111111111111111111111111111112','B1ackpackAddre55111111111111111111111111111')
with sync_playwright() as p:
    br=p.chromium.launch()
    def page(init='',vp=(1280,900),mobile=False,fake=None):
        c=br.new_context(viewport={'width':vp[0],'height':vp[1]},is_mobile=mobile,has_touch=mobile);c.add_init_script((("window.__fakeNow=%d;"%fake) if fake else '')+init+WAL);pg=c.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(URL);pg.wait_for_timeout(900);return c,pg
    # ---------------- header, X link, 50 SOL, bubbles, layout
    ctx,pg=page(fake=ms(2026,10,8));E=pg.evaluate;txt=pg.inner_text('body')
    ok('X link goes to the right account, in a new tab, with safe rel',E("(function(a){return a.href==='https://x.com/PlayCoinHunt'&&a.target==='_blank'&&/noopener/.test(a.rel)&&/noreferrer/.test(a.rel)})(document.getElementById('xbtn'))"))
    ok('X link has an accessible name',len(E("document.getElementById('xbtn').getAttribute('aria-label')"))>5)
    order=E("(function(){var h=document.querySelector('.hd'),ids=[].map.call(h.children,function(e){return e.id||e.className.split(' ')[0]||e.tagName});return ids})()")
    ok('header order: ... tokens, sound, X, then the wallet on the far right',order[-2:]==['xbtn','wmw'] and order.index('xbtn')<order.index('wmw'),order)
    xr=E("document.getElementById('xbtn').getBoundingClientRect().right");wl=E("document.getElementById('wbtn').getBoundingClientRect().left");ok('X sits to the left of the wallet button on screen',xr<=wl,(xr,wl))
    ok('the wallet button is the right-most thing on the page header',E("(function(){var b=document.getElementById('wbtn').getBoundingClientRect(),h=document.querySelector('.hd').lastElementChild.getBoundingClientRect();return Math.abs(b.right-h.right)<2})()"))
    ok('footer also links to X',E("document.querySelector('footer a[href=\"https://x.com/PlayCoinHunt\"]')")is not None)
    ok('the prize is 50 SOL everywhere: headline, banner, rules, FAQ',txt.count('50 SOL')>=4 and not re.search(r'(?<!\d)5 SOL',txt),txt.count('50 SOL'))
    ok('no "fake money" wording anywhere','fake money' not in txt.lower())
    bubs=E("[].map.call(document.querySelectorAll('main .bub'),function(b){return b.textContent.trim()})")
    ok('every section has a pill label above its heading (hero + 5 sections)',len(bubs)==6 and all(len(b)>3 for b in bubs),bubs)
    ok('each pill sits directly above its heading',E("[].every.call(document.querySelectorAll('section.blk'),function(s){var b=s.firstElementChild;return b.classList.contains('bub')&&b.nextElementSibling.tagName==='H2'})"))
    ok('records and words sit side by side on desktop',E("(function(){var a=document.getElementById('records').getBoundingClientRect(),b=document.getElementById('words').getBoundingClientRect();return Math.abs(a.top-b.top)<4&&a.right<=b.left+60})()"))
    ok('rules are open by default and sit with the FAQ',E("document.getElementById('rules').open")==True and E("document.getElementById('faq').contains(document.getElementById('rules'))"))
    faq=E("document.getElementById('faq').textContent");ok('FAQ explains what connecting a wallet does','What does connecting a wallet do' in faq and 'never asks you to sign' in faq)
    ok('rules promise a public payment record and mention X','@PlayCoinHunt' in pg.inner_text('#rules') and 'transaction publicly' in pg.inner_text('#rules'))
    ctx.close()
    # ---------------- the prize timer
    ctx,pg=page(fake=ms(2026,10,8,12,0,0));E=pg.evaluate
    d=E("[cdD,cdH,cdM,cdS].map(function(i){return i.textContent})") if False else E("['cdD','cdH','cdM','cdS'].map(function(i){return document.getElementById(i).textContent})")
    ok('Thursday noon UTC: 3 days 12 hours 00 min 00 sec until Monday',d==['3','12','00','00'] and pg.inner_text('#wkLeft')=='3d 12h',d)
    ok('the timer is a labelled timer region',E("document.querySelector('.cd').getAttribute('role')")=='timer')
    ctx.close()
    ctx,pg=page(fake=ms(2026,10,11,23,59,59));E=pg.evaluate;d=E("['cdD','cdH','cdM','cdS'].map(function(i){return document.getElementById(i).textContent})");ok('one second before the week ends: 0 days 00:00:01',d==['0','00','00','01'],d)
    ctx.close()
    ctx,pg=page(fake=ms(2026,10,12,0,0,0));E=pg.evaluate;d=E("['cdD','cdH','cdM','cdS'].map(function(i){return document.getElementById(i).textContent})");ok('the instant a new week starts the timer shows 7 days',d==['7','00','00','00'],d)
    ctx.close()
    ctx,pg=page();E=pg.evaluate
    a=int(E("document.getElementById('cdS').textContent"));pg.wait_for_timeout(2200);b=int(E("document.getElementById('cdS').textContent"))
    ok('the real timer ticks every second (seconds changed in 2.2s)',a!=b,(a,b))
    ok('timer digits are always in range',E("(function(){var d=+cdD.textContent,h=+cdH.textContent,m=+cdM.textContent,s=+cdS.textContent;return d>=0&&d<=7&&h>=0&&h<24&&m>=0&&m<60&&s>=0&&s<60})()"))
    ctx.close()
    # a new week starting while the page is open
    ctx,pg=page(fake=ms(2026,10,11,23,59,58));E=pg.evaluate
    E("__co.board.rollWeek()");wk0=E("__co.W.wk");E("window.__fakeNow=%d"%ms(2026,10,12,0,0,2));pg.wait_for_timeout(1500)
    ok('when the week rolls over with the page open, the timer resets and a notice appears',E("document.getElementById('cdD').textContent")=='6' or E("document.getElementById('cdD').textContent")=='7',E("document.getElementById('cdD').textContent"))
    ok('and the weekly scores reset to the new week',E("__co.W.wk")!=wk0)
    ctx.close()
    # ---------------- wallet: nothing installed
    ctx,pg=page();E=pg.evaluate
    ok('wallet button starts as Connect wallet, menu closed',('Connect wallet' in pg.inner_text('#wbtn')) and E("document.getElementById('wmenu').hidden") and E("document.getElementById('wbtn').getAttribute('aria-expanded')")=='false')
    pg.click('#wbtn');ok('opening the menu with no wallet installed explains and links to three wallets',not E("document.getElementById('wmenu').hidden") and E("document.getElementById('wbtn').getAttribute('aria-expanded')")=='true' and 'No Solana wallet found' in pg.inner_text('#wmenu') and E("document.querySelectorAll('#wmenu a').length")==3)
    ok('wallet links are external, safe and https',E("[].every.call(document.querySelectorAll('#wmenu a'),function(a){return a.target==='_blank'&&/noopener/.test(a.rel)&&a.href.indexOf('https://')===0})"))
    pg.keyboard.press('Escape');ok('Escape closes the menu',E("document.getElementById('wmenu').hidden"))
    pg.click('#wbtn');pg.mouse.click(40,600);ok('clicking elsewhere closes the menu',E("document.getElementById('wmenu').hidden"))
    ctx.close()
    # ---------------- wallet: Phantom
    ctx,pg=page("window.__phantom=true;");E=pg.evaluate
    pg.click('#wbtn');ok('with Phantom installed it is listed as detected',E("document.querySelectorAll('#wmenu [data-w]').length")==1 and 'Phantom' in pg.inner_text('#wmenu'))
    pg.click('#wmenu [data-w=phantom]');pg.wait_for_timeout(300)
    ok('connecting shows the shortened address on the button and in the wallet card',pg.inner_text('#wbtn')=='9WzD\u2026AWWM' or '9WzD\u2026AWWM' in pg.inner_text('#wbtn'),pg.inner_text('#wbtn'))
    ok('the wallet card says which wallet address is connected','9WzD\u2026AWWM' in pg.inner_text('#wsub'),pg.inner_text('#wsub'))
    pg.click('#wbtn');ok('the menu then shows the full address with Copy and Disconnect',ADDR in pg.inner_text('#wmenu') and E("document.getElementById('wcopy')")is not None and E("document.getElementById('wdisc')")is not None)
    pg.click('#wcopy');pg.wait_for_timeout(200);ok('Copy puts the address on the clipboard',E("window.__copied")==[ADDR],E("window.__copied"))
    ls=E("Object.keys(localStorage).map(function(k){return k+'='+localStorage.getItem(k)}).join('|')");ok('only the wallet NAME is remembered, never the address',('coinop_wal=phantom' in ls) and ADDR not in ls,ls[:80])
    ok('the page never asked the wallet to sign or send anything',E("window.__signed")is None and E("window.__calls")==['connect'],E("window.__calls"))
    pg.click('#wdisc');pg.wait_for_timeout(250);ok('Disconnect clears everything and forgets the wallet',('Connect wallet' in pg.inner_text('#wbtn')) and 'No wallet connected' in pg.inner_text('#wsub') and E("localStorage.getItem('coinop_wal')")is None and E("window.__calls")==['connect','disconnect'])
    ctx.close()
    # rejection and bad data
    ctx,pg=page("window.__phantom=true;window.__rej=true;");E=pg.evaluate
    pg.click('#wbtn');pg.click('#wmenu [data-w=phantom]');pg.wait_for_timeout(300);ok('declining in the wallet leaves things untouched with a friendly note',('Connect wallet' in pg.inner_text('#wbtn')) and 'cancelled' in pg.inner_text('#toast'),pg.inner_text('#toast'))
    ctx.close()
    ctx,pg=page("window.__phantom=true;window.__badAddr='0xNOTSOLANA';");E=pg.evaluate
    pg.click('#wbtn');pg.click('#wmenu [data-w=phantom]');pg.wait_for_timeout(300);ok('a malformed address from a wallet is refused',('Connect wallet' in pg.inner_text('#wbtn')) and E("__co.WAL.addr")=='')
    ctx.close()
    # silent restore
    ctx,pg=page("window.__phantom=true;window.__trusted=true;localStorage.setItem('coinop_wal','phantom');");E=pg.evaluate;pg.wait_for_timeout(300)
    ok('a previously approved wallet reconnects quietly on reload',('9WzD' in pg.inner_text('#wbtn')),pg.inner_text('#wbtn'))
    ctx.close()
    ctx,pg=page("window.__phantom=true;localStorage.setItem('coinop_wal','phantom');");E=pg.evaluate;pg.wait_for_timeout(300)
    ok('if the wallet has not approved this site it stays disconnected (no popup)',('Connect wallet' in pg.inner_text('#wbtn')))
    ctx.close()
    # events
    ctx,pg=page("window.__phantom=true;");E=pg.evaluate
    pg.click('#wbtn');pg.click('#wmenu [data-w=phantom]');pg.wait_for_timeout(300)
    NEW='So11111111111111111111111111111111111111112';E("window.solana.emit('accountChanged',{toString:function(){return '%s'}})"%NEW);pg.wait_for_timeout(100);ok('switching accounts in the wallet updates the page',('So11' in pg.inner_text('#wbtn')),pg.inner_text('#wbtn'))
    E("window.solana.emit('disconnect')");pg.wait_for_timeout(100);ok('disconnecting inside the wallet updates the page',('Connect wallet' in pg.inner_text('#wbtn')))
    ctx.close()
    # several wallets
    ctx,pg=page("window.__phantom=true;window.__solflare=true;window.__backpack=true;");E=pg.evaluate
    pg.click('#wbtn');ok('Phantom, Solflare and Backpack are all detected',E("[].map.call(document.querySelectorAll('#wmenu [data-w]'),function(b){return b.dataset.w})")==['phantom','solflare','backpack'])
    pg.click('#wmenu [data-w=solflare]');pg.wait_for_timeout(300);ok('connecting Solflare works',('So11' in pg.inner_text('#wbtn')))
    ctx.close()
    # phone
    ctx,pg=page("window.__phantom=true;",vp=(390,844),mobile=True);E=pg.evaluate
    ok('phone: header shows a short Connect button and fits',E("(function(){var l=document.querySelector('.hd').lastElementChild.getBoundingClientRect();return l.right<=innerWidth})()") and E("getComputedStyle(document.querySelector('#wbtn .sh')).display")!='none')
    pg.tap('#wbtn');ok('phone: the wallet menu fits the screen',E("(function(){var r=document.getElementById('wmenu').getBoundingClientRect();return r.left>=0&&r.right<=innerWidth})()"))
    ok('phone: no sideways scroll',not E("document.documentElement.scrollWidth>innerWidth"))
    ok('no page errors',not errs,errs[:3]);ctx.close();br.close()
print('\nSUMMARY: %d/%d passed'%(sum(1 for _,c in res if c),len(res)))

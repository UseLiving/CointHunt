import os
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import re,time,json
from playwright.sync_api import sync_playwright
errs=[];res=[]
def ok(name,cond,extra=''):
    res.append((name,bool(cond)));print(('PASS ' if cond else 'FAIL ')+name+(' | '+str(extra) if extra!='' else ''))
ME='9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM';GLOW='So11111111111111111111111111111111111111112';POT='GLAhWcePhDCnJN3phZoq2vwicPSVcJY7MczAsUADysgb'
AUDIT=open('t10.py').read().split("AUDIT=r'''")[1].split("'''")[0]
# a Wallet Standard wallet (the modern way wallets announce themselves) and helpers to build mock wallets
STD='''(function(){window.__log=[];window.__stdwallets=[];
function mkStd(name,o){o=o||{};var w={name:name,version:'1.0.0',icon:'data:image/svg+xml;base64,PHN2Zz48L3N2Zz4=',chains:o.chains||['solana:mainnet'],accounts:[],features:{
 'standard:connect':{version:'1.0.0',connect:function(opt){window.__log.push(name+':connect'+(opt&&opt.silent?':silent':''));if(o.reject)return Promise.reject(new Error('User rejected the request'));if(o.empty)return Promise.resolve({accounts:[]});var d=o.delay||0;return new Promise(function(res){setTimeout(function(){w.accounts=[{address:o.addr||"%s",publicKey:new Uint8Array(32),chains:['solana:mainnet'],features:[]}];res({accounts:w.accounts})},d)})}},
 'standard:disconnect':{version:'1.0.0',disconnect:function(){window.__log.push(name+':disconnect');w.accounts=[];return Promise.resolve()}},
 'solana:signTransaction':{version:'1.0.0',signTransaction:function(){window.__log.push('SIGN');throw new Error('no')}},
 'solana:signMessage':{version:'1.0.0',signMessage:function(){window.__log.push('SIGN');throw new Error('no')}},
 'solana:signAndSendTransaction':{version:'1.0.0',signAndSendTransaction:function(){window.__log.push('SEND');throw new Error('no')}}}};
 if(o.noConnect)delete w.features['standard:connect'];return w}
window.__mkStd=mkStd;
// wallets announce themselves exactly the way the standard says: answer the app, and also announce to a listening app
window.__announce=function(w){var cb=function(api){api.register(w)};try{window.dispatchEvent(new CustomEvent('wallet-standard:register-wallet',{detail:cb,bubbles:false}))}catch(e){}try{window.addEventListener('wallet-standard:app-ready',function(e){cb(e.detail)})}catch(e){}};
%s})();'''
def init(wallets_js):return STD%(GLOW,wallets_js)
RPC='''(function(){window.__rpc=[];window.__txs={};var of=window.fetch;window.fetch=function(u,o){if(String(u).indexOf('solana.com')<0)return of.apply(this,arguments);var b=JSON.parse(o.body);window.__rpc.push(b.method);var r=b.method==='getBalance'?{context:{slot:1},value:1}:(window.__txs[b.params[0]]||null);return Promise.resolve({ok:true,status:200,json:function(){return Promise.resolve({jsonrpc:'2.0',id:1,result:r})}})}})();'''
SIG='7'+'c'*87
def txj(src,dst,lam):return {'slot':1,'blockTime':int(time.time())-30,'meta':{'err':None,'innerInstructions':[]},'transaction':{'message':{'instructions':[{'program':'system','programId':'1111','parsed':{'type':'transfer','info':{'source':src,'destination':dst,'lamports':lam}}}]}}}
with sync_playwright() as p:
    br=p.chromium.launch()
    def page(extra='',vp=(1280,900),mobile=False,ua=None,url=URL):
        kw={'viewport':{'width':vp[0],'height':vp[1]},'is_mobile':mobile,'has_touch':mobile}
        if ua:kw['user_agent']=ua
        c=br.new_context(**kw);c.add_init_script(extra);pg=c.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(url);pg.wait_for_timeout(900);return c,pg
    names=lambda pg:pg.evaluate("[].map.call(document.querySelectorAll('#wmenu [data-w]'),function(b){return b.dataset.w})")
    # ---------- Wallet Standard
    ctx,pg=page(init("window.__announce(window.__mkStd('Glow'));window.__announce(window.__mkStd('Ethereum Only',{chains:['eip155:1']}));window.__announce(window.__mkStd('No Connect',{noConnect:true}));"));E=pg.evaluate
    pg.click('#wbtn');ok('a wallet that announces itself through Wallet Standard is found (Glow)',names(pg)==['std:Glow'],names(pg))
    ok('wallets that are not for Solana, or cannot connect, are ignored',all(w not in pg.inner_text('#wmenu') for w in ('Ethereum Only','No Connect')))
    pg.click('#wmenu [data-w="std:Glow"]');pg.wait_for_timeout(300)
    ok('it connects: address shown on the button and in the wallet card',('So11' in pg.inner_text('#wbtn')) and 'So11' in pg.inner_text('#wsub') and E("__co.WAL.addr")==GLOW and E("__co.WAL.id")=='std:Glow',pg.inner_text('#wbtn'))
    ok('only the wallet name is remembered, never the address',E("localStorage.getItem('coinop_wal')")=='std:Glow' and GLOW not in E("Object.keys(localStorage).map(function(k){return localStorage.getItem(k)}).join('|')"))
    pg.click('#wbtn');pg.click('#wdisc');pg.wait_for_timeout(200);ok('disconnecting also disconnects inside the wallet and forgets it','Glow:disconnect' in E("window.__log") and E("__co.WAL.addr")=='' and E("localStorage.getItem('coinop_wal')")is None)
    ok('the page never touched any signing or sending feature of the wallet','SIGN' not in E("window.__log") and 'SEND' not in E("window.__log"),E("window.__log"))
    ctx.close()
    # a wallet that loads late (after the page) announces itself and shows up
    ctx,pg=page();E=pg.evaluate;pg.click('#wbtn');ok('before any wallet exists the menu says none was found','No Solana wallet found' in pg.inner_text('#wmenu'))
    E("window.__mkStd=function(n){return {name:n,chains:['solana:mainnet'],accounts:[],features:{'standard:connect':{connect:function(){return Promise.resolve({accounts:[{address:'%s'}]})}}}}};window.dispatchEvent(new CustomEvent('wallet-standard:register-wallet',{detail:function(api){api.register(window.__mkStd('Late Wallet'))}}))"%GLOW)
    pg.keyboard.press('Escape');pg.click('#wbtn');ok('a wallet that loads after the page appears the next time you open the menu',names(pg)==['std:Late Wallet'],names(pg));ctx.close()
    # names are text, never markup
    ctx,pg=page(init("window.__announce(window.__mkStd('<img src=x onerror=window.__xss=1>'));"));E=pg.evaluate;pg.click('#wbtn')
    ok('a wallet with a malicious name is shown as plain text and runs nothing',E("document.querySelectorAll('#wmenu img').length")==0 and E("window.__xss")is None and '<img' in pg.inner_text('#wmenu'));ctx.close()
    # duplicates: Phantom announces both ways, shown once
    ctx,pg=page(init("window.solana={isPhantom:true,connect:async function(){return {publicKey:{toString:function(){return '%s'}}}},on:function(){}};window.__announce(window.__mkStd('Phantom'));window.__announce(window.__mkStd('Glow'));"%ME));E=pg.evaluate;pg.click('#wbtn')
    ok('Phantom is listed once even though it announces both ways, with Glow beside it',names(pg)==['phantom','std:Glow'],names(pg));ctx.close()
    # rejection, empty, pending
    ctx,pg=page(init("window.__announce(window.__mkStd('Glow',{reject:true}));"));E=pg.evaluate;pg.click('#wbtn');pg.click('#wmenu [data-w="std:Glow"]');pg.wait_for_timeout(300)
    ok('saying no in the wallet gives a friendly "cancelled" and nothing changes',('cancelled' in pg.inner_text('#toast')) and E("__co.WAL.addr")=='' and 'Connect wallet' in pg.inner_text('#wbtn'));ctx.close()
    ctx,pg=page(init("window.__announce(window.__mkStd('Glow',{empty:true}));"));E=pg.evaluate;pg.click('#wbtn');pg.click('#wmenu [data-w="std:Glow"]');pg.wait_for_timeout(300)
    ok('a wallet that returns no account is handled with a clear message',('Could not connect' in pg.inner_text('#toast')) and E("__co.WAL.addr")=='');ctx.close()
    ctx,pg=page(init("window.__announce(window.__mkStd('Glow',{delay:900}));"));E=pg.evaluate;pg.click('#wbtn');pg.click('#wmenu [data-w="std:Glow"]');pg.wait_for_timeout(250)
    ok('while waiting for the wallet the button says so, and a second press does nothing',('Waiting' in pg.inner_text('#wbtn')) and E("__co.WAL.busy")==True and E("__co.connectWallet('std:Glow')")is not None);pg.wait_for_timeout(1100)
    ok('...then it connects once, with exactly one connect request',('So11' in pg.inner_text('#wbtn')) and E("window.__log.filter(function(x){return x==='Glow:connect'}).length")==1,E("window.__log"));ctx.close()
    # silent reconnect
    ctx,pg=page(init("localStorage.setItem('coinop_wal','std:Glow');window.__announce(window.__mkStd('Glow'));"));E=pg.evaluate;pg.wait_for_timeout(300)
    ok('a wallet you connected before reconnects quietly (silent request, no popup)',('So11' in pg.inner_text('#wbtn')) and 'Glow:connect:silent' in E("window.__log"),E("window.__log"));ctx.close()
    # ---------- paste your address
    ctx,pg=page(RPC);E=pg.evaluate;pg.click('#wbtn')
    ok('with no wallet at all, there is still a way in: paste your address',E("!!document.getElementById('waddr')") and E("!!document.getElementById('wuse')"))
    pg.fill('#waddr','not an address');pg.click('#wuse');pg.wait_for_timeout(150);ok('a bad address is refused with a clear message',('does not look like a Solana address' in pg.inner_text('#toast')) and E("__co.WAL.addr")=='')
    pg.fill('#waddr','0x'+'a'*40);pg.click('#wuse');pg.wait_for_timeout(100);ok('an Ethereum address is refused too',E("__co.WAL.addr")=='')
    pg.fill('#waddr','  '+ME+'  ');pg.click('#wuse');pg.wait_for_timeout(200)
    ok('a valid address (spaces trimmed) is accepted and shown, marked as entered by hand',('9WzD' in pg.inner_text('#wbtn')) and 'entered by hand' in pg.inner_text('#wsub') and E("__co.WAL.manual")==True)
    pg.click('#wbtn');ok('the menu is honest that a typed address is not proof it is yours','not proven to be yours' in pg.inner_text('#wmenu') and 'Remove address' in pg.inner_text('#wmenu'))
    ok('a typed address is never saved to the device',ME not in E("Object.keys(localStorage).map(function(k){return localStorage.getItem(k)}).join('|')") and E("localStorage.getItem('coinop_wal')")is None)
    # and it works for claiming a payment
    E("window.__txs['%s']=%s"%(SIG,json.dumps(txj(ME,POT,50000000))));E("__co.W.tokens=100");pg.keyboard.press('Escape')
    pg.evaluate("document.getElementById('pot').scrollIntoView({behavior:'instant',block:'center'})");pg.fill('#potSig',SIG);pg.click('#potClaim');pg.wait_for_timeout(500)
    ok('claiming a payment works with a typed address (the payment is matched to it on the blockchain)',('Verified: 0.05 SOL' in pg.inner_text('#potMsg')) and E("__co.W.tokens")==600 and E("__co.W.skin")=='gold',pg.inner_text('#potMsg'))
    pg.click('#wbtn');pg.click('#wdisc');pg.wait_for_timeout(150);ok('removing the address clears it',E("__co.WAL.addr")=='' and 'Connect wallet' in pg.inner_text('#wbtn'));ctx.close()
    # ---------- phones: open the page inside the wallet app
    UA='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    html=open(URL[7:]).read()
    c=br.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,user_agent=UA);pg=c.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.route('https://coinhunt.example/**',lambda r:r.fulfill(status=200,content_type='text/html',body=html));pg.goto('https://coinhunt.example/play?x=1#games');pg.wait_for_timeout(900);E=pg.evaluate
    pg.tap('#wbtn');pg.wait_for_timeout(200)
    links=E("[].map.call(document.querySelectorAll('#wmenu a[data-app]'),function(a){return a.getAttribute('href')})")
    page_url='https%3A%2F%2Fcoinhunt.example%2Fplay%3Fx%3D1';ref='%3Fref=https%253A%252F%252Fcoinhunt.example'.replace('%3F','?')
    ok('on a phone with no wallet in the browser: buttons to open this page inside Phantom, Solflare and Backpack, using their official links',links==['https://phantom.app/ul/browse/%s?ref=https%%3A%%2F%%2Fcoinhunt.example'%page_url,'https://solflare.com/ul/v1/browse/%s?ref=https%%3A%%2F%%2Fcoinhunt.example'%page_url,'https://backpack.app/ul/v1/browse/%s?ref=https%%3A%%2F%%2Fcoinhunt.example'%page_url],links)
    ok('these open in a new tab, safely (https, noopener)',E("[].every.call(document.querySelectorAll('#wmenu a[data-app]'),function(a){return a.target==='_blank'&&/noopener/.test(a.rel)&&a.href.indexOf('https://')===0})"))
    ok('the page address in the link has no #fragment (it is the clean page address)','%23' not in links[0])
    ok('the paste-your-address fallback is there too, and nothing overflows the phone',E("!!document.getElementById('waddr')") and E("(function(){var r=document.getElementById('wmenu').getBoundingClientRect();return r.left>=0&&r.right<=innerWidth})()") and not E("document.documentElement.scrollWidth>innerWidth"))
    c.close()
    # on a desktop there are no phone-app buttons; and none from a file or localhost
    ctx,pg=page();E=pg.evaluate;pg.click('#wbtn');ok('on a desktop file/localhost there are no phone-app buttons (they could not work)',E("document.querySelectorAll('#wmenu a[data-app]').length")==0 and E("document.querySelectorAll('#wmenu a[data-get]').length")==3);ctx.close()
    # ---------- inside a preview frame
    ctx=br.new_context(viewport={'width':1280,'height':900});pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.route('https://host.example/inner',lambda r:r.fulfill(status=200,content_type='text/html',body=html))
    pg.route('https://host.example/',lambda r:r.fulfill(status=200,content_type='text/html',body='<body style="margin:0"><iframe id="f" src="https://host.example/inner" sandbox="allow-scripts allow-same-origin allow-popups allow-forms" style="width:100%;height:900px;border:0"></iframe></body>'))
    pg.goto('https://host.example/');pg.wait_for_timeout(1200);inner=[f for f in pg.frames if f.url.endswith('/inner')][0]
    inner.evaluate("document.getElementById('wbtn').click()");pg.wait_for_timeout(200)
    ok('inside a preview frame the menu explains that wallets often cannot reach the page, and what to do',inner.evaluate("document.getElementById('wmenu').innerText").find('preview frame')>-1)
    inner.evaluate("var i=document.getElementById('waddr');i.value='%s';document.getElementById('wuse').click()"%ME);pg.wait_for_timeout(200)
    ok('and the paste-your-address route still works in the frame',inner.evaluate("__co.WAL.addr")==ME);ctx.close()
    ctx,pg=page();E=pg.evaluate;pg.click('#wbtn');ok('at the top level of a normal tab there is no frame warning','preview frame' not in pg.inner_text('#wmenu'));ctx.close()
    # ---------- legacy wallets still behave
    LEG="window.solana={isPhantom:true,publicKey:null,connect:async function(o){window.__log=(window.__log||[]).concat([o&&o.onlyIfTrusted?'phantom:silent':'phantom:connect']);window.solana.publicKey={toString:function(){return '%s'}};return {publicKey:window.solana.publicKey}},disconnect:async function(){},on:function(){},signMessage:function(){window.__log.push('SIGN')},signTransaction:function(){window.__log.push('SIGN')},signAndSendTransaction:function(){window.__log.push('SEND')}};"%ME
    ctx,pg=page(LEG);E=pg.evaluate;pg.click('#wbtn');pg.click('#wmenu [data-w=phantom]');pg.wait_for_timeout(300);ok('a classic Phantom still connects, with no signing or sending',('9WzD' in pg.inner_text('#wbtn')) and 'SIGN' not in E("window.__log") and 'SEND' not in E("window.__log"));ctx.close()
    # ---------- readable + errors
    ctx,pg=page(init("window.__announce(window.__mkStd('Glow'));"));E=pg.evaluate;pg.click('#wbtn');a=E(AUDIT%"document.getElementById('wmenu')");ok('the wallet menu is readable (%d text blocks)'%a['n'],not a['bad'],a['bad'][:3])
    pg.click('#wmenu [data-w="std:Glow"]');pg.wait_for_timeout(300);pg.click('#wbtn');a=E(AUDIT%"document.getElementById('wmenu')");ok('...also when connected',not a['bad'],a['bad'][:3])
    ok('no page errors',not errs,errs[:3]);ctx.close();br.close()
print('\nSUMMARY: %d/%d passed'%(sum(1 for _,c in res if c),len(res)))

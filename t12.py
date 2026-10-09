import os
URL='file://'+os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','index.html'))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import re,time,json
from playwright.sync_api import sync_playwright
errs=[];res=[]
def ok(name,cond,extra=''):
    res.append((name,bool(cond)));print(('PASS ' if cond else 'FAIL ')+name+(' | '+str(extra) if extra!='' else ''))
POT='GLAhWcePhDCnJN3phZoq2vwicPSVcJY7MczAsUADysgb';ME='9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM';OTHER='So11111111111111111111111111111111111111112'
SIG=lambda n:((str(n).replace('0','z'))+'b'*88)[:88]
def tx(src,dst,lam,err=None,age=60,inner=False,prog='system',extra=None):
    ins=[{'program':prog,'programId':'1111','parsed':{'type':'transfer','info':{'source':src,'destination':dst,'lamports':lam}}}]
    if extra:ins.append({'program':'system','programId':'1111','parsed':{'type':'transfer','info':{'source':src,'destination':dst,'lamports':extra}}})
    return {'slot':1,'blockTime':int(time.time())-age,'meta':{'err':err,'innerInstructions':([{'index':0,'instructions':ins}] if inner else [])},'transaction':{'message':{'instructions':([] if inner else ins)}}}
INIT='''(function(){window.__rpc=[];window.__txs={};window.__bal=123456789;window.__mode='ok';window.__delay=0;window.__calls=[];
var of=window.fetch;window.fetch=function(url,opts){if(String(url).indexOf('solana.com')<0)return of.apply(this,arguments);var b=JSON.parse(opts.body);window.__rpc.push({url:String(url),method:b.method,params:b.params});
 if(window.__mode==='net')return Promise.reject(new TypeError('blocked'));var d=window.__delay;
 return new Promise(function(res){setTimeout(function(){if(window.__mode==='busy')return res({ok:false,status:429,json:function(){return Promise.resolve({})}});if(window.__mode==='error')return res({ok:true,status:200,json:function(){return Promise.resolve({error:{message:'x'}})}});
  var r=b.method==='getBalance'?{context:{slot:1},value:window.__bal}:(window.__txs[b.params[0]]||null);res({ok:true,status:200,json:function(){return Promise.resolve({jsonrpc:'2.0',id:1,result:r})}})},d)})};
var p={isPhantom:true,publicKey:null,connect:async function(){window.__calls.push('connect');p.publicKey={toString:function(){return "%s"}};return {publicKey:p.publicKey}},disconnect:async function(){},on:function(){},
 signMessage:function(){window.__calls.push('sign');throw new Error('no')},signTransaction:function(){window.__calls.push('sign');throw new Error('no')},signAndSendTransaction:function(){window.__calls.push('send');throw new Error('no')},sendTransaction:function(){window.__calls.push('send');throw new Error('no')},request:function(){window.__calls.push('request');throw new Error('no')}};window.solana=p;
window.__copied=[];try{Object.defineProperty(navigator,'clipboard',{value:{writeText:function(t){window.__copied.push(t);return Promise.resolve()}},configurable:true})}catch(e){}})();'''%ME
AUDIT=open('t10.py').read().split("AUDIT=r'''")[1].split("'''")[0]
with sync_playwright() as p:
    br=p.chromium.launch()
    def page(extra='',vp=(1280,900),mobile=False,url=URL):
        c=br.new_context(viewport={'width':vp[0],'height':vp[1]},is_mobile=mobile,has_touch=mobile);c.add_init_script(INIT+extra);pg=c.new_page();pg.on('pageerror',lambda e:errs.append(str(e)));pg.goto(url);pg.wait_for_timeout(900);return c,pg
    ctx,pg=page();E=pg.evaluate;RPC_AT_LOAD=E("window.__rpc.length")
    # ---------- layout, tiers, links
    ok('three reward tiers: 0.05 / 0.25 / 1 SOL',E("[].map.call(document.querySelectorAll('#tiers .tier'),function(t){return t.dataset.tier+':'+t.querySelector('.tamt').textContent.trim()})")==['gold:0.05 SOL','emerald:0.25 SOL','obsidian:1 SOL'])
    ok('each tier states its coins and skin',all(w in pg.inner_text('#tiers') for w in ('500 bonus coins','3,000 bonus coins','15,000 bonus coins','Gold Hunter','Emerald Hunter','Obsidian Hunter')))
    ok('no link to a solana: address exists anywhere on the page (that kind of link is what blanked the page before)',E("document.querySelectorAll('a[href^=\"solana:\"]').length")==0)
    ok('each tier has a "Send X SOL" button (not a link)',E("[].map.call(document.querySelectorAll('#tiers .tier .btn'),function(b){return b.tagName+':'+b.textContent})")==['BUTTON:Send 0.05 SOL','BUTTON:Send 0.25 SOL','BUTTON:Send 1 SOL'])
    nav=[];pg.on('framenavigated',lambda f:nav.append(f.url));url0=pg.url
    pg.click('#tiers .tier[data-tier=gold] .btn');pg.wait_for_timeout(300)
    ok('pressing Send 0.05 SOL opens a send sheet and the page stays alive (no navigation, no blank screen)',E("!document.getElementById('paySheet').hidden") and pg.url==url0 and nav==[] and E("document.body.children.length")>5,nav)
    ok('the sheet says what you are sending and what you get',pg.inner_text('#psTitle')=='Send 0.05 SOL' and 'Gold Hunter' in pg.inner_text('#psWhat') and '500 bonus coins' in pg.inner_text('#psWhat'))
    ok('the sheet shows the exact prize wallet address and the exact amount',pg.inner_text('#psAddr')==POT and pg.inner_text('#psAmt')=='0.05 SOL')
    ok('it gives the four steps, ending with pasting the signature',E("document.querySelectorAll('#paySheet .sheetol li').length")==4 and 'Verify and claim' in pg.inner_text('#paySheet .sheetol'))
    ok('the page is locked behind the sheet (no scrolling) while it is open',E("document.body.classList.contains('lock')"))
    E("window.__copied=[]");pg.click('#psCopyA');pg.click('#psCopyM');pg.wait_for_timeout(200);ok('the copy buttons copy the exact address and the exact amount',E("window.__copied")==[POT,'0.05'],E("window.__copied"))
    pg.click('#psOpen');pg.wait_for_timeout(250)
    fr=E("(function(){var f=document.querySelector('iframe[aria-hidden=true]');return f?f.getAttribute('src'):null})()")
    ok('"Open my wallet app" hands a Solana Pay link to the phone\'s wallet through a hidden frame, so the visible page can never go blank',fr=='solana:%s?amount=0.05&label=CoinHunt&message=Prize%%20wallet%%20contribution'%POT and nav==[] and pg.url==url0,fr)
    ok('...and tells you what to do if nothing opens','nothing happens' in pg.inner_text('#toast'))
    pg.wait_for_timeout(2200);ok('the hidden frame removes itself',E("document.querySelectorAll('iframe[aria-hidden=true]').length")==0)
    pg.click('#psDone');pg.wait_for_timeout(300);ok('"I\'ve sent it" closes the sheet and puts the cursor in the signature box',E("document.getElementById('paySheet').hidden") and E("document.activeElement.id")=='potSig' and not E("document.body.classList.contains('lock')"))
    pg.click('#tiers .tier[data-tier=emerald] .btn');ok('the emerald sheet shows 0.25 SOL',pg.inner_text('#psAmt')=='0.25 SOL' and 'Emerald Hunter' in pg.inner_text('#psWhat'))
    pg.keyboard.press('Escape');ok('Escape closes the sheet and returns focus to the button you pressed',E("document.getElementById('paySheet').hidden") and E("document.activeElement.closest('.tier').dataset.tier")=='emerald')
    pg.click('#tiers .tier[data-tier=obsidian] .btn');pg.click('#psClose');ok('the Close button works, and the 1 SOL sheet said 1 SOL',E("document.getElementById('paySheet').hidden"))
    pg.click('#tiers .tier[data-tier=gold] .btn');pg.mouse.click(5,5);pg.wait_for_timeout(200);ok('clicking outside the sheet closes it',E("document.getElementById('paySheet').hidden"))
    pg.click('#tiers .tier[data-tier=gold] .btn');a=E(AUDIT%"document.getElementById('paySheet')");ok('every line of the send sheet is readable (%d text blocks)'%a['n'],not a['bad'],a['bad'][:3]);pg.click('#psClose')
    # safety net for any other odd link
    E("(function(){var a=document.createElement('a');a.id='odd';a.href='solana:abc';a.textContent='x';document.body.appendChild(a);var b=document.createElement('a');b.id='odd2';b.href='javascript:alert(1)';b.textContent='y';document.body.appendChild(b);var c=document.createElement('a');c.id='okh';c.href='#games';c.textContent='z';document.body.appendChild(c)})()")
    E("window.__def=[];['odd','odd2','okh'].forEach(function(id){document.getElementById(id).addEventListener('click',function(e){window.__def.push(id+':'+e.defaultPrevented)})})")
    E("document.getElementById('odd').click();document.getElementById('odd2').click();document.getElementById('okh').click()");pg.wait_for_timeout(200)
    ok('safety net: any link that is not http(s), #anchor, mail or phone is blocked (solana: and javascript:), but normal #links still work',E("window.__def")==['odd:true','odd2:true','okh:false'] and pg.url.split('#')[0]==url0.split('#')[0],E("window.__def"))
    ok('the prize wallet link opens a public explorer safely',E("(function(a){return a.href==='https://explorer.solana.com/address/%s'&&a.target==='_blank'&&/noopener/.test(a.rel)&&a.textContent==='GLAh\\u2026ysgb'})(document.getElementById('potAddr'))"%POT))
    E("window.__copied=[]");pg.click('#potCopy');pg.wait_for_timeout(150);ok('Copy address puts the exact address on the clipboard',E("window.__copied")==[POT])
    d=pg.inner_text('#pot').lower()
    ok('the disclosure is on the panel: voluntary, non-refundable, no edge in the prize, 18+, no signing',all(w in d for w in ('voluntary and non-refundable','does not improve your chance','18 or older','never asks you to sign','cosmetic')),d[-300:])
    ok('rules and FAQ were updated (optional contributions rule; coins can be earned but not cashed out)','Optional contributions' in E("document.getElementById('rules').textContent") and "can't be cashed out" in E("document.getElementById('rules').textContent") and E("document.querySelectorAll('#rules li').length")==8)
    src=E("document.documentElement.outerHTML")
    ok('there is no private key, keypair, or signing or sending code anywhere in the page',not re.search(r'(secretKey|privateKey|Keypair|signTransaction|signMessage|signAndSend|sendTransaction|sendRawTransaction|seed phrase input)',src.replace('never asks you to sign','')),re.findall(r'.{15}(?:secretKey|Keypair|signTransaction|signMessage|signAndSend|sendTransaction).{10}',src)[:2])
    # ---------- network behaviour
    ok('nothing is requested from the Solana network until the panel is seen',RPC_AT_LOAD==0,RPC_AT_LOAD)
    E("document.getElementById('pot').scrollIntoView({behavior:'instant',block:'center'})");pg.wait_for_timeout(500)
    ok('when it scrolls into view the public balance is read once (a read-only getBalance of the prize wallet)',E("window.__rpc.length")==1 and E("window.__rpc[0].method")=='getBalance' and E("window.__rpc[0].params[0]")==POT and E("window.__rpc[0].url")=='https://api.mainnet-beta.solana.com',E("window.__rpc"))
    ok('...and shown to 4 decimals',pg.inner_text('#potBal')=='0.1235 SOL',pg.inner_text('#potBal'))
    E("window.__bal=2500000000");pg.click('#potBalBtn');pg.wait_for_timeout(300);ok('the Check button refreshes it',pg.inner_text('#potBal')=='2.5000 SOL')
    E("window.__mode='net'");pg.click('#potBalBtn');pg.wait_for_timeout(300);ok('if the network is blocked it says unavailable (never a made-up number) and explains why claiming cannot work on this host',pg.inner_text('#potBal')=='unavailable here' and E("!document.getElementById('potNote').hidden") and 'blocks connections' in pg.inner_text('#potNote'));E("window.__mode='ok'");pg.click('#potBalBtn');pg.wait_for_timeout(300);ok('...and the notice disappears when the network works',E("document.getElementById('potNote').hidden"))
    # ---------- claims
    E("__co.W.tokens=100");n0=E("window.__rpc.length")
    pg.fill('#potSig',SIG(1));pg.click('#potClaim');pg.wait_for_timeout(200)
    ok('claiming before connecting a wallet asks you to connect, and checks nothing',('Connect your wallet first' in pg.inner_text('#potMsg')) and E("window.__rpc.length")==n0 and E("__co.W.tokens")==100)
    pg.click('#wbtn');pg.click('#wmenu [data-w=phantom]');pg.wait_for_timeout(300)
    pg.fill('#potSig','not-a-signature');pg.click('#potClaim');pg.wait_for_timeout(150);ok('a malformed signature is refused without asking the network',('does not look like' in pg.inner_text('#potMsg')) and E("window.__rpc.length")==n0)
    def claim(sig,expect_msg=None):
        pg.fill('#potSig',sig);pg.click('#potClaim');pg.wait_for_timeout(450);return pg.inner_text('#potMsg')
    E("window.__txs[%s]=%s"%(json.dumps(SIG(1)),json.dumps(tx(ME,POT,50000000))))
    m=claim(SIG(1));ok('0.05 SOL from my wallet: verified, Gold Hunter unlocked and equipped, +500 coins',('Verified: 0.05 SOL' in m) and E("__co.W.tokens")==600 and E("__co.W.skins")==['gold'] and E("__co.W.skin")=='gold',(m,E("__co.W.tokens")))
    ok('the request to the blockchain was a read-only getTransaction with the right options',E("window.__rpc[window.__rpc.length-1].method")=='getTransaction' and E("window.__rpc[window.__rpc.length-1].params[1].encoding")=='jsonParsed' and E("window.__rpc[window.__rpc.length-1].params[1].commitment")=='confirmed')
    k=E("window.__rpc.length");m=claim(SIG(1));ok('the same payment cannot be claimed twice (and the network is not even asked)',('already been claimed' in m) and E("__co.W.tokens")==600 and E("window.__rpc.length")==k)
    E("window.__txs[%s]=%s"%(json.dumps(SIG(2)),json.dumps(tx(ME,POT,300000000))));m=claim(SIG(2));ok('0.3 SOL gives the highest tier it reaches: Emerald Hunter and +3,000 coins',E("__co.W.tokens")==3600 and E("__co.W.skins")==['gold','emerald'] and E("__co.W.skin")=='emerald',(m,E("__co.W.skins")))
    E("window.__txs[%s]=%s"%(json.dumps(SIG(3)),json.dumps(tx(ME,POT,2000000000))));m=claim(SIG(3));ok('2 SOL gives Obsidian Hunter and +15,000 coins',E("__co.W.tokens")==18600 and E("__co.W.skins")==['gold','emerald','obsidian'],E("__co.W.tokens"))
    E("window.__txs[%s]=%s"%(json.dumps(SIG(4)),json.dumps(tx(ME,POT,50000000))));m=claim(SIG(4));ok('a second 0.05 payment gives the coins again but never a duplicate skin',E("__co.W.tokens")==19100 and E("__co.W.skins")==['gold','emerald','obsidian'],E("__co.W.skins"))
    b=E("__co.W.tokens")
    def bad(n,t,needle,label):
        E("window.__txs[%s]=%s"%(json.dumps(SIG(n)),json.dumps(t)) if t is not None else "0");m=claim(SIG(n));ok(label,(needle in m) and E("__co.W.tokens")==b and len(E("__co.W.skins"))==3,m)
    bad(10,tx(ME,POT,40000000),'below the smallest reward','0.04 SOL is below the smallest tier: nothing is unlocked, and the message still thanks you')
    bad(11,tx(ME,OTHER,500000000),'No transfer from your connected wallet','a payment to a different address is rejected')
    bad(12,tx(OTHER,POT,500000000),'No transfer from your connected wallet','a payment sent from SOMEONE ELSE\'S wallet cannot be claimed by me')
    bad(13,tx(ME,POT,500000000,err={'InstructionError':[0,'x']}),'failed on the blockchain','a failed transaction is rejected')
    bad(14,tx(ME,POT,500000000,age=40*86400),'too old','a transaction older than 30 days is rejected')
    bad(15,None,'not found yet','a signature the chain does not know yet is not accepted')
    bad(16,tx(ME,POT,500000000,prog='spl-token'),'No transfer from your connected wallet','a look-alike that is not a System Program transfer is ignored')
    E("window.__txs[%s]=%s"%(json.dumps(SIG(20)),json.dumps(tx(ME,POT,30000000,extra=30000000))));E("__co.W.skins=['x'].slice(1);__co.W.skin='classic'");b=E("__co.W.tokens");m=claim(SIG(20))
    ok('two transfers in one transaction are added up: 0.03 + 0.03 = 0.06 SOL -> Gold',('Verified: 0.06 SOL' in m) and E("__co.W.tokens")==b+500 and E("__co.W.skins")==['gold'],m)
    E("window.__txs[%s]=%s"%(json.dumps(SIG(21)),json.dumps(tx(ME,POT,250000000,inner=True))));b=E("__co.W.tokens");m=claim(SIG(21));ok('a transfer made inside another instruction (inner) is found too',('Verified: 0.25 SOL' in m) and E("__co.W.tokens")==b+3000,m)
    E("window.__txs[%s]=%s"%(json.dumps(SIG(22)),json.dumps(tx(ME,POT,50000000))))
    for mode,needle in (('net','reach the Solana network'),('busy','busy'),('error','returned an error')):
        E("window.__mode='%s'"%mode);b=E("__co.W.tokens");m=claim(SIG(22));ok('node problem "%s": a clear message and nothing is granted'%mode,(needle in m) and E("__co.W.tokens")==b,m)
    E("window.__mode='ok'");E("window.__delay=400");b=E("__co.W.tokens");pg.fill('#potSig',SIG(22));pg.click('#potClaim');pg.click('#potClaim',force=True);pg.wait_for_timeout(1200)
    ok('a double click on Verify grants once, not twice',E("__co.W.tokens")==b+500 and E("window.__rpc.filter(function(r){return r.method==='getTransaction'&&r.params[0]===%s}).length"%json.dumps(SIG(22)))>=1 and E("__co.W.red.filter(function(s){return s===%s}).length"%json.dumps(SIG(22)))==1);E("window.__delay=0")
    ok('the wallet was only ever asked to connect (never to sign, send or request anything)',E("window.__calls")==['connect'],E("window.__calls"))
    # ---------- skins
    E("__co.W.skins=['gold','emerald','obsidian'];__co.W.skin='classic';__co.pay.render();__co.applySkin()")
    ok('the skin picker lists Classic plus every unlocked skin',E("[].map.call(document.querySelectorAll('#skinsRow button'),function(b){return b.textContent})")==['Classic','Gold Hunter','Emerald Hunter','Obsidian Hunter'])
    pg.click('#skinsRow [data-skin=gold]');ok('equipping Gold changes the page filter used by Coiny and the clicker coin',E("document.documentElement.getAttribute('data-skin')")=='gold' and 'hue-rotate' in E("getComputedStyle(document.querySelector('#coiny svg')).filter") and E("__co.W.skin")=='gold')
    pg.click('#skinsRow [data-skin=classic]');ok('equipping Classic restores the original look',E("getComputedStyle(document.querySelector('#coiny svg')).filter")=='none')
    ok('a skin you do not own cannot be equipped',E("__co.pay.equip('nope')")==False and E("__co.W.skins=['gold'];__co.pay.equip('obsidian')")==False)
    E("__co.W.skins=['gold','emerald','obsidian']")
    # pouch colour really changes in the Candle Catcher
    def pouch_px(skin):
        E("__co.W.skin='%s';__co.openGame('catcher','free');(function(){var G=__co.GM.catcher,s=G.s;G.stop();G.s=s;s.items.length=0;s.px=180;s.mood='n';G.draw(document.querySelector('#stBody canvas').getContext('2d'))})()"%skin)
        px=E("(function(){var c=document.querySelector('#stBody canvas'),k=c.width/360,d=c.getContext('2d').getImageData(Math.round(150*k),Math.round(500*k),1,1).data;return [d[0],d[1],d[2]]})()");E("__co.closeStage(true)");return px
    c0=pouch_px('classic');c1=pouch_px('gold');c2=pouch_px('obsidian')
    ok('in Candle Catcher the purse is tan, gold or near-black depending on the skin',c1[0]>c0[0]+20 and sum(c2)<sum(c0)-100,(c0,c1,c2))
    # leaderboard star
    E("__co.W.skin='gold';__co.W.name='Hunter';__co.W.wk=__co.board.weekId(Date.now());__co.W.wb={sweeper:100};__co.board.renderBoard()");ok('a contributor gets a star next to their name on the leaderboard',E("__co.board.myDoc().sk")=='gold' and '\u2605' in pg.inner_text('#lbb'),pg.inner_text('#lbb')[:60])
    E("__co.W.skin='classic';__co.board.renderBoard()");ok('and Classic has no star',E("__co.board.myDoc().sk")=='' and '\u2605' not in pg.inner_text('#lbb'))
    E("__co.W.skin='gold';__co.W.skins=['gold'];__co.W.name='Hunter'");E("__co.board.DB.docs=[{uid:'u1',n:'Faker',wk:__co.board.weekId(Date.now()),wb:{sweeper:90},ab:{},sk:'<img src=x>'},{uid:'u2',n:'Real',wk:__co.board.weekId(Date.now()),wb:{sweeper:80},ab:{},sk:'obsidian'}];__co.board.renderBoard()")
    ok('a forged skin value in someone else\'s record is ignored (only known skins get a star)',E("__co.board.boardRows('overall','week').filter(function(r){return r.n==='Faker'})[0].sk")=='' and E("__co.board.boardRows('overall','week').filter(function(r){return r.n==='Real'})[0].sk")=='obsidian' and E("document.querySelectorAll('#lbb img').length")==0)
    # saved data survives, and corruption is cleaned
    E("__co.W.skins=['gold','emerald'];__co.W.skin='emerald';__co.W.red=[%s];__co.save()"%json.dumps(SIG(1)));pg.reload();pg.wait_for_timeout(900);E=pg.evaluate
    ok('skins, the equipped skin and claimed payments survive a reload',E("__co.W.skins")==['gold','emerald'] and E("__co.W.skin")=='emerald' and E("__co.W.red")==[SIG(1)] and E("document.documentElement.getAttribute('data-skin')")=='emerald')
    ctx.close()
    ctx,pg=page("localStorage.setItem('coinop',JSON.stringify({tokens:50,skins:['hack','gold','gold',5],skin:'hack',red:['x',123,'%s']}))"%SIG(7));E=pg.evaluate
    ok('corrupted saved skins are cleaned up (unknown ids and duplicates removed, unowned skin falls back to Classic)',E("__co.W.skins")==['gold'] and E("__co.W.skin")=='classic' and E("__co.W.red")==[SIG(7)],E("[__co.W.skins,__co.W.skin,__co.W.red]"));ctx.close()
    ctx,pg=page("localStorage.setItem('coinop',JSON.stringify({tokens:50,skins:['gold'],skin:'gold'}))");E=pg.evaluate;ok('a saved equipped skin that you own is kept',E("__co.W.skin")=='gold');ctx.close()
    # ---------- devnet switch for testing
    ctx,pg=page(url=URL+'?devnet=1');E=pg.evaluate
    ok('local testing: ?devnet=1 switches to Solana devnet, labels it DEVNET TEST, and links the explorer to devnet',E("__co.pay.state().dev")==True and 'devnet' in E("__co.pay.state().rpc") and pg.inner_text('#potNet')=='DEVNET TEST' and E("document.getElementById('potAddr').href").endswith('?cluster=devnet'));ctx.close()
    ctx=br.new_context(viewport={'width':1280,'height':900});ctx.add_init_script(INIT);pg=ctx.new_page();html=open(URL[7:]).read()
    pg.route('https://coinhunt.example/**',lambda r:r.fulfill(status=200,content_type='text/html',body=html));pg.goto('https://coinhunt.example/?devnet=1');pg.wait_for_timeout(900);E=pg.evaluate
    ok('on a real website ?devnet=1 does nothing (so nobody can claim rewards with free test SOL)',E("__co.pay.state().dev")==False and 'mainnet' in E("__co.pay.state().rpc") and pg.inner_text('#potNet')=='LIVE',E("__co.pay.state()"));ctx.close()
    # ---------- the exact situation that blanked the page: the whole site inside a sandboxed frame
    html=open(URL[7:]).read()
    ctx=br.new_context(viewport={'width':1280,'height':900});ctx.add_init_script(INIT);pg=ctx.new_page();pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.route('https://host.example/inner',lambda r:r.fulfill(status=200,content_type='text/html',body=html))
    pg.route('https://host.example/',lambda r:r.fulfill(status=200,content_type='text/html',body='<body style="margin:0"><iframe id="f" src="https://host.example/inner" sandbox="allow-scripts allow-same-origin allow-popups allow-forms" style="width:100%;height:900px;border:0"></iframe></body>'))
    pg.goto('https://host.example/');pg.wait_for_timeout(1500);fr=pg.frame_locator('#f');inner=[f for f in pg.frames if f.url.endswith('/inner')][0]
    fr.locator('#tiers .tier[data-tier=gold] .btn').scroll_into_view_if_needed();fr.locator('#tiers .tier[data-tier=gold] .btn').click();pg.wait_for_timeout(300)
    ok('inside a sandboxed frame: pressing Send 0.05 SOL opens the sheet',inner.evaluate("!document.getElementById('paySheet').hidden"))
    fr.locator('#psOpen').click();pg.wait_for_timeout(500)
    ok('inside a sandboxed frame: pressing "Open my wallet app" leaves the page fully intact (this is the press that used to go blank)',inner.evaluate("document.body.children.length>5&&!document.getElementById('paySheet').hidden&&document.getElementById('psAddr').textContent")==POT and pg.evaluate("document.getElementById('f').contentDocument.body.innerText.length")>500)
    fr.locator('#psDone').click();pg.wait_for_timeout(300);ok('inside a sandboxed frame: the flow continues to the claim box',inner.evaluate("document.activeElement.id")=='potSig');ctx.close()
    # ---------- reading + phone
    ctx,pg=page();E=pg.evaluate;a=E(AUDIT%"document.getElementById('pot')");ok('every line of the contribution panel is readable (%d text blocks)'%a['n'],not a['bad'],a['bad'][:3]);ctx.close()
    ctx,pg=page(vp=(390,844),mobile=True);E=pg.evaluate
    ok('phone: tiers stack, nothing sideways, buttons fit',not E("document.documentElement.scrollWidth>innerWidth") and E("(function(){var r=document.getElementById('pot').getBoundingClientRect();return r.left>=0&&r.right<=innerWidth})()") and E("getComputedStyle(document.getElementById('tiers')).gridTemplateColumns.split(' ').length")==1)
    a=E(AUDIT%"document.getElementById('pot')");ok('phone: the panel is readable',not a['bad'],a['bad'][:3])
    ok('no page errors',not errs,errs[:3]);ctx.close();br.close()
print('\nSUMMARY: %d/%d passed'%(sum(1 for _,c in res if c),len(res)))

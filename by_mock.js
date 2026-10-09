(function(){
 window.__pres=[];window.__lpres=[];window.__peerHandler=null;window.__lobbyHandler=null;window.__dbwrites=[];window.__joined=[];window.__left=[];
 var store={};window.__dbstore=store;var subs=[];
 function clone(o){return JSON.parse(JSON.stringify(o))}
 function idOf(p){var s=p.split('/');return s[s.length-1]}
 function snapDoc(path){return {id:idOf(path),exists:!!store[path],data:function(){return store[path]?clone(store[path]):undefined}}}
 function qs(col){var pre=col+'/',docs=Object.keys(store).filter(function(k){return k.indexOf(pre)===0&&k.slice(pre.length).indexOf('/')<0}).map(snapDoc);return {docs:docs,size:docs.length,empty:!docs.length,docChanges:function(){return[]}}}
 function fire(){subs.forEach(function(s){try{s.next(qs(s.col))}catch(e){}})}
 window.__dbfire=fire;
 if(window.__preseed)Object.keys(window.__preseed).forEach(function(k){store[k.indexOf('/')>-1?k:('lb/'+k)]=clone(window.__preseed[k])});
 var db={doc:function(path){return {id:idOf(path),path:path,get:async function(){return snapDoc(path)},set:async function(d){if(window.__dbfail){var e=new Error('no');e.code=window.__dbfail;throw e}window.__dbwrites.push([path,clone(d)]);store[path]=clone(d);fire()}}},
  collection:function(path){var q={limit:function(){return q},orderBy:function(){return q},onSnapshot:function(next,err){var s={col:path,next:next};subs.push(s);setTimeout(function(){next(qs(path))},0);return function(){}},get:async function(){return qs(path)}};return q}};
 var rooms={};
 function ns(name){if(rooms[name])return rooms[name];var isLobby=name==='blockstrike-lobby',r={name:name,handler:null,presence:function(p){(isLobby?window.__lpres:window.__pres).push(p);return Promise.resolve()},peers:function(){return[]},
   onPeers:function(h){r.handler=h;if(isLobby)window.__lobbyHandler=h;else window.__peerHandler=h;setTimeout(function(){try{var init=(isLobby?window.__initLobby:window.__initPeers)||{},pl=[{peer:isLobby?'l1':'m1',isMe:true,sameTab:true,presence:{}}];Object.keys(init).forEach(function(k){pl.push({peer:k,isMe:false,presence:init[k]})});h({peers:pl,joined:[],left:[],updated:[]})}catch(e){}},0);return function(){}},
   connected:function(){return true},leave:async function(){window.__left.push(name);delete rooms[name];if(!isLobby&&window.__peerHandler===r.handler)window.__peerHandler=null}};
  rooms[name]=r;window.__joined.push(name);return r}
 var room={join:async function(name){return ns(name)},presence:function(){return Promise.resolve()},peers:function(){return[]},onPeers:function(){return function(){}},connected:function(){return true},leave:async function(){}};
 window.claude={use:async function(n){if(n==='room')return window.__noRoom?null:room;if(n==='db')return window.__noDb?null:db;if(n==='user')return window.__noDb?null:{id:async function(){return window.__uid||'u_me'},can:async function(){return true},isOwner:async function(){return window.__isOwner===true}};return null}};
})();

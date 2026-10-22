// Cache only the public React shell/assets. Never store account, wardrobe or photo responses.
const CACHE='fashion-shell-v2-1';
self.addEventListener('install',event=>{
 event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(['/','/manifest.webmanifest'])));
 self.skipWaiting();
});
self.addEventListener('activate',event=>{
 event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('fashion-shell-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch',event=>{
 const url=new URL(event.request.url);
 if(event.request.method!=='GET'||url.origin!==self.location.origin||url.pathname.startsWith('/api/')||url.pathname.startsWith('/uploads/'))return;
 if(event.request.mode==='navigate'){
  event.respondWith(fetch(event.request).catch(()=>caches.match('/').then(r=>r||Response.error())));
 }else if(url.pathname.startsWith('/assets/')||url.pathname.startsWith('/app-icons/')){
  event.respondWith(caches.match(event.request).then(cached=>cached||fetch(event.request).then(async response=>{
   if(response.ok){try{const cache=await caches.open(CACHE);await cache.put(event.request,response.clone());}catch(error){/* Storage failure must not block online use. */}}
   return response;
  })));
 }
});

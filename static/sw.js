self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open("gpchat-cache").then((cache) => {
      return cache.addAll([
        "/",
        "/static/style.css",
        "/static/script.js",
        "/static/bg-chat.png",
        "/static/header.bg.png",
        "/static/icon-192.png",
        "/static/icon-512.png"
      ]);
    })
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});

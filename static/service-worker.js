// A minimal service worker — required for a website to qualify as an
// installable PWA (and therefore convertible into an APK).
// This doesn't do offline caching yet, just satisfies the installability check.

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Pass-through: just let all requests go to the network as normal.
  event.respondWith(fetch(event.request));
});

// A minimal service worker — required for a website to qualify as an
// installable PWA (and therefore convertible into an APK).
// It intentionally does NOT intercept API calls, to avoid breaking chat requests.

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

// No fetch handler at all — let every request go straight to the network,
// untouched. This still satisfies PWA installability requirements.

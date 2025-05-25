const CACHE_NAME = 'koala-search-v1';
const urlsToCache = [
    '/',
    '/css/main.css',
    '/css/components.css',
    '/css/responsive.css',
    '/js/app.js',
    '/js/config.js',
    '/js/utils.js',
    '/js/api.js'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
    );
}); 
// service_worker.js – cache básico para o PMRV 4 em 1.
// Este service worker implementa um cache estático simples para permitir
// funcionamento offline das páginas essenciais.  Para ambientes de produção
// considere implementar estratégias de cache mais avançadas.

const CACHE_NAME = 'pmrv-4em1-v1';
const URLS_TO_CACHE = [
  './index.html',
  './manifest.json',
  './css/style.css',
  './icon-192.png',
  './icon-512.png'
];

// Instala o service worker e pré‑cacheia recursos básicos.
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(URLS_TO_CACHE))
  );
});

// Ativa o novo service worker e limpa caches antigos.
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames.map(name => {
          if (name !== CACHE_NAME) {
            return caches.delete(name);
          }
        })
      )
    )
  );
});

// Intercepta requisições e responde com cache sempre que possível.
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
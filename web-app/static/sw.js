// Service Worker for Reptile Tracker PWA
// Provides offline support, caching, and push notifications

const CACHE_NAME = 'reptile-tracker-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/manifest.json',
  '/static/icon-192.png',
  '/static/icon-512.png'
];

// Install event - cache resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }

        return fetch(event.request).then(
          response => {
            // Check if valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clone the response
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return response;
          }
        );
      })
  );
});

// Push notification event
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const title = data.title || 'Reptile Tracker';
  const options = {
    body: data.body || 'You have a notification',
    icon: '/static/icon-192.png',
    badge: '/static/icon-192.png',
    vibrate: [200, 100, 200],
    data: data.url || '/',
    actions: [
      {
        action: 'open',
        title: 'Open App'
      },
      {
        action: 'close',
        title: 'Close'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

// Notification click event
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'open' || !event.action) {
    event.waitUntil(
      clients.openWindow(event.notification.data || '/')
    );
  }
});

// Background sync for offline feeding logs
self.addEventListener('sync', event => {
  if (event.tag === 'sync-feeding-logs') {
    event.waitUntil(syncFeedingLogs());
  }
});

async function syncFeedingLogs() {
  // Get pending feeding logs from IndexedDB
  const db = await openDB();
  const tx = db.transaction('pending-logs', 'readonly');
  const store = tx.objectStore('pending-logs');
  const logs = await store.getAll();

  // Sync each log
  for (const log of logs) {
    try {
      const response = await fetch('/api/feeding/' + log.reptile_id, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(log.data)
      });

      if (response.ok) {
        // Remove from pending
        const deleteTx = db.transaction('pending-logs', 'readwrite');
        const deleteStore = deleteTx.objectStore('pending-logs');
        await deleteStore.delete(log.id);
      }
    } catch (error) {
      console.error('Failed to sync log:', error);
    }
  }
}

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('reptile-tracker-db', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = event => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('pending-logs')) {
        db.createObjectStore('pending-logs', { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

// Made with Bob

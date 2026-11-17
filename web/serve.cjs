const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 4173;
const HOST = '127.0.0.1';
const DIST_DIR = path.join(__dirname, 'dist');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.mjs': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.webp': 'image/webp'
};

const server = http.createServer((req, res) => {
  // Normalize URL
  const parsedUrl = new URL(req.url, `http://${req.headers.host || HOST}`);
  let pathname = decodeURIComponent(parsedUrl.pathname);

  // If path is API request without backend, respond with mock 404/503 gracefully
  if (pathname.startsWith('/api/') || pathname.startsWith('/users/')) {
    res.writeHead(503, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
    res.end(JSON.stringify({ error: 'Backend API offline, running in client mock mode' }));
    return;
  }

  // Handle default to index.html
  if (pathname === '/') {
    pathname = '/index.html';
  }

  let filePath = path.join(DIST_DIR, pathname);

  // Check if file exists
  fs.stat(filePath, (err, stats) => {
    if (!err && stats.isFile()) {
      const ext = path.extname(filePath).toLowerCase();
      const contentType = MIME_TYPES[ext] || 'application/octet-stream';
      res.writeHead(200, {
        'Content-Type': contentType,
        'Cache-Control': 'no-cache',
        'Access-Control-Allow-Origin': '*'
      });
      const stream = fs.createReadStream(filePath);
      stream.on('error', () => {
        if (!res.headersSent) res.writeHead(500);
        res.end();
      });
      stream.pipe(res);
    } else {
      // SPA fallback to index.html for client routes (unless requesting a non-existent asset)
      const isAsset = pathname.startsWith('/assets/') || pathname.startsWith('/screens/') || path.extname(pathname) !== '';
      if (!isAsset) {
        const indexPath = path.join(DIST_DIR, 'index.html');
        fs.readFile(indexPath, (readErr, data) => {
          if (readErr) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('Not Found');
          } else {
            res.writeHead(200, {
              'Content-Type': 'text/html; charset=utf-8',
              'Cache-Control': 'no-cache',
              'Access-Control-Allow-Origin': '*'
            });
            res.end(data);
          }
        });
      } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('File Not Found');
      }
    }
  });
});

server.listen(PORT, HOST, () => {
  console.log(`Rebound server running at http://${HOST}:${PORT}/`);
});

server.on('error', (err) => {
  console.error('Server error:', err);
});

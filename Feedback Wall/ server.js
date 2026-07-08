const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const DATA_FILE = path.join(__dirname, 'messages.json');
const PUBLIC_DIR = path.join(__dirname, 'public');

// Helper to read messages
const getMessages = () => {
    if (!fs.existsSync(DATA_FILE)) fs.writeFileSync(DATA_FILE, JSON.stringify([]));
    return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
};

const server = http.createServer((req, res) => {
    // API Endpoint: Get all messages
    if (req.url === '/api/messages' && req.method === 'GET') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        return res.end(JSON.stringify(getMessages()));
    }

    // API Endpoint: Post a new message
    if (req.url === '/api/messages' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => { body += chunk.toString(); });
        req.on('end', () => {
            const { name, text } = JSON.parse(body);
            if (!name || !text) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                return res.end(JSON.stringify({ error: 'Missing fields' }));
            }
            
            const messages = getMessages();
            messages.push({ name, text, timestamp: new Date().toLocaleTimeString() });
            fs.writeFileSync(DATA_FILE, JSON.stringify(messages, null, 2));

            res.writeHead(201, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: true }));
        });
        return;
    }

    // Serve Static Frontend Files
    let filePath = path.join(PUBLIC_DIR, req.url === '/' ? 'index.html' : req.url);
    let extname = path.extname(filePath);
    let contentType = 'text/html';

    if (extname === '.css') contentType = 'text/css';
    if (extname === '.js') contentType = 'text/javascript';

    fs.readFile(filePath, (err, content) => {
        if (err) {
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.end('404 Not Found');
        } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content);
        }
    });
});

server.listen(PORT, () => console.log(`Server running at http://localhost:${PORT}`));

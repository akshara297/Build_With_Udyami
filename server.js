const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 3000;

// ==========================================
// CONFIGURATION (Change your admin password here)
// ==========================================
const ADMIN_PASSWORD = "mysecretbdaypass"; 

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const DB_FILE = path.join(__dirname, 'database.json');

if (!fs.existsSync(DB_FILE)) {
    const defaultData = {
        unlockDate: new Date(Date.now() + 60000 * 2).toISOString(), 
        capsules: [
            { id: 1, sender: "Alex", message: "Happy Birthday! Hope this year brings you absolute joy!" },
            { id: 2, sender: "Sam", message: "Cheers to more chaotic adventures together!" }
        ]
    };
    fs.writeFileSync(DB_FILE, JSON.stringify(defaultData, null, 2));
}

const readDB = () => JSON.parse(fs.readFileSync(DB_FILE, 'utf8'));
const writeDB = (data) => fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2));

// ==========================================
// API ENDPOINTS
// ==========================================

// 1. Public config check (Only gives out the date, NOT the messages)
app.get('/api/config', (req, res) => {
    const db = readDB();
    res.json({ unlockDate: db.unlockDate });
});

// 2. Submit a message (Publicly accessible)
app.post('/api/capsules', (req, res) => {
    const { sender, message } = req.body;
    if (!sender || !message) {
        return res.status(400).json({ error: "Please provide both your name and a message." });
    }

    const db = readDB();
    db.capsules.push({
        id: Date.now(),
        sender: sender.trim(),
        message: message.trim()
    });
    writeDB(db);

    res.status(201).json({ success: true });
});

// 3. SECURE ADMIN ENDPOINT (Only allows access with the correct password AND after unlock date)
app.post('/api/admin/reveal', (req, res) => {
    const { password } = req.body;
    const db = readDB();
    const now = new Date();
    const unlockTime = new Date(db.unlockDate);

    // Guard 1: Time Check
    if (now < unlockTime) {
        return res.status(403).json({ error: "The capsule's lock mechanism has not released yet." });
    }

    // Guard 2: Password Check
    if (password !== ADMIN_PASSWORD) {
        return res.status(401).json({ error: "Invalid Admin Authorization Key." });
    }

    // If both pass, return the secret messages
    res.json({ success: true, capsules: db.capsules });
});

// ==========================================
// FRONTEND 1: Main Contributor Page
// ==========================================
app.get('/', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chronos: Drop a Message</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <style>@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap'); body { font-family: 'Space Grotesk', sans-serif; }</style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between">
    <header class="py-6 border-b border-slate-800 backdrop-blur-md bg-slate-950/80">
        <div class="max-w-xl mx-auto px-4 flex justify-between items-center">
            <h1 class="text-2xl font-bold bg-gradient-to-r from-pink-500 to-indigo-500 bg-clip-text text-transparent">CHRONOS</h1>
            <a href="/admin" class="text-xs text-slate-500 hover:text-pink-400 transition-colors">Admin Login</a>
        </div>
    </header>

    <main class="max-w-xl mx-auto px-4 py-12 w-full flex-grow">
        <div class="bg-slate-900/50 border border-slate-800 p-8 rounded-2xl shadow-xl">
            <h3 class="text-xl font-semibold mb-2 text-pink-400">Leave a Birthday Message</h3>
            <p class="text-xs text-slate-400 mb-6">Your message will be safely encrypted and hidden until the countdown finishes. Only the birthday VIP can read it.</p>
            
            <form id="contribution-form" class="space-y-4">
                <div>
                    <label class="block text-xs uppercase tracking-wider text-slate-400 mb-1">Your Name</label>
                    <input type="text" id="sender" required class="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-pink-500">
                </div>
                <div>
                    <label class="block text-xs uppercase tracking-wider text-slate-400 mb-1">Secret Message</label>
                    <textarea id="message" rows="4" required class="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-pink-500 resize-none"></textarea>
                </div>
                <button type="submit" class="w-full bg-gradient-to-r from-pink-500 to-purple-600 font-medium text-sm py-3 rounded-lg hover:from-pink-600 transition-all cursor-pointer">
                    Lock Message Into Vault
                </button>
            </form>
        </div>
    </main>
    <script>
        document.getElementById('contribution-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const res = await fetch('/api/capsules', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sender: document.getElementById('sender').value, message: document.getElementById('message').value })
            });
            if (res.ok) {
                alert('✨ Vaulted! Your message is safely tucked away.');
                document.getElementById('contribution-form').reset();
            }
        });
    </script>
</body>
</html>
    `);
});

// ==========================================
// FRONTEND 2: Private Admin Panel
// ==========================================
app.get('/admin', (req, res) => {
    res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chronos Admin View</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <style>@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap'); body { font-family: 'Space Grotesk', sans-serif; }</style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between">
    <main class="max-w-xl mx-auto px-4 py-12 w-full flex-grow">
        <div id="admin-deck" class="bg-slate-900/50 border border-slate-800 p-8 rounded-2xl shadow-xl space-y-6">
            <div class="text-center">
                <span class="text-4xl">👑</span>
                <h2 class="text-2xl font-bold mt-2">VIP Dashboard</h2>
                <p class="text-xs text-slate-400 mt-1">Unlock time status and message review module.</p>
            </div>

            <div id="countdown" class="text-center text-xl font-bold tracking-widest text-pink-500 bg-slate-950 p-4 rounded-xl border border-slate-800">
                Calculating remaining temporal lock...
            </div>

            <div id="access-form-container" class="hidden space-y-4">
                <div>
                    <label class="block text-xs uppercase tracking-wider text-slate-400 mb-1">Enter Secret Admin Password</label>
                    <input type="password" id="password" class="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-pink-500">
                </div>
                <button id="btn-decrypt" class="w-full bg-emerald-600 font-medium text-sm py-3 rounded-lg hover:bg-emerald-700 transition-all cursor-pointer">
                    Decrypt Messages
                </button>
            </div>
        </div>
    </main>

    <script>
        let unlockTargetDate;
        
        async function initAdmin() {
            const res = await fetch('/api/config');
            const config = await res.json();
            unlockTargetDate = new Date(config.unlockDate);

            const timer = setInterval(() => {
                const distance = unlockTargetDate.getTime() - new Date().getTime();
                if (distance < 0) {
                    clearInterval(timer);
                    document.getElementById('countdown').innerHTML = "🔓 SYSTEM UNLOCKED";
                    document.getElementById('countdown').className = "text-center text-sm font-bold text-emerald-400 bg-emerald-950/20 p-3 rounded-xl border border-emerald-500/20";
                    document.getElementById('access-form-container').classList.remove('hidden');
                } else {
                    const h = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    const m = Math.floor((distance % (1000 * 60)) / (1000 * 60));
                    const s = Math.floor((distance % (1000 * 60)) / 1000);
                    document.getElementById('countdown').textContent = \`LOCKED: \${h}h \${m}m \${s}s\`;
                }
            }, 1000);
        }

        document.getElementById('btn-decrypt').addEventListener('click', async () => {
            const password = document.getElementById('password').value;
            const res = await fetch('/api/admin/reveal', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password })
            });

            const data = await res.json();
            if(!res.ok) {
                alert(data.error);
                return;
            }

            // Render private messages exclusively for you
            const deck = document.getElementById('admin-deck');
            deck.innerHTML = \`<h3 class="text-xl font-bold tracking-tight text-purple-400">📬 Inbox Messages (\${data.capsules.length})</h3>\`;
            
            data.capsules.forEach(item => {
                const card = document.createElement('div');
                card.className = "bg-slate-950 border border-slate-800 p-6 rounded-xl space-y-2";
                card.innerHTML = \`
                    <p class="text-slate-200 text-sm italic">"\${item.message}"</p>
                    <div class="text-right text-xs uppercase font-semibold tracking-wider text-pink-500">— From \${item.sender}</div>
                \`;
                deck.appendChild(card);
            });
        });

        initAdmin();
    </script>
</body>
</html>
    `);
});

app.listen(PORT, () => console.log(`🚀 Private Vault running at http://localhost:${PORT}`));
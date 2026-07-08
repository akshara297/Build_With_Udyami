const express = require('express');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const { getUsers, saveUsers } = require('./database');

const app = express();
const PORT = process.env.PORT || 5000;
const JWT_SECRET = 'super-secret-key-change-this-in-production';

// Middleware
app.use(cors());
app.use(express.json());

// Health Check
app.get('/api/health', (req, res) => {
    res.json({ status: "success", message: "Diary Server is up and running!" });
});

// 1. REGISTER ROUTE
app.post('/api/register', async (req, res) => {
    try {
        const { username, password } = req.body;

        if (!username || !password) {
            return res.status(400).json({ error: "Username and password are required" });
        }

        const users = await getUsers();
        
        // Check if user already exists
        const userExists = users.find(u => u.username.toLowerCase() === username.toLowerCase());
        if (userExists) {
            return res.status(400).json({ error: "Username already taken" });
        }

        // Hash the password securely
        const hashedPassword = await bcrypt.hash(password, 10);

        // Create new user object
        const newUser = {
            id: uuidv4(),
            username,
            password: hashedPassword
        };

        users.push(newUser);
        await saveUsers(users);

        res.status(201).json({ message: "User registered successfully!" });
    } catch (error) {
        res.status(500).json({ error: "Server error during registration" });
    }
});

// 2. LOGIN ROUTE
app.post('/api/login', async (req, res) => {
    try {
        const { username, password } = req.body;

        const users = await getUsers();
        
        // Find user
        const user = users.find(u => u.username.toLowerCase() === username.toLowerCase());
        if (!user) {
            return res.status(400).json({ error: "Invalid credentials" });
        }

        // Check password match
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.status(400).json({ error: "Invalid credentials" });
        }

        // Generate JWT Token (expires in 1 hour)
        const token = jwt.sign({ userId: user.id, username: user.username }, JWT_SECRET, { expiresIn: '1h' });

        res.json({ 
            message: "Login successful!", 
            token, 
            user: { id: user.id, username: user.username } 
        });
    } catch (error) {
        res.status(500).json({ error: "Server error during login" });
    }
});
const { getEntries, saveEntries } = require('./database');

// --- AUTH MIDDLEWARE ---
// This intercepts requests to make sure the user is logged in
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Expects "Bearer TOKEN"

    if (!token) {
        return res.status(401).json({ error: "Access denied. No token provided." });
    }

    jwt.verify(token, JWT_SECRET, (err, decodedUser) => {
        if (err) {
            return res.status(403).json({ error: "Invalid or expired token." });
        }
        req.user = decodedUser; // Adds { userId, username } to the request object
        next();
    });
}

// --- DIARY CRUD ROUTES ---

// 1. CREATE: Add a new entry
app.post('/api/entries', authenticateToken, async (req, res) => {
    try {
        const { title, content } = req.body;
        if (!title || !content) {
            return res.status(400).json({ error: "Title and content are required." });
        }

        const entries = await getEntries();
        
        const newEntry = {
            id: uuidv4(),
            userId: req.user.userId, // Tied strictly to the logged-in user
            title,
            content,
            createdAt: new Date().toISOString()
        };

        entries.push(newEntry);
        await saveEntries(entries);

        res.status(201).json({ message: "Diary entry created!", entry: newEntry });
    } catch (error) {
        res.status(500).json({ error: "Failed to save diary entry." });
    }
});

// 2. READ: Get all entries for the logged-in user ONLY
app.get('/api/entries', authenticateToken, async (req, res) => {
    try {
        const entries = await getEntries();
        // Securely filter entries so users can't see other people's diaries
        const userEntries = entries.filter(e => e.userId === req.user.userId);
        res.json(userEntries);
    } catch (error) {
        res.status(500).json({ error: "Failed to retrieve entries." });
    }
});

// 3. UPDATE: Edit an existing entry
app.put('/api/entries/:id', authenticateToken, async (req, res) => {
    try {
        const { title, content } = req.body;
        const entries = await getEntries();
        
        const entryIndex = entries.findIndex(e => e.id === req.params.id && e.userId === req.user.userId);
        
        if (entryIndex === -1) {
            return res.status(404).json({ error: "Entry not found or unauthorized access." });
        }

        // Update fields if provided
        if (title) entries[entryIndex].title = title;
        if (content) entries[entryIndex].content = content;
        
        await saveEntries(entries);
        res.json({ message: "Entry updated successfully!", entry: entries[entryIndex] });
    } catch (error) {
        res.status(500).json({ error: "Failed to update entry." });
    }
});

// 4. DELETE: Remove an entry
app.delete('/api/entries/:id', authenticateToken, async (req, res) => {
    try {
        let entries = await getEntries();
        
        // Check if entry exists and belongs to the user
        const entryExists = entries.some(e => e.id === req.params.id && e.userId === req.user.userId);
        if (!entryExists) {
            return res.status(404).json({ error: "Entry not found or unauthorized access." });
        }

        // Filter out the deleted entry
        entries = entries.filter(e => e.id !== req.params.id);
        await saveEntries(entries);

        res.json({ message: "Entry deleted successfully." });
    } catch (error) {
        res.status(500).json({ error: "Failed to delete entry." });
    }
});

// Start Server
app.listen(PORT, () => {
    console.log(`🚀 Server securely running on http://localhost:${PORT}`);
});
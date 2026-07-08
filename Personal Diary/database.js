const fs = require('fs').promises;
const path = require('path');

const USERS_FILE = path.join(__dirname, 'data', 'users.json');
const ENTRIES_FILE = path.join(__dirname, 'data', 'entries.json');

// --- USER REPOSITORY FUNCTIONS ---

// Read all users
async function getUsers() {
    try {
        const data = await fs.readFile(USERS_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        return []; // Fallback if file doesn't exist yet
    }
}

// Write all users
async function saveUsers(users) {
    await fs.writeFile(USERS_FILE, JSON.stringify(users, null, 2), 'utf8');
}

// --- ENTRY REPOSITORY FUNCTIONS ---

// Read all diary entries
async function getEntries() {
    try {
        const data = await fs.readFile(ENTRIES_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        return [];
    }
}

// Write all diary entries
async function saveEntries(entries) {
    await fs.writeFile(ENTRIES_FILE, JSON.stringify(entries, null, 2), 'utf8');
}

// Export functions to be used in other files
module.exports = {
    getUsers,
    saveUsers,
    getEntries,
    saveEntries
};

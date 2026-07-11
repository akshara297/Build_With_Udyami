const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;
const DB_FILE = path.join(__dirname, 'petData.json');

app.use(express.json());
app.use(express.static('public'));

const getPetData = () => {
    const now = Date.now();
    
    if (!fs.existsSync(DB_FILE)) {
        // Return null instead of a default pet, so the frontend knows to show the adoption screen!
        return null;
    }

    const pet = JSON.parse(fs.readFileSync(DB_FILE));
    
    // Time decay logic
    const elapsedMs = now - pet.lastCheck;
    const intervals = Math.floor(elapsedMs / 10000); 

    if (intervals > 0) {
        pet.hunger = Math.min(100, pet.hunger + (intervals * 2));
        pet.happiness = Math.max(0, pet.happiness - (intervals * 2));
        pet.lastCheck = pet.lastCheck + (intervals * 10000);
        fs.writeFileSync(DB_FILE, JSON.stringify(pet, null, 2));
    }

    return pet;
};

// --- API ROUTES ---

// Get current pet status
app.get('/api/pet', (req, res) => {
    const pet = getPetData();
    res.json(pet); // Will return null if no pet exists
});

// Setup/Adopt a new pet
app.post('/api/adopt', (req, res) => {
    const { name, type } = req.body;
    
    const newPet = {
        name: name || "Unknown",
        type: type || "cat", // 'cat', 'dog', or 'dragon'
        hunger: 30,
        happiness: 70,
        lastCheck: Date.now()
    };

    fs.writeFileSync(DB_FILE, JSON.stringify(newPet, null, 2));
    res.json(newPet);
});

app.post('/api/feed', (req, res) => {
    const pet = getPetData();
    if (!pet) return res.status(404).json({ error: "No pet found" });
    pet.hunger = Math.max(0, pet.hunger - 15);
    pet.lastCheck = Date.now();
    fs.writeFileSync(DB_FILE, JSON.stringify(pet, null, 2));
    res.json({ message: "Om nom nom! 🍖", pet });
});

app.post('/api/play', (req, res) => {
    const pet = getPetData();
    if (!pet) return res.status(404).json({ error: "No pet found" });
    pet.happiness = Math.min(100, pet.happiness + 15);
    pet.lastCheck = Date.now();
    fs.writeFileSync(DB_FILE, JSON.stringify(pet, null, 2));
    res.json({ message: "Yay, let's play! 🎾", pet });
});

app.listen(PORT, () => {
    console.log(`Cute server running at http://localhost:${PORT} ✨`);
});
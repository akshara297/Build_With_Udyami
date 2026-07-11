const setupCard = document.getElementById('setup-card');
const gameCard = document.getElementById('game-card');
const petName = document.getElementById('pet-name');
const petStatusText = document.getElementById('pet-status-text');
const petAvatar = document.getElementById('pet-avatar');
const hungerVal = document.getElementById('hunger-val');
const hungerBar = document.getElementById('hunger-bar');
const happinessVal = document.getElementById('happiness-val');
const happinessBar = document.getElementById('happiness-bar');
const bubble = document.getElementById('bubble');

const btnFeed = document.getElementById('btn-feed');
const btnPlay = document.getElementById('btn-play');
const btnAdopt = document.getElementById('btn-adopt');
const nameInput = document.getElementById('name-input');

let selectedSpecies = 'cat'; 

// 🔊 RETRO 8-BIT AUDIO SYNTHESIZER ENGINE
function playSound(type) {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    
    osc.connect(gain);
    gain.connect(ctx.destination);

    const now = ctx.currentTime;

    if (type === 'feed') {
        // Quick two-tone crunchy chomp sound
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(150, now);
        osc.frequency.exponentialRampToValueAtTime(300, now + 0.1);
        gain.gain.setValueAtTime(0.3, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
        osc.start(now);
        osc.stop(now + 0.2);
    } else if (type === 'play') {
        // Upward sliding happy victory chime
        osc.type = 'square';
        osc.frequency.setValueAtTime(400, now);
        osc.frequency.exponentialRampToValueAtTime(800, now + 0.15);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
        osc.start(now);
        osc.stop(now + 0.2);
    } else if (type === 'adopt') {
        // Sparkling magical level-up arpeggio
        osc.type = 'sine';
        osc.frequency.setValueAtTime(300, now);
        osc.frequency.setValueAtTime(450, now + 0.08);
        osc.frequency.setValueAtTime(600, now + 0.16);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
        osc.start(now);
        osc.stop(now + 0.3);
    }
}

// Visual Juice: Triggers the CSS pop bounce animation
function triggerJuiceAnimation() {
    petAvatar.classList.remove('animate-bounce'); // Pause baseline float
    petAvatar.classList.add('pet-bounce');
    
    // Reset back to normal floating after animation stops
    setTimeout(() => {
        petAvatar.classList.remove('pet-bounce');
        petAvatar.classList.add('animate-bounce');
    }, 400);
}

function selectSpecies(species) {
    selectedSpecies = species;
    ['cat', 'dog', 'dragon'].forEach(s => {
        const btn = document.getElementById(`choice-${s}`);
        if (s === species) {
            btn.classList.add('border-indigo-500', 'bg-indigo-50');
            btn.classList.remove('border-transparent', 'bg-gray-50');
        } else {
            btn.classList.remove('border-indigo-500', 'bg-indigo-50');
            btn.classList.add('border-transparent', 'bg-gray-50');
        }
    });
}

function getAvatarEmoji(type, hunger, happiness) {
    const sets = {
        cat: { normal: "🐱", happy: "🥰", sad: "😿", hungry: "🦁" },
        dog: { normal: "🐶", happy: "🤪", sad: "🥺", hungry: "🐺" },
        dragon: { normal: "🐉", happy: "🐲", sad: "🦕", hungry: "🐊" }
    };
    
    const petSet = sets[type] || sets.cat;

    if (hunger > 75) return petSet.hungry;
    if (happiness < 30) return petSet.sad;
    if (happiness > 80 && hunger < 30) return petSet.happy;
    return petSet.normal;
}

function updateUI(pet) {
    if (!pet) {
        setupCard.classList.remove('hidden');
        gameCard.classList.add('hidden');
        return;
    }

    setupCard.classList.add('hidden');
    gameCard.classList.remove('hidden');

    petName.textContent = pet.name;
    hungerVal.textContent = `${pet.hunger}%`;
    happinessVal.textContent = `${pet.happiness}%`;
    hungerBar.style.width = `${pet.hunger}%`;
    happinessBar.style.width = `${pet.happiness}%`;

    petAvatar.textContent = getAvatarEmoji(pet.type, pet.hunger, pet.happiness);
    
    if (pet.hunger > 75) petStatusText.textContent = "Starving for food!";
    else if (pet.happiness < 30) petStatusText.textContent = "Bored and lonely...";
    else petStatusText.textContent = "Happy and healthy!";
}

function showBubble(text) {
    bubble.textContent = text;
    bubble.style.opacity = "1";
    setTimeout(() => bubble.style.opacity = "0", 1500);
}

async function initPet() {
    try {
        const response = await fetch('/api/pet');
        const pet = await response.json();
        updateUI(pet);
    } catch (err) {
        console.error("Error connecting:", err);
    }
}

btnAdopt.addEventListener('click', async () => {
    const name = nameInput.value.trim();
    if (!name) return alert("Please name your companion!");

    try {
        const response = await fetch('/api/adopt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, type: selectedSpecies })
        });
        const pet = await response.json();
        updateUI(pet);
        playSound('adopt');
    } catch (err) {
        console.error("Error adopting pet:", err);
    }
});

btnFeed.addEventListener('click', async () => {
    const response = await fetch('/api/feed', { method: 'POST' });
    const data = await response.json();
    updateUI(data.pet);
    showBubble(data.message);
    playSound('feed');
    triggerJuiceAnimation();
});

btnPlay.addEventListener('click', async () => {
    const response = await fetch('/api/play', { method: 'POST' });
    const data = await response.json();
    updateUI(data.pet);
    showBubble(data.message);
    playSound('play');
    triggerJuiceAnimation();
});

initPet();
setInterval(initPet, 3000);
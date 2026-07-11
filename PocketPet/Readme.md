# ✨ VIRTUAL POCKET PET DASHBOARD ✨

A beautifully responsive, interactive full-stack virtual pet application built with a cozy retro chiptune aesthetic. Adopt a companion (`Cat`, `Dog`, or `Dragon`), keep them well-fed and entertained, watch them grow as they gain Experience Points (XP) to level up, and enjoy tactile feedback through sound and visual animations!

This project features procedural 8-bit sound generation (no external media files required), active CSS bounce mechanics, automated status decay logic, and a lightweight local flat-file storage layer.

---

## 🎮 Game Features & Systems

* **Dynamic Expression Engine:** Your pet's avatar emoji dynamically reacts to its stats—shifting faces depending on whether they are happy, healthy, starving, or lonely.
* **The Level-Up System:** Every positive interaction (`Feed` or `Play`) awards your companion XP. Hitting **100 XP** triggers a level-up animation and a custom 4-tone victory chime!
* **Real-Time Time Decay:** A custom server-side delta calculator runs in the background. Even if the browser is closed, your pet's hunger will steadily increase and its happiness will gradually decay over time.
* **Procedural Audio Engine:** Utilizes the native browser **Web Audio API** to synthesize chiptune effects (chomp sounds, play sounds, and level-up fanfares) entirely out of raw math code.
* **Visual Juice Animations:** Triggers a snappy CSS scale-and-rotate transform pop whenever you interact with your pet, making the UI feel tactile and satisfying.

---

## 🛠️ Technology Stack

* **Frontend UI Layer:** Vanilla JavaScript DOM structure styled via **Tailwind CSS CDN** with smooth transition properties.
* **Application Backend Engine:** **Node.js** coupled with an **Express** web server framework.
* **Data Persistence Layer:** A lightweight local flat-file configuration (`petData.json`) that saves state information securely across server restarts.

---

## 🚀 Getting Started

### 1. Project Folder Verification
Ensure your project files are laid out exactly like this inside your workspace directory:
```text
pocket-pet/
├── node_modules/         # Express dependencies
├── petData.json          # Live pet state database storage
├── server.js             # Express application & status decay logic
├── package.json          # Node configuration file
└── public/               # Frontend directory
    ├── index.html        # App layout structure & CSS animations
    └── script.js         # UI updates, synth audio, and fetch calls

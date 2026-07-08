# Mini Feedback Wall 📝

A simple, lightweight full-stack web application built using **pure JavaScript** (no external frameworks like Express or React). It allows users to write messages on a digital guestbook wall that persist across page reloads using a local JSON file database.

## 🚀 Features
*   **Pure Native Stack:** Built using only standard vanilla HTML, CSS, Node.js (HTTP module), and Browser JS.
*   **Data Persistence:** Uses a lightweight JSON file (`messages.json`) as a makeshift database.
*   **XSS Protection:** Essential sanitization on the client side to prevent malicious script injection.
*   **Responsive UI:** Clean, minimalist, card-based interface tailored for mobile and desktop screens.

---

## 📁 Project Directory Structure 

```text
feedback-wall/
│
├── public/          # Frontend Web Assets
│   ├── index.html   # Markup structure
│   ├── style.css    # Styling and layout
│   └── script.js    # DOM manipulation and API handling
│
├── server.js        # Native Node.js HTTP Backend Server
├── messages.json    # Local JSON storage file (Auto-generated)
└── README.md        # Documentation

# Full-Stack Calculator App

A simple, decoupled full-stack calculator application built with a lightweight Node.js/Express back-end API and a modern, responsive HTML5/CSS3/JavaScript front-end. 

Unlike traditional browser-only calculators, this project demonstrates standard client-server architecture by offloading arithmetic operations to a RESTful API.

## 🚀 Features

- **Decoupled Architecture:** Front-end UI entirely separated from the back-end calculation engine.
- **RESTful API:** Clean `POST` endpoint handling inputs and validating mathematical operations.
- **Robust Error Handling:** Server-side validation preventing common issues like missing parameters, invalid operations, and division by zero.
- **Responsive UI:** Clean, centered card-based design that adapts beautifully to both mobile and desktop screens.

---

## 📂 Project Structure

```text
calculator-app/
├── public/                 # Front-end Assets
│   ├── index.html          # Application UI markup
│   ├── style.css           # UI styling and layout
│   └── app.js              # Client-side API fetch logic
├── server.js               # Node.js Express server backend
├── package.json            # Project dependencies and metadata
└── README.md               # Documentation

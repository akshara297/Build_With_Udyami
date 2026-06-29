const express = require('express');
const path = require('path');
const app = express();
const PORT = 3000;

// Middleware to parse incoming JSON data from the frontend
app.use(express.json());

// Serve your static frontend files (html, css, js) automatically
app.use(express.static(path.join(__dirname)));

// A temporary "in-memory database" array to store tasks for now
let tasks = [
    { id: 1, text: "Research backend architecture", status: "to-do" },
    { id: 2, text: "Design database schema", status: "to-do" },
    { id: 3, text: "Building frontend UI", status: "in-progress" },
    { id: 4, text: "Project ideation", status: "done" }
];

// API Endpoint: Get all tasks
app.get('/api/tasks', (req, res) => {
    res.json(tasks);
});
// API Endpoint: Update a task's column status
app.post('/api/tasks/update', (req, res) => {
    const { taskText, newStatus } = req.body;

    // Find the task by its text content and update its status
    const task = tasks.find(t => t.text === taskText);
    if (task) {
        task.status = newStatus;
        console.log(`Updated task "${taskText}" -> ${newStatus}`);
        return res.json({ success: true, tasks });
    }

    res.status(404).json({ success: false, message: "Task not found" });
});

// API Endpoint: Add a brand new task
app.post('/api/tasks', (req, res) => {
    const { text, status } = req.body;

    if (!text) {
        return res.status(400).json({ success: false, message: "Task text is required" });
    }

    const newTask = {
        id: tasks.length + 1, // Simple auto-increment ID
        text: text,
        status: status
    };

    tasks.push(newTask);
    console.log(`Added new task: "${text}" to [${status}]`);
    res.json({ success: true, task: newTask });
});


// Start the server
app.listen(PORT, () => {
    console.log(`🚀 Server is running smoothly at http://localhost:${PORT}`);
});
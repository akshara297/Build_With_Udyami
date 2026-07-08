const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 3000;

// Middleware
app.use(cors()); // Allows our front-end to communicate with the back-end
app.use(express.json()); // Parses incoming JSON requests

// Calculation Endpoint
app.post('/calculate', (req, res) => {
    const { num1, num2, operation } = req.body;

    // Validation
    if (num1 === undefined || num2 === undefined || !operation) {
        return res.status(400).json({ error: "Missing required parameters." });
    }

    const n1 = parseFloat(num1);
    const n2 = parseFloat(num2);
    let result = 0;

    switch (operation) {
        case 'add':
            result = n1 + n2;
            break;
        case 'subtract':
            result = n1 - n2;
            break;
        case 'multiply':
            result = n1 * n2;
            break;
        case 'divide':
            if (n2 === 0) {
                return res.status(400).json({ error: "Cannot divide by zero." });
            }
            result = n1 / n2;
            break;
        default:
            return res.status(400).json({ error: "Invalid operation. Use add, subtract, multiply, or divide." });
    }

    res.json({ result });
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});

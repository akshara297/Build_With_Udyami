document.getElementById('calc-btn').addEventListener('click', async () => {
    const num1 = document.getElementById('num1').value;
    const num2 = document.getElementById('num2').value;
    const operation = document.getElementById('operation').value;
    const resultValue = document.getElementById('result-value');

    // Quick front-end validation
    if (num1 === '' || num2 === '') {
        alert('Please enter both numbers');
        return;
    }

    try {
        // Making the API call to our Node.js server
        const response = await fetch('http://localhost:3000/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ num1, num2, operation })
        });

        const data = await response.json();

        if (response.ok) {
            resultValue.textContent = data.result;
        } else {
            alert(`Error: ${data.error}`);
            resultValue.textContent = 'Error';
        }
    } catch (error) {
        console.error('Fetch error:', error);
        alert('Could not connect to the back-end server.');
    }
});

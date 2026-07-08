const form = document.getElementById('messageForm');
const container = document.getElementById('messagesContainer');

// Fetch and display messages
async function loadMessages() {
    try {
        const response = await fetch('/api/messages');
        const messages = await response.json();
        
        container.innerHTML = messages.length === 0 
            ? '<p>No messages yet. Be the first!</p>' 
            : '';

        messages.reverse().forEach(msg => {
            const card = document.createElement('div');
            card.className = 'message-card';
            card.innerHTML = `
                <p><strong>${escapeHTML(msg.name)}</strong>: ${escapeHTML(msg.text)}</p>
                <div class="meta">${msg.timestamp}</div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        container.innerHTML = '<p>Error loading messages.</p>';
    }
}

// Handle form submission
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('nameInput').value;
    const text = document.getElementById('textInput').value;

    try {
        const response = await fetch('/api/messages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, text })
        });

        if (response.ok) {
            form.reset();
            loadMessages();
        }
    } catch (err) {
        alert('Failed to send message.');
    }
});

// Simple security helper to prevent script injection (XSS)
function escapeHTML(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Initial load
loadMessages();

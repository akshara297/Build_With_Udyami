let draggedCard = null;

// 1. Core Drag and Drop Event Setup Function
function attachDragEvents(card) {
    card.setAttribute('draggable', 'true');

    card.addEventListener('dragstart', () => {
        draggedCard = card;
        setTimeout(() => (card.style.display = 'none'), 0);
    });

    card.addEventListener('dragend', () => {
        card.style.display = 'block';
        draggedCard = null;
    });
}

// 2. Fetch Initial Tasks from the Backend Server
async function fetchTasks() {
    try {
        const response = await fetch('/api/tasks');
        const tasks = await response.json();

        tasks.forEach(task => {
            const card = document.createElement('div');
            card.classList.add('task-card');
            card.innerText = task.text;

            // Enable dragging on this fetched card
            attachDragEvents(card);

            // Append to the correct column list
            const targetList = document.getElementById(`list-${task.status}`);
            if (targetList) {
                targetList.appendChild(card);
            }
        });
    } catch (error) {
        console.error("Error fetching tasks from server:", error);
    }
}

// 3. Setup Columns for Drag Over and Drop Interactions
const columns = document.querySelectorAll('.task-list');
columns.forEach(column => {
    column.addEventListener('dragover', (e) => {
        e.preventDefault(); 
    });

    column.addEventListener('dragenter', (e) => {
        e.preventDefault();
        column.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
    });

    column.addEventListener('dragleave', () => {
        column.style.backgroundColor = '';
    });

    column.addEventListener('drop', async () => {
        column.style.backgroundColor = '';
        if (draggedCard) {
            column.appendChild(draggedCard);

            // Extract the text of the card and the new column status
            const taskText = draggedCard.innerText;
            // Extracts 'to-do', 'in-progress', or 'done' from 'list-to-do'
            const newStatus = column.id.replace('list-', ''); 

            // Send a POST request to the backend updating the status
            try {
                await fetch('/api/tasks/update', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ taskText, newStatus })
                });
            } catch (error) {
                console.error("Failed to save card placement:", error);
            }
        }
    });
});

// 4. Handle Creating New Cards from Input Fields (Frontend + Backend)
const columnsContainers = document.querySelectorAll('.column');
columnsContainers.forEach(column => {
    const button = column.querySelector('.add-btn');
    const input = column.querySelector('.task-input');
    const taskList = column.querySelector('.task-list');

    button.addEventListener('click', async () => {
        const taskText = input.value.trim();
        // Extract status name (e.g., 'to-do', 'in-progress', 'done')
        const status = taskList.id.replace('list-', ''); 
        
        if (taskText !== "") {
            try {
                // Send the new task data to the backend first
                const response = await fetch('/api/tasks', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: taskText, status: status })
                });

                if (response.ok) {
                    // If backend saved it successfully, display it on screen
                    const newCard = document.createElement('div');
                    newCard.classList.add('task-card');
                    newCard.innerText = taskText;

                    attachDragEvents(newCard);
                    taskList.appendChild(newCard);
                    input.value = "";
                }
            } catch (error) {
                console.error("Failed to save new task to backend:", error);
            }
        }
    });

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            button.click();
        }
    });
});
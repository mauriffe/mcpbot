let ws;
let isElicitationPending = false;

function connect() {
    ws = new WebSocket(`ws://${window.location.host}/ws`);

    ws.onopen = () => {
        document.getElementById('status').textContent = '✓ Connected';
        document.getElementById('status').className = 'status';
        document.getElementById('messageInput').disabled = false;
        document.getElementById('sendButton').disabled = false;
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };

    ws.onclose = () => {
        document.getElementById('status').textContent = '✗ Disconnected';
        document.getElementById('status').className = 'status error';
        document.getElementById('messageInput').disabled = true;
        document.getElementById('sendButton').disabled = true;
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

function handleMessage(data) {
    const messagesDiv = document.getElementById('messages');

    if (data.type === 'system') {
        addMessage(data.message, 'system', null, false);
    } else if (data.type === 'user') {
        addMessage(data.message, 'user', 'You', false);
    } else if (data.type === 'assistant') {
        // Remove thinking indicator
        const thinking = messagesDiv.querySelector('.thinking');
        if (thinking) thinking.remove();

        addMessage(data.message, 'assistant', 'Gemini', true);
    } else if (data.type === 'thinking') {
        addMessage(data.message, 'thinking', null, false);
    } else if (data.type === 'elicitation') {
        isElicitationPending = true;
        addMessage('⚠️ ' + data.message, 'elicitation', 'Server', false);
        document.getElementById('messageInput').placeholder = 'Type your response... (or type "cancel")';
    } else if (data.type === 'error') {
        addMessage('Error: ' + data.message, 'system', null, false);
    }
}

function addMessage(text, className, sender, useMarkdown) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;

    // Add sender and timestamp if provided
    if (sender) {
        const now = new Date();
        const time = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });

        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';

        const senderSpan = document.createElement('span');
        senderSpan.className = 'message-sender';
        senderSpan.textContent = sender;

        const timestampSpan = document.createElement('span');
        timestampSpan.className = 'message-timestamp';
        timestampSpan.textContent = time;

        headerDiv.appendChild(senderSpan);
        headerDiv.appendChild(timestampSpan);

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        if (useMarkdown) {
            // Render markdown content
            contentDiv.innerHTML = marked.parse(text);
        } else {
            contentDiv.textContent = text;
        }

        messageDiv.appendChild(headerDiv);
        messageDiv.appendChild(contentDiv);
    } else {
        // For system messages without sender
        if (useMarkdown) {
            messageDiv.innerHTML = marked.parse(text);
        } else {
            messageDiv.textContent = text;
        }
    }

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message) return;

    ws.send(JSON.stringify({
        type: isElicitationPending ? 'elicitation_response' : 'message',
        message: message
    }));

    input.value = '';

    if (isElicitationPending) {
        isElicitationPending = false;
        document.getElementById('messageInput').placeholder = 'Type your message...';
    }
}

document.getElementById('sendButton').addEventListener('click', sendMessage);
document.getElementById('messageInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

document.getElementById('resetButton').addEventListener('click', () => {
    if (confirm('Are you sure you want to reset the chat? This will clear all messages and history.')) {
        // Clear the UI
        document.getElementById('messages').innerHTML = '';

        // Send reset command to server
        ws.send(JSON.stringify({
            type: 'reset'
        }));

        // Add confirmation message
        addMessage('Chat has been reset', 'system', null, false);
    }
});

connect();
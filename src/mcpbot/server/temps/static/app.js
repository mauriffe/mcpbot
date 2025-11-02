let ws;
let isElicitationPending = false;
let chartInstances = {}; // Store chart instances for cleanup

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
        // Check if the message contains chart data
        console.log('Received assistant message, checking for chart data:', data.message);
        const hasChart = tryParseChartData(data.message);
        if (!hasChart) {
            console.log('No chart found, adding regular message');
            // No chart found, display as regular markdown message
            addMessage(data.message, 'assistant', 'Gemini', true);
        }
        // If chart was found and rendered, we don't add the text message
    } else if (data.type === 'thinking') {
        addMessage(data.message, 'thinking', null, false);
    } else if (data.type === 'elicitation') {
        isElicitationPending = true;
        addMessage('⚠️ ' + data.message, 'elicitation', 'Server', false);
        document.getElementById('messageInput').placeholder = 'Type your response... (or type "cancel")';
    } else if (data.type === 'error') {
        addMessage('Error: ' + data.message, 'system', null, false);
    } else if (data.type === 'tool_log') {
        // addToolLog(data.message, data.level);
        addMessage('Tool: ' + data.message, 'system', null, false);
    }
}

function tryParseChartData(text) {
    try {
        console.log('Trying to parse chart data from text');
        // First, try to extract JSON from markdown code blocks
        const codeBlockMatch = text.match(/```json\s*([\s\S]*?)\s*```/);
        if (codeBlockMatch) {
            try {
                const chartData = JSON.parse(codeBlockMatch[1]);
                if (chartData.chart_type === 'echarts' && chartData.config) {
                    // Extract text before and after the chart
                    const beforeChart = text.substring(0, text.indexOf('```json')).trim();
                    const afterChart = text.substring(text.indexOf('```', text.indexOf('```json') + 7) + 3).trim();
                    
                    // Add text before chart if it exists
                    if (beforeChart) {
                        addMessage(beforeChart, 'assistant', 'Gemini', true);
                    }
                    
                    // Render the chart
                    renderChart(chartData);
                    
                    // Add text after chart if it exists
                    if (afterChart) {
                        addMessage(afterChart, 'assistant', 'Gemini', true);
                    }
                    
                    return true;
                }
            } catch (e) {
                console.log('Failed to parse JSON from code block:', e);
            }
        }

        // Try to find JSON chart data directly in the text
        const jsonMatch = text.match(/\{[\s\S]*?"chart_type"\s*:\s*"echarts"[\s\S]*?\}/);
        if (jsonMatch) {
            try {
                const chartData = JSON.parse(jsonMatch[0]);
                if (chartData.chart_type === 'echarts' && chartData.config) {
                    renderChart(chartData);
                    return true;
                }
            } catch (e) {
                console.log('Failed to parse JSON from text:', e);
            }
        }

        // Try parsing the entire text as JSON
        try {
            const chartData = JSON.parse(text);
            if (chartData.chart_type === 'echarts' && chartData.config) {
                renderChart(chartData);
                return true;
            }
        } catch (e) {
            // Not valid JSON
        }
    } catch (e) {
        console.error('Error in tryParseChartData:', e);
    }
    return false;
}

function renderChart(chartData) {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant chart-message';

    const now = new Date();
    const time = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });

    // Create header
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';

    const senderSpan = document.createElement('span');
    senderSpan.className = 'message-sender';
    senderSpan.textContent = 'Gemini';

    const timestampSpan = document.createElement('span');
    timestampSpan.className = 'message-timestamp';
    timestampSpan.textContent = time;

    headerDiv.appendChild(senderSpan);
    headerDiv.appendChild(timestampSpan);

    // Create content div
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Add title if present
    if (chartData.title && chartData.title !== 'Chart') {
        const titleDiv = document.createElement('div');
        titleDiv.className = 'chart-title';
        titleDiv.textContent = chartData.title;
        contentDiv.appendChild(titleDiv);
    }

    // Add description if present
    if (chartData.description) {
        const descDiv = document.createElement('div');
        descDiv.className = 'chart-description';
        descDiv.textContent = chartData.description;
        contentDiv.appendChild(descDiv);
    }

    // Create chart container
    const chartContainer = document.createElement('div');
    chartContainer.className = 'chart-container';
    const chartId = 'chart-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    chartContainer.id = chartId;
    contentDiv.appendChild(chartContainer);

    messageDiv.appendChild(headerDiv);
    messageDiv.appendChild(contentDiv);
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    // Initialize ECharts
    setTimeout(() => {
        const chartDom = document.getElementById(chartId);
        if (chartDom) {
            // Dispose existing chart if any
            if (chartInstances[chartId]) {
                chartInstances[chartId].dispose();
            }

            try {
                const myChart = echarts.init(chartDom);
                chartInstances[chartId] = myChart;

                // Set default theme if not specified
                const option = {
                    backgroundColor: 'transparent',
                    ...chartData.config
                };

                myChart.setOption(option);

                // Handle window resize
                const resizeHandler = () => {
                    if (myChart && !myChart.isDisposed()) {
                        myChart.resize();
                    }
                };
                window.addEventListener('resize', resizeHandler);
                
                // Store resize handler for cleanup
                chartContainer.dataset.resizeHandler = 'attached';
            } catch (e) {
                console.error('Error initializing chart:', e);
                contentDiv.innerHTML = '<div style="color: red;">Error rendering chart: ' + e.message + '</div>';
            }
        }
    }, 100);
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
        // Dispose all chart instances
        Object.values(chartInstances).forEach(chart => {
            if (chart) chart.dispose();
        });
        chartInstances = {};

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
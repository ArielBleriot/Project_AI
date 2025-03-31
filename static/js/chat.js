const API_URL = 'http://127.0.0.1:5000'; // Replace with your API URL

const messagesContainer = document.getElementById('messages');
const inputField = document.getElementById('inputField');
const sendButton = document.getElementById('sendButton');

// Fetch the conversation history when the page loads
window.onload = function() {
    fetchConversationHistory();
};

function fetchConversationHistory() {
    fetch(`${API_URL}/historymessage/`)
        .then(response => response.json())
        .then(data => {
            console.log('API Response:', data); // Log the full response for debugging

            if (data.message) {
                displayMessage('system', data.message);
            } else {
                const conversationHistory = data.conversation_history;
                if (Array.isArray(conversationHistory)) {
                    conversationHistory.forEach(message => {
                        displayMessage(message.sender, message.content);
                    });
                } else {
                    console.error('Invalid conversation history format:', conversationHistory);
                }
            }
        })
        .catch(error => console.error('Error fetching conversation history:', error));
}

// This is your display function to show messages, modify it as needed
function displayMessage(sender, content) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.classList.add(sender); // Adds sender as a class, for styling (e.g., user or assistant)
    messageElement.textContent = content;
    document.getElementById('conversation').appendChild(messageElement); // Assuming #conversation is your message container
}

function displayMessage(sender, content) {
    const messageDiv = document.createElement('div');
    messageDiv.textContent = `${sender}: ${content}`;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight; // Scroll to the bottom
}

function sendMessage() {
    const userMessage = inputField.value.trim();
    if (userMessage) {
        displayMessage('You', userMessage);
        inputField.value = ''; // Clear input field

        // Send message to API
        fetch(`${API_URL}/usermessage/?&message=${encodeURIComponent(userMessage)}`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            const assistantResponse = data.response;
            displayMessage('Assistant', assistantResponse);
        })
        .catch(error => console.error('Error sending message:', error));
    }
}

// Send message when clicking the send button
sendButton.addEventListener('click', sendMessage);

// Send message when "Enter" is pressed
inputField.addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});
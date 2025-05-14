// Chatbot functionality
let chatbotVisible = false;

function toggleChatbot() {
    const chatbot = document.getElementById('chatbot');
    chatbotVisible = !chatbotVisible;
    chatbot.style.display = chatbotVisible ? 'flex' : 'none';
}

function sendMessage() {
    const input = document.getElementById('user-message');
    const message = input.value.trim();
    
    if (message) {
        // Add user message to chat
        addMessageToChat('user', message);
        
        // Clear input
        input.value = '';
        
        // Send to backend and get response
        fetch('/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            addMessageToChat('bot', data.response);
        })
        .catch(error => {
            console.error('Error:', error);
            addMessageToChat('bot', 'Sorry, I encountered an error. Please try again.');
        });
    }
}

function addMessageToChat(type, message) {
    const messagesDiv = document.getElementById('chatbot-messages');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', type === 'user' ? 'user-message' : 'bot-message');
    messageDiv.textContent = message;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Handle enter key in chat input
document.getElementById('user-message')?.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Provider dashboard availability toggle
const availabilityToggle = document.getElementById('availabilityToggle');
if (availabilityToggle) {
    availabilityToggle.addEventListener('change', function() {
        // Send availability update to backend
        fetch('/provider/update-availability', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ available: this.checked })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Availability updated successfully', 'success');
            } else {
                showAlert('Failed to update availability', 'danger');
                this.checked = !this.checked;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Failed to update availability', 'danger');
            this.checked = !this.checked;
        });
    });
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.classList.add('alert', `alert-${type}`, 'alert-dismissible', 'fade', 'show');
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

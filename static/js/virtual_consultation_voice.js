// Initialize Socket.IO
const socket = io();
const chatContainer = document.getElementById('chatContainer');

// Scroll chat to bottom
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Add message to chat
// Add message to chat
function addMessage(sender, text, isUser) {
    const now = new Date();
    const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'doctor-message'}`;

    if (!isUser) {
        messageDiv.innerHTML = `
            <div class="d-flex align-items-center mb-2">
                <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" 
                     style="width: 30px; height: 30px;">
                    <i class="fas fa-user-md"></i>
                </div>
                <strong class="ms-2">Dr. AI</strong>
            </div>
            <p>${text}</p>
            <div class="message-time">${timeString}</div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="d-flex align-items-center mb-2">
                <div class="bg-secondary text-white rounded-circle d-flex align-items-center justify-content-center" 
                     style="width: 30px; height: 30px;">
                    <i class="fas fa-user"></i>
                </div>
                <strong class="ms-2">You</strong>
            </div>
            <p>${text}</p>
            <div class="message-time">${timeString}</div>
        `;
    }

    document.getElementById('chatContainer').appendChild(messageDiv);
}

// Send message to AI Doctor API
document.getElementById('sendMessage').addEventListener('click', async function () {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (message) {
        addMessage('You', message, true);
        input.value = '';

        // Show typing indicator
        document.getElementById('typingIndicator').style.display = 'inline-block';

        try {
            const response = await fetch('/ai_doctor_chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, specialization: 'general', language: 'en' })
            });

            const data = await response.json();
            document.getElementById('typingIndicator').style.display = 'none';

            if (data.status === 'success') {
                addMessage('AI Doctor', data.response.message, false);
            } else {
                addMessage('System', 'Error: ' + data.message, false);
            }
        } catch (error) {
            console.error('Error:', error);
            addMessage('System', 'Network error. Please try again.', false);
        }
    }
});

// End consultation
document.getElementById('endConsultation').addEventListener('click', async function () {
    Swal.fire({
        title: 'End Consultation?',
        text: 'Are you sure you want to end this consultation?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, End It',
        cancelButtonText: 'Cancel'
    }).then(async (result) => {
        if (result.isConfirmed) {
            try {
                const response = await fetch('/complete_appointment', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ appointment_id: appointmentId })
                });

                const data = await response.json();

                if (data.status === 'success') {
                    Swal.fire('Consultation Completed', 'The appointment has been marked as completed.', 'success')
                        .then(() => window.location.href = '/doctors');
                } else {
                    Swal.fire('Error', data.message || 'Failed to complete consultation.', 'error');
                }
            } catch (error) {
                console.error('Error completing consultation:', error);
                Swal.fire('Error', 'Network error. Please try again.', 'error');
            }
        }
    });
});
// Receive AI response
socket.on('ai_response', (data) => {
    hideTypingIndicator();

    if (data.response_text) {
        addMessage('AI Doctor', data.response_text, false);
    }
});

// Handle connection errors
socket.on('connect_error', (error) => {
    addMessage('System', 'Connection error. Please refresh the page.', false);
    console.error('Socket error:', error);
});

// Initial scroll to bottom
scrollToBottom();
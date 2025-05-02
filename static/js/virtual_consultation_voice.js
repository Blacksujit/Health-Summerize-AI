// Initialize Socket.IO
const socket = io();
const chatContainer = document.getElementById('chatContainer');

// Scroll chat to bottom
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

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

    chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Show typing indicator
function showTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.style.display = 'inline-block';
    scrollToBottom();
}

// Hide typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.style.display = 'none';
}

// Send text message
document.getElementById('sendMessage').addEventListener('click', function () {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (message) {
        addMessage('You', message, true);
        input.value = '';

        // Show typing indicator
        showTypingIndicator();

        // Send to server
        socket.emit('process_text', {
            appointment_id: appointmentId,
            text: message
        });
    }
});

// Also send on Enter key
document.getElementById('messageInput').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        document.getElementById('sendMessage').click();
    }
});

// End consultation
document.getElementById("endConsultation").addEventListener("click", async function () {
    Swal.fire({
        title: "End Consultation?",
        text: "Are you sure you want to end this consultation?",
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Yes, End It",
        cancelButtonText: "Cancel",
    }).then(async (result) => {
        if (result.isConfirmed) {
            try {
                const response = await fetch("/complete_appointment", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ appointment_id: appointmentId }),
                });

                const data = await response.json();

                if (data.status === "success") {
                    Swal.fire({
                        icon: "success",
                        title: "Consultation Completed",
                        text: "The appointment has been marked as completed.",
                        timer: 2000,
                        showConfirmButton: false,
                    }).then(() => {
                        window.location.href = "/doctors";
                    });
                } else {
                    Swal.fire({
                        icon: "error",
                        title: "Error",
                        text: data.message || "Failed to complete consultation.",
                        confirmButtonText: "OK",
                    });
                }
            } catch (error) {
                console.error("Error completing consultation:", error);
                Swal.fire({
                    icon: "error",
                    title: "Network Error",
                    text: "There was an issue completing the consultation. Please try again.",
                    confirmButtonText: "OK",
                });
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
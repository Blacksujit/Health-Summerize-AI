 
// Initialize Socket.IO
const socket = io();
let mediaRecorder;
let audioChunks = [];
const appointmentId = "{{ appointment_id }}";
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
                <strong class="ms-2">Dr. {{ appointment_data.doctor.split(' ')[0] }}</strong>
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
    document.getElementById('typingIndicator').style.display = 'none';
}

// Start recording
document.getElementById('startRecording').addEventListener('click', function() {
    const button = this;
    
    if (button.classList.contains('recording')) {
        // Stop recording
        button.classList.remove('recording');
        button.innerHTML = '<i class="fas fa-microphone"></i>';
        stopRecording();
    } else {
        // Start recording
        button.classList.add('recording');
        button.innerHTML = '<i class="fas fa-stop"></i>';
        startRecording();
    }
});

// Start recording function
function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();
            
            audioChunks = [];
            
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('audio', audioBlob);
                formData.append('appointment_id', appointmentId);
                
                // Show user message placeholder
                addMessage('You', '[Voice message]', true);
                
                // Show typing indicator while processing
                showTypingIndicator();
                
                // Send to server
                fetch('/upload_audio', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    // Send to server for processing
                    socket.emit('process_voice', {
                        appointment_id: appointmentId,
                        audio_file_path: data.file_path
                    });
                })
                .catch(error => {
                    console.error('Error:', error);
                    hideTypingIndicator();
                    addMessage('System', 'Error processing voice message', false);
                });
            };
        })
        .catch(error => {
            console.error('Error accessing microphone:', error);
            addMessage('System', 'Could not access microphone. Please check permissions.', false);
        });
}

// Stop recording function
function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
}

// Send text message
document.getElementById('sendMessage').addEventListener('click', function() {
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
document.getElementById('messageInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        document.getElementById('sendMessage').click();
    }
});

document.getElementById('endConsultation').addEventListener('click', async function() {
    if (confirm('Are you sure you want to end this consultation?')) {
        try {
            const response = await fetch("{{ url_for('main.complete_appointment') }}", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ appointment_id: "{{ appointment_id }}" })
            });

            const data = await response.json();

            if (data.status === 'success') {
                alert('Consultation completed successfully.');
                window.location.href = "{{ url_for('main.doctors') }}";
            } else {
                alert('Error: ' + (data.message || 'Failed to complete consultation'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Network error completing consultation.');
        }
    }
});
// Receive AI response
// Modify the ai_voice_response handler
socket.on('ai_voice_response', (data) => {
hideTypingIndicator();

if (data.response_text) {
addMessage('AI Doctor', data.response_text, false);

// Speech synthesis with lip sync
const utterance = new SpeechSynthesisUtterance(data.response_text);
utterance.lang = 'en-US';

utterance.onstart = () => {
    startLipSync();
};

utterance.onend = () => {
    stopLipSync();
};

speechSynthesis.speak(utterance);
}

if (data.response_audio) {
const audio = new Audio(data.response_audio);
audio.play().catch(e => console.error('Error playing audio:', e));
audio.addEventListener('play', startLipSync);
audio.addEventListener('ended', stopLipSync);
}
});



// Handle connection errors
socket.on('connect_error', (error) => {
    addMessage('System', 'Connection error. Please refresh the page.', false);
    console.error('Socket error:', error);
});

// Initial scroll to bottom
scrollToBottom();

// Add after socket initialization
let mixer, avatarMesh;
const clock = new THREE.Clock();

// Initialize 3D scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(800, 600);
document.getElementById('sceneContainer').appendChild(renderer.domElement);

// Add lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
scene.add(ambientLight);
const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(5, 5, 5);
scene.add(directionalLight);

// Load avatar model
const loader = new THREE.GLTFLoader();
document.getElementById('loadingOverlay').style.display = 'flex';
loader.load(
'/static/avatar-images/model.glb',
function(gltf) {
avatarMesh = gltf.scene;
scene.add(avatarMesh);
avatarMesh.position.set(0, -1, 0);
camera.position.z = 3;
mixer = new THREE.AnimationMixer(avatarMesh);
document.getElementById('loadingOverlay').style.display = 'none';
animate();
},
undefined,
function(error) {
console.error('Error loading avatar:', error);
}
);

function animate() {
requestAnimationFrame(animate);
const delta = clock.getDelta();
if (mixer) mixer.update(delta);
renderer.render(scene, camera);
}

// Add lip sync animation
function startLipSync() {
if (avatarMesh) {
avatarMesh.traverse(child => {
    if (child.isMesh && child.name === 'Mouth') {
        child.material.emissive = new THREE.Color(0xff0000);
        child.material.needsUpdate = true;
        child.visible = true;
    }
});
}
}

function stopLipSync() {
if (avatarMesh) {
avatarMesh.traverse(child => {
    if (child.isMesh && child.name === 'Mouth') {
        child.material.emissive = new THREE.Color(0x000000);
        child.visible = false;
    }
});
}
}
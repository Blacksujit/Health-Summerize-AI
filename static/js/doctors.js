// Notify user with SweetAlert after booking an appointment
document
    .querySelector('form[action="/book"]')
    .addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent the default form submission

        const form = this;
        const formData = new FormData(form);

        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Show SweetAlert popup for success
            Swal.fire({
                icon: "success",
                title: "Appointment Booked!",
                text: "Your appointment has been booked successfully.",
                confirmButtonText: "OK",
            }).then(() => {
                // Clear the form after success
                form.reset();

                // Fetch and update the appointments list dynamically
                fetchUpdatedAppointments();
            });
        } catch (error) {
            console.error("Error booking appointment:", error);

            // Show SweetAlert popup for error
            Swal.fire({
                icon: "error",
                title: "Error",
                text: "There was an issue booking your appointment. Please try again.",
                confirmButtonText: "OK",
            });
        }
    });

// Function to fetch and update the appointments list dynamically
async function fetchUpdatedAppointments() {
    try {
        const response = await fetch('/get_appointments');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.status === "success") {
            updateAppointmentsList(data.appointments);
            // Also update completed appointments
            if(data.completed_appointments) {
                updateCompletedAppointmentsList(data.completed_appointments);
            }
        } else {
            console.error("Error fetching appointments:", data.message);
        }
    } catch (error) {
        console.error("Error fetching appointments:", error);
    }
}

// Function to update the "Your Appointments" list in the DOM
function updateAppointmentsList(appointments) {
    const appointmentsContainer = document.querySelector(".card.appointment-card .list-group");
    
    if (!appointmentsContainer) return;

    if (appointments.length > 0) {
        appointmentsContainer.innerHTML = appointments
            .map(
                (appointment) => `
  <div class="list-group-item list-group-item-action">
    <div class="d-flex justify-content-between align-items-start">
      <div class="me-3">
        <span class="badge bg-primary badge-status mb-2">
          <i class="fas fa-clock me-1"></i>Scheduled
        </span>
        <h5 class="mb-1">${appointment.doctor}</h5>
        <small class="text-muted">
          <i class="fas fa-user me-1"></i>${appointment.patient}
        </small>
        <div class="mt-2">
          <small>
            <i class="fas fa-calendar me-1"></i>${appointment.time}
          </small>
        </div>
      </div>
      <div class="text-end">
        <small class="d-block text-muted mb-2">ID: ${appointment.appointment_id}</small>
        <button
          class="btn btn-sm btn-outline-primary copy-btn"
          onclick="copyToClipboard('${appointment.appointment_id}')"
        >
          <i class="fas fa-copy me-1"></i>Copy ID
        </button>
      </div>
    </div>
  </div>
`
            )
            .join("");
    } else {
        appointmentsContainer.innerHTML = `
<div class="text-center py-4">
  <i class="fas fa-calendar-times fa-3x text-muted mb-3"></i>
  <p class="text-muted">No upcoming appointments</p>
</div>
`;
    }
}

// Function to update the "Completed Appointments" list in the DOM
function updateCompletedAppointmentsList(appointments) {
    const completedContainer = document.querySelector(".card.completed-card .list-group");
    
    if (!completedContainer) return;

    if (appointments.length > 0) {
        completedContainer.innerHTML = appointments
            .map(
                (appointment) => `
  <div class="list-group-item">
    <div class="d-flex justify-content-between align-items-start">
      <div class="me-3">
        <span class="badge bg-success badge-status mb-2">
          <i class="fas fa-check me-1"></i>Completed
        </span>
        <h5 class="mb-1">${appointment.doctor}</h5>
        <small class="text-muted">
          <i class="fas fa-user me-1"></i>${appointment.patient}
        </small>
      </div>
      <div>
        <small class="text-muted">
          <i class="fas fa-calendar me-1"></i>${appointment.time}
        </small>
      </div>
    </div>
  </div>
`
            )
            .join("");
    } else {
        completedContainer.innerHTML = `
<div class="text-center py-4">
  <i class="fas fa-calendar-check fa-3x text-muted mb-3"></i>
  <p class="text-muted">No completed appointments yet</p>
</div>
`;
    }
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show toast notification
        const toast = document.createElement("div");
        toast.className = "position-fixed bottom-0 end-0 p-3";
        toast.innerHTML = `
                <div class="toast show" role="alert">
                    <div class="toast-body bg-primary text-white">
                        <i class="fas fa-check-circle me-2"></i>Appointment ID copied!
                    </div>
                </div>
            `;
        document.body.appendChild(toast);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 2000);
    });
}

// Complete appointment
function completeAppointment(appointmentId) {
    if (!appointmentId) return;
    
    fetch('/complete_appointment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ appointment_id: appointmentId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            Swal.fire({
                icon: 'success',
                title: 'Appointment Completed',
                text: 'The appointment has been marked as completed.',
                confirmButtonText: 'OK'
            }).then(() => {
                // Redirect to doctors page with hash to scroll to consultations
                window.location.href = '/doctors#consultations';
                // Force refresh
                fetchUpdatedAppointments();
            });
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: data.message || 'There was an issue completing the appointment.',
                confirmButtonText: 'OK'
            });
        }
    })
    .catch(error => {
        console.error('Error completing appointment:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'There was an issue connecting to the server. Please try again.',
            confirmButtonText: 'OK'
        });
    });
}

// Validate appointment
document.getElementById("validateAppointment")?.addEventListener("click", async () => {
    const appointmentId = document.getElementById("appointmentIdInput").value.trim();

    if (!appointmentId) {
        Swal.fire({
            icon: "warning",
            title: "Missing Appointment ID",
            text: "Please enter an appointment ID to validate.",
            confirmButtonText: "OK",
        });
        return;
    }

    try {
        const response = await fetch('/validate_appointment', {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ appointment_id: appointmentId }),
        });

        const data = await response.json();

        if (data.status === "success") {
            Swal.fire({
                icon: "success",
                title: "Appointment Validated",
                text: "Redirecting to the consultation page...",
                timer: 2000,
                showConfirmButton: false,
            }).then(() => {
                window.location.href = data.redirect_url;
            });
        } else {
            Swal.fire({
                icon: "error",
                title: "Validation Failed",
                text: data.message || "Invalid appointment ID. Please try again.",
                confirmButtonText: "OK",
            });
        }
    } catch (error) {
        console.error("Validation error:", error);
        Swal.fire({
            icon: "error",
            title: "Server Error",
            text: "An error occurred while validating the appointment. Please try again later.",
            confirmButtonText: "OK",
        });
    }
});
// Show alert function
function showAlert(message, type) {
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} mt-3`;
    alertDiv.textContent = message;

    const container = document.querySelector(".col-lg-4 .card-body");
    if (container) {
        container.insertBefore(alertDiv, container.lastElementChild);
        setTimeout(() => alertDiv.remove(), 5000);
    }
}

// Add this to refresh appointments list on page load
window.addEventListener('load', () => {
    // Fetch updated appointments on page load
    fetchUpdatedAppointments();
    
    // Scroll to consultation section if coming from completed consultation
    if (window.location.hash === '#consultations') {
        const consultationsSection = document.querySelector('.completed-card');
        if (consultationsSection) {
            consultationsSection.scrollIntoView();
        }
    }
});
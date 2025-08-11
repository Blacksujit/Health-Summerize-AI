// Notify user with SweetAlert after booking an appointment
const bookForm = document.querySelector('form[action="/book"]');
if (bookForm) {
    bookForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent the default form submission

        const form = this;
        const formData = new FormData(form);

        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                cache: 'no-store'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Try to get the new appointment from the response
            let data;
            try {
                data = await response.json();
            } catch (e) {
                data = {};
            }

            // Show SweetAlert popup for success with auto-close
            Swal.fire({
                icon: "success",
                title: "Appointment Booked!",
                text: "Your appointment has been booked successfully.",
                confirmButtonText: "OK",
                timer: 1800,
                timerProgressBar: true,
            }).then(() => {
                // Clear the form after success
                form.reset();

                // If server returned the newly created appointment(s), optimistically update UI
                if (data && data.status === 'success' && data.appointments) {
                    updateAppointmentsList(data.appointments);
                    if (data.completed_appointments) {
                        updateCompletedAppointmentsList(data.completed_appointments);
                    }
                } else {
                    // Fallback: fetch fresh data
                    fetchUpdatedAppointments();
                }
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
}

// Function to fetch and update the appointments list dynamically
async function fetchUpdatedAppointments() {
    try {
        const response = await fetch(`/get_appointments?_=${Date.now()}`, { cache: 'no-store', headers: { 'X-Requested-With': 'XMLHttpRequest' } });
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
    // Cache full list for filtering
    window.__ALL_APPOINTMENTS__ = Array.isArray(appointments) ? appointments : [];
    renderFilteredAppointments();
}

// Render appointments applying current search query
function renderFilteredAppointments() {
    const container = document.getElementById('appointmentsList');
    if (!container) return;

    const all = window.__ALL_APPOINTMENTS__ || [];
    const q = (document.getElementById('appointmentsSearch')?.value || '').trim().toLowerCase();

    const filtered = q
        ? all.filter(a =>
            String(a.appointment_id || '').toLowerCase().includes(q) ||
            String(a.doctor || '').toLowerCase().includes(q) ||
            String(a.patient || '').toLowerCase().includes(q) ||
            String(a.time || '').toLowerCase().includes(q)
          )
        : all;

    if (filtered.length > 0) {
        container.innerHTML = filtered.map((appointment) => `
<div class="modern-list-group-item animate__animated animate__fadeInUp">
  <div>
    <span class="modern-badge scheduled mb-2">
      <i class="fa fa-clock me-1"></i>Scheduled
    </span>
    <h5 class="mb-1" style="font-weight:700;">${appointment.doctor}</h5>
    <small class="text-muted d-block">
      <i class="fa fa-user me-1"></i>${appointment.patient}
    </small>
    <div class="mt-2">
      <small>
        <i class="fa fa-calendar me-1"></i>${appointment.time}
      </small>
    </div>
  </div>
  <div class="text-end">
    <small class="d-block text-muted mb-2" style="font-size:0.98em;">
      ID: <span class="fw-bold" style="color:#1a73e8;">${appointment.appointment_id}</span>
    </small>
    <button
      class="btn modern-copy-btn btn-sm"
      onclick="copyToClipboard('${appointment.appointment_id}')"
    >
      <i class="fa fa-copy me-1"></i>Copy ID
    </button>
  </div>
</div>
`).join('');
    } else {
        container.innerHTML = `
<div class="text-center py-4">
  <i class="fa fa-calendar-times fa-3x text-muted mb-3"></i>
  <p class="text-muted">No upcoming appointments</p>
</div>
`;
    }
}

// Function to update the "Completed Appointments" list in the DOM
function updateCompletedAppointmentsList(appointments) {
    const completedContainer = document.getElementById('completedAppointmentsList');
    if (!completedContainer) return;

    if (appointments.length > 0) {
        completedContainer.innerHTML = appointments
            .map(
                (appointment) => `
<div class="modern-list-group-item animate__animated animate__fadeInUp">
  <div>
    <span class="modern-badge success mb-2">
      <i class="fa fa-check me-1"></i>Completed
    </span>
    <h5 class="mb-1" style="font-weight:700;">${appointment.doctor}</h5>
    <small class="text-muted d-block">
      <i class="fa fa-user me-1"></i>${appointment.patient}
    </small>
    <div class="mt-2">
      <small>
        <i class="fa fa-calendar me-1"></i>${appointment.time}
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
  <i class="fa fa-calendar-check fa-3x text-muted mb-3"></i>
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

        // Remove after 2 seconds
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
    // Wire up live search for appointments list
    const search = document.getElementById('appointmentsSearch');
    if (search) {
        search.addEventListener('input', renderFilteredAppointments);
        // Enter key triggers search
        search.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                renderFilteredAppointments();
            }
        });
    }
    // Search button click
    const searchBtn = document.getElementById('appointmentsSearchBtn');
    if (searchBtn) {
        searchBtn.addEventListener('click', renderFilteredAppointments);
    }
});
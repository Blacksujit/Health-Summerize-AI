// <!-- Custom JS -->
// <script>
// Notify user with SweetAlert after booking an appointment
document
    .querySelector('form[action="{{ url_for("main.book") }}"]')
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
        const response = await fetch('{{ url_for("main.get_appointments") }}');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.status === "success") {
            updateAppointmentsList(data.appointments);
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

// Validate appointment
document.getElementById("validateAppointment").addEventListener("click", async () => {
    const appointmentId = document.getElementById("appointmentIdInput").value.trim();

    if (!appointmentId) {
        showAlert("Please enter an appointment ID", "danger");
        return;
    }

    try {
        const response = await fetch(validateAppointmentUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ appointment_id: appointmentId })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.status === "success") {
            window.location.href = data.redirect_url;
        } else {
            showAlert(data.message || "Invalid appointment ID", "danger");
        }
    } catch (error) {
        console.error("Validation error:", error);
        showAlert("Error validating appointment. Please try again.", "danger");
    }
});
// Show alert function
function showAlert(message, type) {
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} mt-3`;
    alertDiv.textContent = message;

    const container = document.querySelector(".col-lg-4 .card-body");
    container.insertBefore(alertDiv, container.lastElementChild);

    setTimeout(() => alertDiv.remove(), 5000);
}
// Add this to doctors.html to refresh appointments list
window.addEventListener('load', () => {
    if (performance.navigation.type === 1) { // Check if page was reloaded
        // Scroll to consultation section if coming from completed consultation
        if (window.location.hash === '#consultations') {
            document.getElementById('consultations').scrollIntoView();
        }
    }
});

// </script>
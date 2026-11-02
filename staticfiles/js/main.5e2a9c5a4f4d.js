/**
 * SehatConnect — Front-end Logic & Interactive Components
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // 2. Dynamic Hospital-to-Doctor Dropdown in Appointment Booking
    const hospitalSelect = document.getElementById('id_hospital');
    const doctorSelect = document.getElementById('id_doctor');

    if (hospitalSelect && doctorSelect) {
        hospitalSelect.addEventListener('change', function () {
            const hospitalId = this.value;
            if (!hospitalId) {
                doctorSelect.innerHTML = '<option value="">-- First Select Healthcare Facility --</option>';
                return;
            }

            doctorSelect.innerHTML = '<option value="">Loading available doctors...</option>';

            fetch(`/appointments/api/doctors-by-hospital/${hospitalId}/`)
                .then(response => response.json())
                .then(data => {
                    doctorSelect.innerHTML = '<option value="">-- Choose Specialist Doctor --</option>';
                    if (data.doctors && data.doctors.length > 0) {
                        data.doctors.forEach(doc => {
                            const option = document.createElement('option');
                            option.value = doc.id;
                            option.textContent = `${doc.name} (${doc.room})`;
                            doctorSelect.appendChild(option);
                        });
                    } else {
                        doctorSelect.innerHTML = '<option value="">No active doctors available at this facility</option>';
                    }
                })
                .catch(err => {
                    console.error('Error fetching doctors:', err);
                    doctorSelect.innerHTML = '<option value="">Error loading doctors</option>';
                });
        });
    }

    // 3. Dynamic Slot Availability Verification
    const dateInput = document.getElementById('id_appointment_date');
    const slotSelect = document.getElementById('id_time_slot');

    function checkSlotAvailability() {
        if (!dateInput || !doctorSelect || !slotSelect) return;
        const doctorId = doctorSelect.value;
        const dateVal = dateInput.value;

        if (doctorId && dateVal) {
            fetch(`/appointments/api/available-slots/?doctor_id=${doctorId}&date=${dateVal}`)
                .then(res => res.json())
                .then(data => {
                    if (data.booked_slots) {
                        Array.from(slotSelect.options).forEach(opt => {
                            if (data.booked_slots.includes(opt.value)) {
                                opt.disabled = true;
                                if (!opt.textContent.includes('(Booked)')) {
                                    opt.textContent = `${opt.value} — [Booked / पहले से बुक]`;
                                }
                            } else {
                                opt.disabled = false;
                                opt.textContent = opt.value;
                            }
                        });
                    }
                })
                .catch(err => console.error('Error checking slots:', err));
        }
    }

    if (dateInput && doctorSelect && slotSelect) {
        dateInput.addEventListener('change', checkSlotAvailability);
        doctorSelect.addEventListener('change', checkSlotAvailability);
    }
});

/**
 * Helper to populate demo credentials on login page
 */
function fillDemoLogin(role) {
    const usernameInput = document.getElementById('id_username');
    const passwordInput = document.getElementById('id_password');
    if (!usernameInput || !passwordInput) return;

    if (role === 'worker') {
        usernameInput.value = 'asha_sunita';
        passwordInput.value = 'sunita123';
    } else if (role === 'doctor') {
        usernameInput.value = 'dr_sharma';
        passwordInput.value = 'sharma123';
    } else if (role === 'admin') {
        usernameInput.value = 'admin';
        passwordInput.value = 'admin123';
    }
}

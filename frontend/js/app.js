// CareSync Clinic SPA Application Controller
const API_URL = "http://127.0.0.1:8000";

// Client State
let token = localStorage.getItem("token") || "";
let currentUser = null;

// Initial Startup Check
document.addEventListener("DOMContentLoaded", () => {
    if (token) {
        verifySession();
    } else {
        showAuth();
    }
});

// Toast System helper
function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let iconName = type === "success" ? "check-circle" : "alert-circle";
    toast.innerHTML = `
        <i data-lucide="${iconName}"></i>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    lucide.createIcons(); // Initialize the new icon

    // Slide in
    setTimeout(() => toast.classList.add("show"), 10);

    // Slide out and destroy after 4 seconds
    setTimeout(() => {
        toast.classList.remove("show");
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

// Authentication View Transition
function showAuth() {
    localStorage.removeItem("token");
    token = "";
    currentUser = null;
    
    document.getElementById("app-view").style.display = "none";
    document.getElementById("auth-view").style.display = "flex";
    switchAuthTab("login");
    lucide.createIcons();
}

// Session Verification on page load
async function verifySession() {
    try {
        const res = await fetch(`${API_URL}/users/me`, {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        
        if (!res.ok) {
            throw new Error("Session expired");
        }
        
        currentUser = await res.json();
        showDashboard();
    } catch (err) {
        showAuth();
        showToast("Session expired. Please login again.", "error");
    }
}

// Tab Switching in Auth Form
function switchAuthTab(type) {
    const tabLogin = document.getElementById("tab-login");
    const tabRegister = document.getElementById("tab-register");
    const formLogin = document.getElementById("form-login");
    const formRegister = document.getElementById("form-register");

    if (type === "login") {
        tabLogin.classList.add("active");
        tabRegister.classList.remove("active");
        formLogin.style.display = "block";
        formRegister.style.display = "none";
    } else {
        tabLogin.classList.remove("active");
        tabRegister.classList.add("active");
        formLogin.style.display = "none";
        formRegister.style.display = "block";
    }
}

// Handle User Registration
async function handleRegister(event) {
    event.preventDefault();
    const fullName = document.getElementById("reg-name").value;
    const email = document.getElementById("reg-email").value;
    const password = document.getElementById("reg-password").value;
    const role = document.getElementById("reg-role").value;

    try {
        const res = await fetch(`${API_URL}/auth/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                full_name: fullName,
                email: email,
                password: password,
                role: role
            })
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || "Registration failed");
        }

        showToast("Registration successful! You can now log in.");
        // Auto-switch to login tab and prefill email
        switchAuthTab("login");
        document.getElementById("login-email").value = email;
        document.getElementById("form-register").reset();
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Handle User Login
async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    try {
        // FastAPI OAuth2PasswordRequestForm expects urlencoded payload
        const formDetails = new URLSearchParams();
        formDetails.append("username", email);
        formDetails.append("password", password);

        const res = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formDetails
        });

        const data = await res.json();
        if (!res.ok) {
            throw new Error(data.detail || "Incorrect username or password");
        }

        // Save token
        token = data.access_token;
        localStorage.setItem("token", token);
        
        // Fetch current user details
        await verifySession();
        showToast(`Welcome back, ${currentUser.full_name}!`);
        document.getElementById("form-login").reset();
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Handle Logout
function handleLogout() {
    showAuth();
    showToast("Signed out successfully.");
}

// Dashboard Transition and Interface Population
function showDashboard() {
    document.getElementById("auth-view").style.display = "none";
    document.getElementById("app-view").style.display = "grid";

    // Setup Sidebar Widgets
    document.getElementById("user-display-name").innerText = currentUser.full_name;
    document.getElementById("user-display-role").innerText = currentUser.role;
    document.getElementById("user-avatar").innerText = currentUser.full_name.charAt(0).toUpperCase();

    // Adjust widget styling based on role
    const roleBadge = document.getElementById("user-display-role");
    roleBadge.className = "user-role";
    roleBadge.classList.add(currentUser.role.toLowerCase());

    // Show menu corresponding to the logged in role
    const menus = ["patient-menu", "doctor-menu", "admin-menu"];
    menus.forEach(menu => {
        document.querySelector(`.${menu}`).style.display = "none";
    });
    document.querySelector(`.${currentUser.role.toLowerCase()}-menu`).style.display = "block";

    // Load Default Tab
    if (currentUser.role === "Patient") {
        showTab("patient-appointments");
    } else if (currentUser.role === "Doctor") {
        showTab("doctor-schedule");
    } else if (currentUser.role === "Admin") {
        showTab("admin-users");
    }
}

// SPA Routing controller
function showTab(tabName) {
    // Hide all view tabs
    const views = document.querySelectorAll(".tab-view");
    views.forEach(v => v.style.display = "none");

    // Show target tab
    document.getElementById(`tab-${tabName}`).style.display = "block";

    // Update active class in sidebar menu
    const menuItems = document.querySelectorAll(".menu-item");
    menuItems.forEach(item => item.classList.remove("active"));
    
    const navItem = document.getElementById(`nav-${tabName}`);
    if (navItem) navItem.classList.add("active");

    // Load data specific to that active tab viewport
    if (tabName === "patient-appointments") {
        fetchPatientAppointments();
    } else if (tabName === "patient-book") {
        fetchDoctorsList();
    } else if (tabName === "patient-profile") {
        fetchPatientProfile();
    } else if (tabName === "doctor-schedule") {
        fetchDoctorSchedule();
    } else if (tabName === "doctor-profile") {
        fetchDoctorProfile();
    } else if (tabName === "admin-users") {
        fetchAdminUsers();
    } else if (tabName === "admin-appointments") {
        fetchAdminAppointments();
    }
    
    lucide.createIcons();
}

/* API headers injection */
function getHeaders() {
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

/* ==========================================================================
   A. PATIENT DASHBOARD LOGIC
   ========================================================================== */

// Get patient demographic details
async function fetchPatientProfile() {
    try {
        const res = await fetch(`${API_URL}/patients/me`, {
            headers: getHeaders()
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        document.getElementById("pat-dob").value = data.date_of_birth || "";
        document.getElementById("pat-gender").value = data.gender || "";
        document.getElementById("pat-phone").value = data.phone || "";
        document.getElementById("pat-history").value = data.medical_history || "";
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Update patient profile
async function handlePatientProfileUpdate(event) {
    event.preventDefault();
    const dob = document.getElementById("pat-dob").value;
    const gender = document.getElementById("pat-gender").value;
    const phone = document.getElementById("pat-phone").value;
    const history = document.getElementById("pat-history").value;

    try {
        const res = await fetch(`${API_URL}/patients/me`, {
            method: "PUT",
            headers: getHeaders(),
            body: JSON.stringify({
                date_of_birth: dob || null,
                gender: gender || null,
                phone: phone || null,
                medical_history: history || null
            })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        showToast("Profile details updated successfully!");
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Get listing of active doctors and display as cards
async function fetchDoctorsList() {
    try {
        const res = await fetch(`${API_URL}/doctors/`, {
            headers: getHeaders()
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        const container = document.getElementById("doctor-cards-container");
        container.innerHTML = "";

        if (data.length === 0) {
            container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">No doctors are registered in the clinic yet.</div>`;
            return;
        }

        data.forEach(doc => {
            const card = document.createElement("div");
            card.className = "doctor-item-card fade-in";
            
            // Format time display
            const formatTime = (tStr) => {
                const parts = tStr.split(":");
                return `${parts[0]}:${parts[1]}`;
            };
            
            card.innerHTML = `
                <div>
                    <div class="doctor-info-header" style="margin-bottom: 12px;">
                        <div class="avatar">${doc.user.full_name.charAt(0).toUpperCase()}</div>
                        <div class="doctor-meta">
                            <h3>${doc.user.full_name}</h3>
                            <span class="doctor-spec">${doc.specialization}</span>
                        </div>
                    </div>
                    <p class="doctor-bio">${doc.bio || "No biography provided."}</p>
                </div>
                <div>
                    <div class="doctor-schedules-details" style="margin-bottom: 15px;">
                        <div class="schedule-row">
                            <span>Available Hours:</span>
                            <span class="val">${formatTime(doc.availability_start)} - ${formatTime(doc.availability_end)}</span>
                        </div>
                        <div class="schedule-row">
                            <span>Consultation Fee:</span>
                            <span class="val" style="color: var(--color-success); font-weight: 700;">$${doc.consultation_fee}</span>
                        </div>
                    </div>
                    <button class="btn btn-block" onclick="openBookingModal('${doc.id}', '${doc.user.full_name}', '${formatTime(doc.availability_start)}', '${formatTime(doc.availability_end)}')">
                        <i data-lucide="calendar"></i> Book Appointment
                    </button>
                </div>
            `;
            container.appendChild(card);
        });
        lucide.createIcons();
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Open booking overlays modal
function openBookingModal(doctorId, doctorName, start, end) {
    document.getElementById("modal-doctor-id").value = doctorId;
    document.getElementById("modal-doctor-name").innerText = `Book Consultation with ${doctorName}`;
    document.getElementById("modal-avail-note").innerText = `Doctor availability hours: ${start} - ${end}`;
    
    // Set default booking date as tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    document.getElementById("book-date").value = tomorrow.toISOString().split("T")[0];
    document.getElementById("book-time").value = "10:00";
    
    document.getElementById("booking-modal").classList.add("active");
}

function closeBookingModal() {
    document.getElementById("booking-modal").classList.remove("active");
}

// Submit Appointment Booking
async function submitBooking() {
    const doctorId = document.getElementById("modal-doctor-id").value;
    const bookDate = document.getElementById("book-date").value;
    const bookTime = document.getElementById("book-time").value;
    const notes = document.getElementById("book-notes").value;

    if (!bookDate || !bookTime) {
        showToast("Please choose a valid date and start time.", "error");
        return;
    }

    try {
        const res = await fetch(`${API_URL}/appointments/`, {
            method: "POST",
            headers: getHeaders(),
            body: JSON.stringify({
                doctor_id: doctorId,
                appointment_date: bookDate,
                start_time: `${bookTime}:00`, // Include seconds
                notes: notes || null
            })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        showToast("Appointment booked successfully!");
        closeBookingModal();
        showTab("patient-appointments"); // Redirect to appointments list
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Get patient booked appointments list
async function fetchPatientAppointments() {
    try {
        const res = await fetch(`${API_URL}/appointments/`, {
            headers: getHeaders()
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        // Fetch doctors list to map doctor IDs to names
        const docsRes = await fetch(`${API_URL}/doctors/`, { headers: getHeaders() });
        const doctorsList = await docsRes.json();
        const docMap = {};
        doctorsList.forEach(d => docMap[d.id] = d.user.full_name);

        const list = document.getElementById("patient-appointments-list");
        list.innerHTML = "";

        if (data.length === 0) {
            list.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-secondary);">You have no appointments booked.</td></tr>`;
            return;
        }

        data.forEach(appt => {
            const row = document.createElement("tr");
            
            const formatTime = (tStr) => tStr.split(":").slice(0, 2).join(":");
            const docName = docMap[appt.doctor_id] || "Doctor";
            
            let statusClass = appt.status.toLowerCase();
            let actionBtn = "";
            if (appt.status === "Scheduled") {
                actionBtn = `<button class="btn btn-danger btn-secondary" style="padding: 6px 12px; font-size: 0.8rem;" onclick="cancelAppointment('${appt.id}')"><i data-lucide="x-circle"></i> Cancel</button>`;
            } else {
                actionBtn = `<span style="color: var(--text-muted); font-size: 0.8rem;">No Actions Available</span>`;
            }

            row.innerHTML = `
                <td style="font-weight: 600;">${docName}</td>
                <td>${appt.appointment_date}</td>
                <td>${formatTime(appt.start_time)}</td>
                <td>${formatTime(appt.end_time)}</td>
                <td><span class="badge badge-${statusClass}">${appt.status}</span></td>
                <td style="font-size: 0.85rem; max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${appt.notes || ''}">${appt.notes || '-'}</td>
                <td>${actionBtn}</td>
            `;
            list.appendChild(row);
        });
        lucide.createIcons();
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Cancel appointment slot
async function cancelAppointment(apptId) {
    if (!confirm("Are you sure you want to cancel this appointment?")) return;

    try {
        const res = await fetch(`${API_URL}/appointments/${apptId}`, {
            method: "PUT",
            headers: getHeaders(),
            body: JSON.stringify({
                status: "Cancelled"
            })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        showToast("Appointment has been cancelled.");
        if (currentUser.role === "Patient") {
            fetchPatientAppointments();
        } else if (currentUser.role === "Doctor") {
            fetchDoctorSchedule();
        }
    } catch (err) {
        showToast(err.message, "error");
    }
}

/* ==========================================================================
   B. DOCTOR DASHBOARD LOGIC
   ========================================================================== */

// Get doctor schedule profile details
async function fetchDoctorProfile() {
    try {
        const res = await fetch(`${API_URL}/doctors/${currentUser.id}`, {
            headers: getHeaders()
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        document.getElementById("doc-spec").value = data.specialization || "";
        document.getElementById("doc-fee").value = data.consultation_fee || 0;
        document.getElementById("doc-bio").value = data.bio || "";
        document.getElementById("doc-start").value = data.availability_start.split(":").slice(0,2).join(":") || "09:00";
        document.getElementById("doc-end").value = data.availability_end.split(":").slice(0,2).join(":") || "17:00";
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Update doctor availability settings
async function handleDoctorProfileUpdate(event) {
    event.preventDefault();
    const spec = document.getElementById("doc-spec").value;
    const fee = document.getElementById("doc-fee").value;
    const bio = document.getElementById("doc-bio").value;
    const start = document.getElementById("doc-start").value;
    const end = document.getElementById("doc-end").value;

    try {
        const res = await fetch(`${API_URL}/doctors/me`, {
            method: "PUT",
            headers: getHeaders(),
            body: JSON.stringify({
                specialization: spec,
                consultation_fee: parseFloat(fee),
                bio: bio || null,
                availability_start: `${start}:00`,
                availability_end: `${end}:00`
            })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        showToast("Availability settings updated successfully!");
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Get listing of patient consultations scheduled with this doctor
async function fetchDoctorSchedule() {
    try {
        const res = await fetch(`${API_URL}/appointments/`, {
            headers: getHeaders()
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        // Fetch patient profiles to map patient IDs to patient names
        const patRes = await fetch(`${API_URL}/patients/`, { headers: getHeaders() });
        const patientsList = await patRes.json();
        const patMap = {};
        patientsList.forEach(p => patMap[p.id] = { name: p.user.full_name, history: p.medical_history });

        // Populate stats metrics
        document.getElementById("doc-stat-total").innerText = data.length;
        document.getElementById("doc-stat-scheduled").innerText = data.filter(a => a.status === "Scheduled").length;

        const list = document.getElementById("doctor-appointments-list");
        list.innerHTML = "";

        if (data.length === 0) {
            list.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-secondary);">No patients have booked appointments with you.</td></tr>`;
            return;
        }

        data.forEach(appt => {
            const row = document.createElement("tr");
            
            const formatTime = (tStr) => tStr.split(":").slice(0, 2).join(":");
            const patientMeta = patMap[appt.patient_id] || { name: "Patient Profile", history: "" };
            
            let statusClass = appt.status.toLowerCase();
            let actionBtn = "";
            
            if (appt.status === "Scheduled") {
                actionBtn = `
                    <div style="display: flex; gap: 8px;">
                        <button class="btn" style="padding: 6px 12px; font-size: 0.8rem; background: var(--color-success); box-shadow: none;" onclick="completeAppointment('${appt.id}')">
                            <i data-lucide="check-circle"></i> Complete
                        </button>
                        <button class="btn btn-danger" style="padding: 6px 12px; font-size: 0.8rem; box-shadow: none;" onclick="cancelAppointment('${appt.id}')">
                            <i data-lucide="x-circle"></i> Cancel
                        </button>
                    </div>
                `;
            } else {
                actionBtn = `<span style="color: var(--text-muted); font-size: 0.8rem;">Finished</span>`;
            }

            row.innerHTML = `
                <td style="font-weight: 600;">${patientMeta.name}</td>
                <td>${appt.appointment_date}</td>
                <td>${formatTime(appt.start_time)} - ${formatTime(appt.end_time)}</td>
                <td style="font-size: 0.85rem; max-width: 250px;">
                    <div style="color: var(--text-secondary); font-style: italic; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="Symptom notes: ${appt.notes || 'None'}"><strong>Symptoms:</strong> ${appt.notes || 'None'}</div>
                    <div style="color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="History: ${patientMeta.history || 'None'}"><strong>History:</strong> ${patientMeta.history || 'None'}</div>
                </td>
                <td><span class="badge badge-${statusClass}">${appt.status}</span></td>
                <td>${actionBtn}</td>
            `;
            list.appendChild(row);
        });
        lucide.createIcons();
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Complete appointment slot
async function completeAppointment(apptId) {
    try {
        const res = await fetch(`${API_URL}/appointments/${apptId}`, {
            method: "PUT",
            headers: getHeaders(),
            body: JSON.stringify({
                status: "Completed"
            })
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        showToast("Appointment marked as completed!");
        fetchDoctorSchedule();
    } catch (err) {
        showToast(err.message, "error");
    }
}


/* ==========================================================================
   C. ADMIN DASHBOARD LOGIC
   ========================================================================== */

// Get list of system user accounts
async function fetchAdminUsers() {
    try {
        const res = await fetch(`${API_URL}/users/`, {
            headers: getHeaders()
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        const list = document.getElementById("admin-users-list");
        list.innerHTML = "";

        data.forEach(usr => {
            const row = document.createElement("tr");
            
            // Format Created Date
            const createdDate = new Date(usr.created_at).toLocaleDateString();
            
            // Disable delete button for the current active admin to prevent lockouts
            const isSelf = usr.id === currentUser.id;
            const deleteBtn = isSelf 
                ? `<span style="color: var(--text-muted); font-size: 0.85rem;">(Active Admin)</span>`
                : `<button class="btn btn-danger" style="padding: 6px 12px; font-size: 0.8rem; box-shadow: none;" onclick="deleteUser('${usr.id}', '${usr.full_name}')"><i data-lucide="trash-2"></i> Delete</button>`;

            row.innerHTML = `
                <td style="font-size: 0.8rem; color: var(--text-secondary);">${usr.id}</td>
                <td style="font-weight: 600;">${usr.full_name}</td>
                <td>${usr.email}</td>
                <td><span class="user-role ${usr.role.toLowerCase()}">${usr.role}</span></td>
                <td><span style="color: ${usr.is_active ? 'var(--color-success)' : 'var(--color-error)'}; font-weight: 600;">${usr.is_active ? 'Active' : 'Inactive'}</span></td>
                <td>${createdDate}</td>
                <td>${deleteBtn}</td>
            `;
            list.appendChild(row);
        });
        lucide.createIcons();
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Delete user account (Admin only)
async function deleteUser(userId, name) {
    if (!confirm(`Are you sure you want to permanently delete the account for "${name}"? This action will cascade and remove all associated profiles and booked appointments.`)) return;

    try {
        const res = await fetch(`${API_URL}/users/${userId}`, {
            method: "DELETE",
            headers: getHeaders()
        });

        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || "Delete user failed");
        }

        showToast(`Account for ${name} has been deleted.`);
        fetchAdminUsers(); // Refresh accounts grid
    } catch (err) {
        showToast(err.message, "error");
    }
}

// Get global clinic appointments list (Admin only)
async function fetchAdminAppointments() {
    try {
        const res = await fetch(`${API_URL}/appointments/`, {
            headers: getHeaders()
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        const list = document.getElementById("admin-appointments-list");
        list.innerHTML = "";

        if (data.length === 0) {
            list.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-secondary);">No appointments are stored in the database.</td></tr>`;
            return;
        }

        data.forEach(appt => {
            const row = document.createElement("tr");
            const formatTime = (tStr) => tStr.split(":").slice(0, 2).join(":");
            let statusClass = appt.status.toLowerCase();
            
            row.innerHTML = `
                <td style="font-size: 0.8rem; color: var(--text-secondary);">${appt.patient_id}</td>
                <td style="font-size: 0.8rem; color: var(--text-secondary);">${appt.doctor_id}</td>
                <td>${appt.appointment_date}</td>
                <td>${formatTime(appt.start_time)} - ${formatTime(appt.end_time)}</td>
                <td><span class="badge badge-${statusClass}">${appt.status}</span></td>
                <td>
                    <button class="btn btn-danger" style="padding: 6px 12px; font-size: 0.8rem; box-shadow: none;" onclick="cancelAppointment('${appt.id}')">
                        <i data-lucide="trash"></i> Cancel
                    </button>
                </td>
            `;
            list.appendChild(row);
        });
        lucide.createIcons();
    } catch (err) {
        showToast(err.message, "error");
    }
}

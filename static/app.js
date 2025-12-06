// Calendar Aggregator Frontend
let currentView = 'monthly';
let currentDate = new Date();
let schedules = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadProviders();
    loadAuthStatus();
    setActiveView('monthly');
    loadSchedules();
});

// Load provider information
async function loadProviders() {
    try {
        const response = await fetch('/api/info');
        const data = await response.json();
        
        const providersContainer = document.getElementById('providers');
        providersContainer.innerHTML = '';
        
        if (data.providers && data.providers.length > 0) {
            data.providers.forEach(provider => {
                const badge = document.createElement('span');
                badge.className = `provider-badge ${provider}`;
                badge.textContent = provider.charAt(0).toUpperCase() + provider.slice(1);
                providersContainer.appendChild(badge);
            });
        } else {
            providersContainer.innerHTML = '<span class="provider-badge">No providers configured</span>';
        }
    } catch (error) {
        console.error('Error loading providers:', error);
    }
}

// Set active view
function setActiveView(view) {
    currentView = view;
    
    // Update button states
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-view="${view}"]`).classList.add('active');
    
    loadSchedules();
}

// Load schedules from API
async function loadSchedules() {
    const calendarContainer = document.getElementById('calendar');
    calendarContainer.innerHTML = '<div class="loading">Loading schedules...</div>';
    
    try {
        const response = await fetch(`/api/schedules?view=${currentView}`);
        const data = await response.json();
        
        // Load schedules even if there are errors (partial success)
        schedules = data.data || [];
        
        // Log any errors but still show the calendar
        if (data.errors && data.errors.length > 0) {
            console.warn('Some providers had errors:', data.errors);
        }
        
        renderCalendar();
    } catch (error) {
        // Even if API fails completely, show empty calendar
        console.error('Error loading schedules:', error);
        schedules = [];
        renderCalendar();
    }
}

// Render calendar based on current view
function renderCalendar() {
    const calendarContainer = document.getElementById('calendar');
    
    if (currentView === 'monthly') {
        renderMonthlyCalendar();
    } else if (currentView === 'weekly') {
        renderWeeklyCalendar();
    } else {
        renderDailyCalendar();
    }
}

// Render monthly calendar
function renderMonthlyCalendar() {
    const calendarContainer = document.getElementById('calendar');
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];
    
    let html = `
        <div class="calendar-header">
            <h2>${monthNames[month]} ${year}</h2>
            <button class="refresh-btn" onclick="loadSchedules()">Refresh</button>
        </div>
        <div class="calendar-grid">
            <div class="calendar-day-header">Sun</div>
            <div class="calendar-day-header">Mon</div>
            <div class="calendar-day-header">Tue</div>
            <div class="calendar-day-header">Wed</div>
            <div class="calendar-day-header">Thu</div>
            <div class="calendar-day-header">Fri</div>
            <div class="calendar-day-header">Sat</div>
    `;
    
    // Empty cells before first day
    for (let i = 0; i < startingDayOfWeek; i++) {
        html += '<div class="calendar-day"></div>';
    }
    
    // Days of the month
    const today = new Date();
    for (let day = 1; day <= daysInMonth; day++) {
        const date = new Date(year, month, day);
        const isToday = date.toDateString() === today.toDateString();
        const daySchedules = getSchedulesForDate(date);
        
        html += `<div class="calendar-day ${isToday ? 'today' : ''}">
            <div class="day-number">${day}</div>`;
        
        daySchedules.forEach(schedule => {
            const time = new Date(schedule.start_time).toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit'
            });
            html += `
                <div class="event ${schedule.provider}" onclick='showEventDetails(${JSON.stringify(schedule)})'>
                    <div class="event-title">${escapeHtml(schedule.title)}</div>
                    <div class="event-time">${time}</div>
                </div>
            `;
        });
        
        html += '</div>';
    }
    
    html += '</div>';
    
    if (schedules.length === 0) {
        html += '<div class="no-events">No events scheduled for this month</div>';
    }
    
    calendarContainer.innerHTML = html;
}

// Render weekly calendar
function renderWeeklyCalendar() {
    const calendarContainer = document.getElementById('calendar');
    const today = new Date();
    
    let html = `
        <div class="calendar-header">
            <h2>This Week</h2>
            <button class="refresh-btn" onclick="loadSchedules()">Refresh</button>
        </div>
        <div class="calendar-grid">
    `;
    
    for (let i = 0; i < 7; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
        const dayNum = date.getDate();
        const isToday = date.toDateString() === today.toDateString();
        const daySchedules = getSchedulesForDate(date);
        
        html += `<div class="calendar-day ${isToday ? 'today' : ''}">
            <div class="day-number">${dayName} ${dayNum}</div>`;
        
        daySchedules.forEach(schedule => {
            const time = new Date(schedule.start_time).toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit'
            });
            html += `
                <div class="event ${schedule.provider}" onclick='showEventDetails(${JSON.stringify(schedule)})'>
                    <div class="event-title">${escapeHtml(schedule.title)}</div>
                    <div class="event-time">${time}</div>
                </div>
            `;
        });
        
        html += '</div>';
    }
    
    html += '</div>';
    
    if (schedules.length === 0) {
        html += '<div class="no-events">No events scheduled for this week</div>';
    }
    
    calendarContainer.innerHTML = html;
}

// Render daily calendar
function renderDailyCalendar() {
    const calendarContainer = document.getElementById('calendar');
    const today = new Date();
    const daySchedules = getSchedulesForDate(today);
    
    const dateStr = today.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    let html = `
        <div class="calendar-header">
            <h2>${dateStr}</h2>
            <button class="refresh-btn" onclick="loadSchedules()">Refresh</button>
        </div>
    `;
    
    if (daySchedules.length === 0) {
        html += '<div class="no-events">No events scheduled for today</div>';
    } else {
        daySchedules.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
        
        daySchedules.forEach(schedule => {
            const startTime = new Date(schedule.start_time).toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit'
            });
            const endTime = new Date(schedule.end_time).toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit'
            });
            
            html += `
                <div class="event ${schedule.provider}" onclick='showEventDetails(${JSON.stringify(schedule)})' style="margin: 10px 0; padding: 15px;">
                    <div class="event-title" style="font-size: 1.2em;">${escapeHtml(schedule.title)}</div>
                    <div class="event-time">${startTime} - ${endTime}</div>
                    ${schedule.location ? `<div style="margin-top: 5px;">📍 ${escapeHtml(schedule.location)}</div>` : ''}
                </div>
            `;
        });
    }
    
    calendarContainer.innerHTML = html;
}

// Get schedules for a specific date
function getSchedulesForDate(date) {
    return schedules.filter(schedule => {
        const scheduleDate = new Date(schedule.start_time);
        return scheduleDate.toDateString() === date.toDateString();
    });
}

// Show event details in modal
function showEventDetails(schedule) {
    const modal = document.getElementById('eventModal');
    const startTime = new Date(schedule.start_time).toLocaleString();
    const endTime = new Date(schedule.end_time).toLocaleString();
    
    document.getElementById('modalTitle').textContent = schedule.title;
    document.getElementById('modalProvider').textContent = schedule.provider.charAt(0).toUpperCase() + schedule.provider.slice(1);
    document.getElementById('modalTime').textContent = `${startTime} - ${endTime}`;
    document.getElementById('modalDescription').textContent = schedule.description || 'No description';
    document.getElementById('modalLocation').textContent = schedule.location || 'No location';
    document.getElementById('modalAttendees').textContent = schedule.attendees.length > 0 ? schedule.attendees.join(', ') : 'No attendees';
    
    modal.classList.add('show');
}

// Close modal
function closeModal() {
    document.getElementById('eventModal').classList.remove('show');
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('eventModal');
    if (e.target === modal) {
        closeModal();
    }
});


// Toggle settings panel
function toggleSettings() {
    const panel = document.getElementById('settingsPanel');
    panel.classList.toggle('show');
    if (panel.classList.contains('show')) {
        loadCredentials();
        loadAuthStatus();
    }
}

// Load existing credentials
async function loadCredentials() {
    try {
        const response = await fetch('/api/credentials/get');
        const data = await response.json();
        
        // Populate Google fields
        if (data.google.client_id && !data.google.client_id.startsWith('your_')) {
            document.getElementById('googleClientId').value = data.google.client_id;
            if (data.google.client_secret_masked) {
                document.getElementById('googleClientSecret').placeholder = 'Already set: ' + data.google.client_secret_masked;
            }
        }
        
        // Populate Outlook fields
        if (data.outlook.client_id && !data.outlook.client_id.startsWith('your_')) {
            document.getElementById('outlookClientId').value = data.outlook.client_id;
            if (data.outlook.client_secret_masked) {
                document.getElementById('outlookClientSecret').placeholder = 'Already set: ' + data.outlook.client_secret_masked;
            }
        }
    } catch (error) {
        console.error('Error loading credentials:', error);
    }
}

// Save credentials
async function saveCredentials() {
    const googleClientId = document.getElementById('googleClientId').value.trim();
    const googleClientSecret = document.getElementById('googleClientSecret').value.trim();
    const outlookClientId = document.getElementById('outlookClientId').value.trim();
    const outlookClientSecret = document.getElementById('outlookClientSecret').value.trim();
    
    // Validate at least one provider has credentials
    if ((!googleClientId || !googleClientSecret) && (!outlookClientId || !outlookClientSecret)) {
        showCredentialMessage('Please enter credentials for at least one provider', 'error');
        return;
    }
    
    try {
        const response = await fetch('/api/credentials/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                google_client_id: googleClientId || 'your_google_client_id_here',
                google_client_secret: googleClientSecret || 'your_google_client_secret_here',
                outlook_client_id: outlookClientId || 'your_microsoft_client_id_here',
                outlook_client_secret: outlookClientSecret || 'your_microsoft_client_secret_here'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showCredentialMessage('✓ Credentials saved! You can now connect your calendars below.', 'success');
            // Reload auth status after saving
            setTimeout(() => {
                loadAuthStatus();
                loadProviders();
            }, 1000);
        } else {
            showCredentialMessage('Error: ' + data.error, 'error');
        }
    } catch (error) {
        console.error('Error saving credentials:', error);
        showCredentialMessage('Failed to save credentials. Please try again.', 'error');
    }
}

// Show credential message
function showCredentialMessage(message, type) {
    const messageDiv = document.getElementById('credentialMessage');
    messageDiv.textContent = message;
    messageDiv.className = 'credential-message show ' + type;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageDiv.classList.remove('show');
    }, 5000);
}

// Load authentication status
async function loadAuthStatus() {
    try {
        const response = await fetch('/api/auth/status');
        const status = await response.json();
        
        // Update Google status
        const googleStatus = document.getElementById('googleStatus');
        const googleBtn = document.getElementById('googleLoginBtn');
        
        if (!status.gmail.has_credentials) {
            googleStatus.textContent = 'No credentials - Add above ☝️';
            googleStatus.className = 'status-text not-connected';
            googleBtn.disabled = true;
            googleBtn.textContent = 'Add Credentials First';
            googleBtn.className = 'login-btn gmail';
        } else if (status.gmail.authenticated) {
            googleStatus.textContent = 'Connected ✓';
            googleStatus.className = 'status-text connected';
            googleBtn.className = 'login-btn gmail connected';
            googleBtn.textContent = '✓ Connected';
            googleBtn.disabled = false;
        } else {
            googleStatus.textContent = 'Ready to connect';
            googleStatus.className = 'status-text';
            googleBtn.disabled = false;
            googleBtn.className = 'login-btn gmail';
            googleBtn.textContent = 'Connect Google';
        }
        
        // Update Outlook status
        const outlookStatus = document.getElementById('outlookStatus');
        const outlookBtn = document.getElementById('outlookLoginBtn');
        
        if (!status.outlook.has_credentials) {
            outlookStatus.textContent = 'No credentials - Add above ☝️';
            outlookStatus.className = 'status-text not-connected';
            outlookBtn.disabled = true;
            outlookBtn.textContent = 'Add Credentials First';
            outlookBtn.className = 'login-btn outlook';
        } else if (status.outlook.authenticated) {
            outlookStatus.textContent = 'Connected ✓';
            outlookStatus.className = 'status-text connected';
            outlookBtn.className = 'login-btn outlook connected';
            outlookBtn.textContent = '✓ Connected';
            outlookBtn.disabled = false;
        } else {
            outlookStatus.textContent = 'Ready to connect';
            outlookStatus.className = 'status-text';
            outlookBtn.disabled = false;
            outlookBtn.className = 'login-btn outlook';
            outlookBtn.textContent = 'Connect Outlook';
        }
    } catch (error) {
        console.error('Error loading auth status:', error);
    }
}

// Login with Google
async function loginGoogle() {
    try {
        const response = await fetch('/api/auth/google/login');
        const data = await response.json();
        
        if (data.success) {
            // Open OAuth URL in popup
            const width = 600;
            const height = 700;
            const left = (screen.width - width) / 2;
            const top = (screen.height - height) / 2;
            
            window.open(
                data.auth_url,
                'Google OAuth',
                `width=${width},height=${height},left=${left},top=${top}`
            );
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error initiating Google login:', error);
        alert('Failed to initiate Google login. Please try again.');
    }
}

// Login with Outlook
async function loginOutlook() {
    try {
        const response = await fetch('/api/auth/outlook/login');
        const data = await response.json();
        
        if (data.success) {
            // Open OAuth URL in popup
            const width = 600;
            const height = 700;
            const left = (screen.width - width) / 2;
            const top = (screen.height - height) / 2;
            
            window.open(
                data.auth_url,
                'Outlook OAuth',
                `width=${width},height=${height},left=${left},top=${top}`
            );
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error initiating Outlook login:', error);
        alert('Failed to initiate Outlook login. Please try again.');
    }
}

// Listen for messages from OAuth popup
window.addEventListener('message', (event) => {
    if (event.data === 'oauth_success') {
        loadAuthStatus();
        loadProviders();
        loadSchedules();
    }
});

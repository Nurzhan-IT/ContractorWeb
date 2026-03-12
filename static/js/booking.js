// booking.js — FullCalendar booking calendar
// Pattern: calendar load → fetch slots → click event → modal → submit → success screen

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// TODO: initialise FullCalendar with eventSources: ['/api/booking/slots/?service=...']
// TODO: eventClick → open booking modal with pre-filled date/time
// TODO: modal form submit → POST /api/booking/submit/ → show success + gcal_url link

// emergency.js — Emergency 24/7 Request
// Pattern: form submit → spinner (2500ms) → SMS bubble + countdown timer

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// TODO: wire up form submit → POST /api/emergency/submit/
// TODO: setInterval countdown from 15:00

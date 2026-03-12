// quote.js — Multi-step Quote Wizard
// State object (populated as user progresses through wizard steps)
const quoteData = {};

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function updateProgress(step, total) {
  const pct = Math.round((step / total) * 100);
  const bar = document.getElementById('progress-bar');
  if (bar) bar.style.width = pct + '%';
}

// TODO: implement wizard step navigation, fetch call to /api/quote/calculate/, PDF download

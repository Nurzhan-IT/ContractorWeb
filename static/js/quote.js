// quote.js — AI Quote Calculator
// Extracted from templates/quote/index.html for browser caching.
// Relies on getCookie() defined globally in base.html.

let selectedFiles = [];
let lastEstimate  = null;
let lastFormData  = {};

// ── Character counter ─────────────────────────────────────────────────────────
const problemTextarea = document.getElementById('problem-desc');
const charCounter     = document.getElementById('char-counter');

problemTextarea.addEventListener('input', function () {
  const len = this.value.length;
  charCounter.textContent = len + ' character' + (len !== 1 ? 's' : '') + ' (20 minimum)';
  charCounter.className   = 'mt-1.5 text-xs ' + (len >= 20 ? 'text-green-600' : 'text-gray-400');
});

// ── Photo upload ──────────────────────────────────────────────────────────────
const dropZone     = document.getElementById('drop-zone');
const photoInput   = document.getElementById('photo-input');
const photoPreview = document.getElementById('photo-preview');

dropZone.addEventListener('click', () => photoInput.click());

dropZone.addEventListener('dragover', function (e) {
  e.preventDefault();
  this.classList.add('border-blue-500', 'bg-blue-50');
});
dropZone.addEventListener('dragleave', function () {
  this.classList.remove('border-blue-500', 'bg-blue-50');
});
dropZone.addEventListener('drop', function (e) {
  e.preventDefault();
  this.classList.remove('border-blue-500', 'bg-blue-50');
  addFiles(Array.from(e.dataTransfer.files));
});

photoInput.addEventListener('change', function () {
  addFiles(Array.from(this.files));
  this.value = '';
});

function addFiles(newFiles) {
  var allowed = ['image/jpeg', 'image/png', 'image/webp'];
  newFiles.forEach(function (file) {
    if (allowed.indexOf(file.type) === -1) return;
    if (file.size > 4 * 1024 * 1024) return;
    if (selectedFiles.length >= 5) return;
    selectedFiles.push(file);
  });
  renderPreviews();
}

function renderPreviews() {
  photoPreview.innerHTML = '';
  if (selectedFiles.length === 0) {
    photoPreview.classList.add('hidden');
    return;
  }
  photoPreview.classList.remove('hidden');
  selectedFiles.forEach(function (file, idx) {
    var url  = URL.createObjectURL(file);
    var wrap = document.createElement('div');
    wrap.className = 'relative aspect-square rounded-lg overflow-hidden bg-gray-100';
    wrap.innerHTML =
      '<img src="' + url + '" class="w-full h-full object-cover" alt="photo ' + (idx + 1) + '">' +
      '<button type="button" data-idx="' + idx + '" ' +
        'class="absolute top-0.5 right-0.5 w-5 h-5 rounded-full bg-red-600 text-white ' +
               'text-xs font-bold flex items-center justify-center hover:bg-red-700 ' +
               'transition-colors leading-none">\xd7</button>';
    (function (capturedUrl, capturedIdx) {
      wrap.querySelector('button').addEventListener('click', function () {
        URL.revokeObjectURL(capturedUrl);
        selectedFiles.splice(capturedIdx, 1);
        renderPreviews();
      });
    })(url, idx);
    photoPreview.appendChild(wrap);
  });
}

// ── Loading text rotation ─────────────────────────────────────────────────────
var MSGS_NO_PHOTO   = ['Analyzing your problem...', 'Calculating price...', 'Almost done...'];
var MSGS_WITH_PHOTO = ['Analyzing your problem...', 'Reading photos...', 'Calculating price...', 'Almost done...'];
var loadingTimer = null;

function startLoadingText(hasPhotos) {
  var msgs = hasPhotos ? MSGS_WITH_PHOTO : MSGS_NO_PHOTO;
  var el   = document.getElementById('loading-text');
  var i    = 0;
  el.textContent = msgs[0];
  loadingTimer = setInterval(function () {
    i = (i + 1) % msgs.length;
    el.textContent = msgs[i];
  }, 2000);
}

function stopLoadingText() {
  if (loadingTimer) { clearInterval(loadingTimer); loadingTimer = null; }
}

// ── Column swap helpers ───────────────────────────────────────────────────────
var formCol   = document.getElementById('form-col');
var resultCol = document.getElementById('result-col');

function showResultCol() {
  formCol.classList.add('hidden');
  resultCol.classList.remove('hidden');
  if (window.innerWidth < 1024) {
    resultCol.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function showFormCol() {
  resultCol.classList.add('hidden');
  formCol.classList.remove('hidden');
}

// ── Show panels ───────────────────────────────────────────────────────────────
function showPanel(name) {
  ['result-loading', 'result-success', 'result-error'].forEach(function (id) {
    document.getElementById(id).classList.toggle('hidden', id !== name);
  });
  showResultCol();
}

// ── Render estimate ───────────────────────────────────────────────────────────
function renderEstimate(estimate) {
  document.getElementById('result-service-type').textContent =
    estimate.service_type || 'Estimate';

  var min = estimate.min_price || 0;
  var max = estimate.max_price || 0;
  document.getElementById('result-price').textContent =
    '$' + min.toLocaleString() + ' \u2013 $' + max.toLocaleString();

  var container = document.getElementById('breakdown-rows');
  container.innerHTML = '';
  (estimate.breakdown || []).forEach(function (row, i) {
    var div = document.createElement('div');
    div.className = 'flex justify-between items-center px-4 py-2.5 text-sm ' +
                    (i % 2 === 0 ? 'bg-white' : 'bg-gray-50');
    div.innerHTML =
      '<span class="text-gray-600">' + (row.item || '') + '</span>' +
      '<span class="font-medium text-gray-800 text-right ml-2">' + (row.cost || '') + '</span>';
    container.appendChild(div);
  });

  var urgencyBlock = document.getElementById('urgency-block');
  var urgencyText  = estimate.urgency_note || '';
  if (urgencyText) {
    document.getElementById('urgency-text').textContent = urgencyText;
    urgencyBlock.classList.remove('hidden');
  } else {
    urgencyBlock.classList.add('hidden');
  }

  var assumBlock = document.getElementById('assumptions-block');
  var assumText  = estimate.assumptions || '';
  if (assumText) {
    document.getElementById('assumptions-text').textContent = assumText;
    assumBlock.classList.remove('hidden');
  } else {
    assumBlock.classList.add('hidden');
  }

  document.getElementById('disclaimer-text').textContent =
    estimate.disclaimer || 'Final price after on-site inspection.';
}

// ── Form submit ───────────────────────────────────────────────────────────────
document.getElementById('quote-form').addEventListener('submit', async function (e) {
  e.preventDefault();

  var btn       = document.getElementById('submit-btn');
  var icon      = document.getElementById('submit-icon');
  var text      = document.getElementById('submit-text');
  var spinner   = document.getElementById('submit-spinner');
  var formError = document.getElementById('form-error');

  formError.classList.add('hidden');

  var fd = new FormData();
  fd.append('problem_description', document.getElementById('problem-desc').value);
  fd.append('address',   document.getElementById('address').value);
  fd.append('zip_code',  document.getElementById('zip-code').value);
  fd.append('name',      document.getElementById('contact-name').value);
  fd.append('phone',     document.getElementById('contact-phone').value);
  fd.append('email',     document.getElementById('contact-email').value);
  selectedFiles.forEach(function (file) { fd.append('photos', file); });

  // Turnstile token (auto-inserted hidden input by CF widget)
  var cfInput = document.querySelector('[name="cf-turnstile-response"]');
  fd.append('cf-turnstile-response', cfInput ? cfInput.value : '');

  lastFormData = {
    name:    document.getElementById('contact-name').value.trim(),
    address: document.getElementById('address').value.trim() +
             (document.getElementById('zip-code').value.trim()
               ? ', ' + document.getElementById('zip-code').value.trim() : ''),
    problem_description: document.getElementById('problem-desc').value.trim(),
  };

  // --- Consent validation ---
  var consentCheckbox = document.getElementById('consent_required');
  if (consentCheckbox && !consentCheckbox.checked) {
    formError.textContent = 'You must agree to the Privacy Policy and AI processing consent to continue.';
    formError.classList.remove('hidden');
    consentCheckbox.focus();
    return;
  }

  // --- Client-side format validation ---
  var emailVal    = document.getElementById('contact-email').value.trim();
  var phoneVal    = document.getElementById('contact-phone').value.trim();
  var emailRe     = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var phoneDigits = phoneVal.replace(/\D/g, '');
  var valErrors   = [];
  if (!emailRe.test(emailVal)) valErrors.push('Enter a valid email address.');
  if (phoneDigits.length < 10 || phoneDigits.length > 15) valErrors.push('Enter a valid phone number (10+ digits).');
  if (valErrors.length) {
    formError.textContent = valErrors.join(' ');
    formError.classList.remove('hidden');
    return;
  }

  btn.disabled = true;
  icon.classList.add('hidden');
  spinner.classList.remove('hidden');
  text.textContent = 'Thinking...';
  showPanel('result-loading');
  startLoadingText(selectedFiles.length > 0);

  try {
    var res  = await fetch('/api/quote/submit/', {
      method:  'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      body:    fd,
    });
    var data = await res.json();
    stopLoadingText();

    if (!data.success) {
      if (data.errors) {
        showFormCol();
        formError.textContent = Object.values(data.errors).join(' ');
        formError.classList.remove('hidden');
      } else {
        document.getElementById('error-text').textContent =
          data.error || 'Something went wrong. Please try again.';
        showPanel('result-error');
      }
      return;
    }

    lastEstimate = data.estimate;
    renderEstimate(data.estimate);
    showPanel('result-success');

  } catch (err) {
    stopLoadingText();
    document.getElementById('error-text').textContent =
      'Network error. Please check your connection and try again.';
    showPanel('result-error');
  } finally {
    btn.disabled = false;
    icon.classList.remove('hidden');
    spinner.classList.add('hidden');
    text.textContent = 'Get AI Estimate \u2014 Free & Instant';
  }
});

// ── PDF download ──────────────────────────────────────────────────────────────
document.getElementById('btn-pdf').addEventListener('click', async function () {
  if (!lastEstimate) return;

  var btnText = document.getElementById('pdf-btn-text');
  this.disabled = true;
  btnText.textContent = 'Generating PDF...';

  try {
    var payload = Object.assign({ estimate: lastEstimate }, lastFormData);
    var res = await fetch('/api/quote/pdf/', {
      method:  'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken':  getCookie('csrftoken'),
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      btnText.textContent = 'Error — try again';
      setTimeout(function () { btnText.textContent = 'Download PDF Estimate'; }, 3000);
      return;
    }
    var blob = await res.blob();
    var url  = URL.createObjectURL(blob);
    var a    = document.createElement('a');
    a.href = url; a.download = 'contractorpro-estimate.pdf'; a.click();
    URL.revokeObjectURL(url);
  } catch {
    btnText.textContent = 'Error — try again';
    setTimeout(function () { btnText.textContent = 'Download PDF Estimate'; }, 3000);
  } finally {
    this.disabled = false;
  }
});

// ── Try Again ─────────────────────────────────────────────────────────────────
document.getElementById('btn-retry').addEventListener('click', function () {
  showFormCol();
  document.getElementById('quote-form').scrollIntoView({ behavior: 'smooth', block: 'start' });
});

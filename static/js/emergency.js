// emergency.js — Emergency 24/7 Request
// Flow: open modal → fill form → submit → spinner 2800ms (parallel fetch) → success screen

document.addEventListener('DOMContentLoaded', function () {

  var modal          = document.getElementById('emergency-modal');
  var formScreen     = document.getElementById('form-screen');
  var successScreen  = document.getElementById('success-screen');
  var form           = document.getElementById('emergency-form');
  var submitBtn      = document.getElementById('submit-btn');
  var phoneInput     = document.getElementById('phone-input');
  var phoneError     = document.getElementById('phone-error');

  var selectedType       = 'other';
  var contactPreference  = 'call';
  var countdownInterval  = null;

  // ── Problem type selector ──────────────────────────────────────────────────
  document.querySelectorAll('[data-problem-type]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('[data-problem-type]').forEach(function (b) {
        b.classList.remove('active');
      });
      btn.classList.add('active');
      selectedType = btn.dataset.problemType;
    });
  });

  // ── Contact preference selector ────────────────────────────────────────────
  document.querySelectorAll('[data-contact]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('[data-contact]').forEach(function (b) {
        b.classList.remove('active');
      });
      btn.classList.add('active');
      contactPreference = btn.dataset.contact;
    });
  });

  // ── Open / close modal ─────────────────────────────────────────────────────
  document.querySelectorAll('[data-open-modal]').forEach(function (btn) {
    btn.addEventListener('click', openModal);
  });

  document.getElementById('modal-close').addEventListener('click', closeModal);

  modal.addEventListener('click', function (e) {
    if (e.target === modal) closeModal();
  });

  // ESC key closes the modal
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !modal.classList.contains('hidden')) closeModal();
  });

  // Focus trap — keep keyboard navigation inside the open modal
  modal.addEventListener('keydown', function (e) {
    if (e.key !== 'Tab') return;
    var focusableEls = Array.from(modal.querySelectorAll(
      'button, input, textarea, select, a[href], [tabindex]:not([tabindex="-1"])'
    )).filter(function (el) { return !el.disabled; });
    if (focusableEls.length === 0) return;
    var firstEl = focusableEls[0];
    var lastEl  = focusableEls[focusableEls.length - 1];
    if (e.shiftKey) {
      if (document.activeElement === firstEl) { e.preventDefault(); lastEl.focus(); }
    } else {
      if (document.activeElement === lastEl) { e.preventDefault(); firstEl.focus(); }
    }
  });

  function openModal() {
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    // Focus first focusable element for accessibility
    setTimeout(function () {
      var firstFocusable = modal.querySelector('input, button, textarea');
      if (firstFocusable) firstFocusable.focus();
    }, 50);
  }

  function closeModal() {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
    // reset to form state
    formScreen.classList.remove('hidden');
    successScreen.classList.add('hidden');
    submitBtn.disabled = false;
    submitBtn.textContent = 'Send Emergency Request →';
    phoneError.classList.add('hidden');
    if (countdownInterval) {
      clearInterval(countdownInterval);
      countdownInterval = null;
    }
  }

  // ── Form submit ────────────────────────────────────────────────────────────
  form.addEventListener('submit', function (e) {
    e.preventDefault();

    var phoneVal = phoneInput.value.trim();
    var phoneDigits = phoneVal.replace(/\D/g, '');
    if (!phoneVal || phoneDigits.length < 10) {
      phoneError.textContent = phoneDigits.length > 0 && phoneDigits.length < 10
        ? 'Please enter a valid phone number (at least 10 digits)'
        : 'Phone number is required';
      phoneError.classList.remove('hidden');
      phoneInput.focus();
      return;
    }
    phoneError.classList.add('hidden');

    var name        = document.getElementById('name-input').value.trim();
    var phone       = phoneInput.value.trim();
    var description = document.getElementById('description-input').value.trim();

    // Show spinner
    submitBtn.disabled = true;
    submitBtn.innerHTML =
      '<svg class="animate-spin h-5 w-5 mr-2 inline" xmlns="http://www.w3.org/2000/svg" ' +
      'fill="none" viewBox="0 0 24 24">' +
      '<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>' +
      '<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>' +
      '</svg>Connecting to dispatch...';

    var apiResponse = null;

    // Start fetch and timer in parallel
    fetch('/api/emergency/submit/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({
        name: name,
        phone: phone,
        problem_description: description,
        problem_type: selectedType,
        contact_preference: contactPreference,
      }),
    })
      .then(function (r) { return r.json(); })
      .then(function (data) { apiResponse = data; })
      .catch(function () {});

    // Show success after 2800ms regardless
    setTimeout(function () {
      showSuccess(apiResponse);
    }, 2800);
  });

  // ── Success screen ─────────────────────────────────────────────────────────
  function showSuccess(data) {
    formScreen.classList.add('hidden');
    successScreen.classList.remove('hidden');

    if (!data) return;

    document.getElementById('sms-text').textContent      = data.sms_text    || '';
    document.getElementById('master-initials').textContent = getInitials(data.master_name || 'Pro');
    document.getElementById('eta-value').textContent      = data.eta_minutes || 18;

    var callBtn     = document.getElementById('call-btn');
    var callBtnText = document.getElementById('call-btn-text');
    callBtn.href        = 'tel:' + (data.master_phone || '');
    callBtnText.textContent =
      '\uD83D\uDCDE Call ' + (data.master_name || 'Master') + ': ' + (data.master_phone || '');

    startCountdown((data.eta_minutes || 18) * 60);
  }

  function getInitials(name) {
    return name.split(' ').map(function (n) { return n[0]; }).join('').toUpperCase().slice(0, 2);
  }

  // ── Countdown timer ────────────────────────────────────────────────────────
  function startCountdown(totalSeconds) {
    var display   = document.getElementById('countdown');
    var container = document.getElementById('countdown-container');
    var remaining = totalSeconds;

    if (countdownInterval) clearInterval(countdownInterval);

    function tick() {
      var mins = Math.floor(remaining / 60);
      var secs = remaining % 60;
      display.textContent =
        String(mins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');

      container.classList.remove('text-green-600', 'text-yellow-500', 'text-red-600');
      if (remaining > 5 * 60) {
        container.classList.add('text-green-600');
      } else if (remaining > 2 * 60) {
        container.classList.add('text-yellow-500');
      } else {
        container.classList.add('text-red-600');
      }

      if (remaining > 0) {
        remaining--;
      } else {
        clearInterval(countdownInterval);
      }
    }

    tick();
    countdownInterval = setInterval(tick, 1000);
  }

});

/* ============================================================
   web_quote.js — AI Website Cost Estimator (Landing Page)
   Self-contained — no framework dependencies
   ============================================================ */

(function () {
  'use strict';

  // ── CSRF helper ───────────────────────────────────────────────────────────
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // ── DOM refs ──────────────────────────────────────────────────────────────
  var formCol      = document.getElementById('wq-form-col');
  var resultCol    = document.getElementById('wq-result-col');
  var submitBtn    = document.getElementById('wq-submit-btn');
  var spinner      = document.getElementById('wq-spinner');
  var btnText      = document.getElementById('wq-btn-text');
  var btnIcon      = document.getElementById('wq-btn-icon');
  var formError    = document.getElementById('wq-form-error');
  var charCount    = document.getElementById('wq-char-count');

  // Fields
  var fldTrade    = document.getElementById('wq-trade');
  var fldDesc     = document.getElementById('wq-description');
  var fldBudget   = document.getElementById('wq-budget');
  var fldTimeline = document.getElementById('wq-timeline');
  var fldName     = document.getElementById('wq-name');
  var fldEmail    = document.getElementById('wq-email');
  var fldPhone    = document.getElementById('wq-phone');

  // Result panels
  var panelLoading = document.getElementById('wq-result-loading');
  var panelSuccess = document.getElementById('wq-result-success');
  var panelError   = document.getElementById('wq-result-error');
  var loadingText  = document.getElementById('wq-loading-text');

  // Result elements
  var elProjectType  = document.getElementById('wq-project-type');
  var elPriceRange   = document.getElementById('wq-price-range');
  var elTimelineBadge = document.getElementById('wq-timeline-text');
  var elFeaturesList = document.getElementById('wq-features-list');
  var elFeaturesBlock = document.getElementById('wq-features-block');
  var elBreakdownBody = document.getElementById('wq-breakdown-body');
  var elBreakdownBlock = document.getElementById('wq-breakdown-block');
  var elAssumptions  = document.getElementById('wq-assumptions-block');
  var elAssumptionsText = document.getElementById('wq-assumptions-text');
  var elDisclaimer   = document.getElementById('wq-disclaimer');
  var btnPdf         = document.getElementById('wq-pdf-btn');
  var btnRetry       = document.getElementById('wq-retry-btn');
  var btnRetryErr    = document.getElementById('wq-retry-btn-err');
  var elErrMsg       = document.getElementById('wq-error-msg');

  // Guard: exit if this page doesn't have the form
  if (!submitBtn) return;

  // ── State ─────────────────────────────────────────────────────────────────
  var lastEstimate = null;
  var lastFormData = {};
  var loadingInterval = null;

  var loadingMessages = [
    'Analyzing project scope\u2026',
    'Calculating development costs\u2026',
    'Preparing your estimate\u2026',
    'Reviewing feature requirements\u2026',
    'Almost ready\u2026',
  ];

  // ── Character counter ─────────────────────────────────────────────────────
  if (fldDesc && charCount) {
    fldDesc.addEventListener('input', function () {
      var len = fldDesc.value.length;
      charCount.textContent = len + ' / 20 min';
      charCount.style.color = len >= 20 ? '#15803d' : '#9ca3af';
    });
  }

  // ── Panel helpers ─────────────────────────────────────────────────────────
  function showPanel(name) {
    [panelLoading, panelSuccess, panelError].forEach(function (p) {
      if (p) p.classList.add('hidden');
    });
    var target = { loading: panelLoading, success: panelSuccess, error: panelError }[name];
    if (target) target.classList.remove('hidden');
  }

  function showResultCol() {
    if (formCol) formCol.classList.add('hidden');
    if (resultCol) {
      resultCol.classList.remove('hidden');
      setTimeout(function () {
        resultCol.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    }
  }

  function showFormCol() {
    if (resultCol) resultCol.classList.add('hidden');
    if (formCol) {
      formCol.classList.remove('hidden');
      formCol.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  // ── Loading animation ─────────────────────────────────────────────────────
  function startLoading() {
    var idx = 0;
    if (loadingText) loadingText.textContent = loadingMessages[0];
    loadingInterval = setInterval(function () {
      idx = (idx + 1) % loadingMessages.length;
      if (loadingText) loadingText.textContent = loadingMessages[idx];
    }, 2000);
  }

  function stopLoading() {
    clearInterval(loadingInterval);
    loadingInterval = null;
  }

  // ── Submit button state ───────────────────────────────────────────────────
  function setSubmitting(on) {
    if (!submitBtn) return;
    submitBtn.disabled = on;
    if (spinner) spinner.classList.toggle('hidden', !on);
    if (btnIcon) btnIcon.classList.toggle('hidden', on);
    if (btnText) btnText.textContent = on ? 'Analyzing with AI\u2026' : 'Get AI Estimate \u2014 Free & Instant';
  }

  // ── Validation ────────────────────────────────────────────────────────────
  function showFormError(msg) {
    if (!formError) return;
    formError.textContent = msg;
    formError.classList.remove('hidden');
    setTimeout(function () { formError.classList.add('hidden'); }, 6000);
  }

  function clearFieldError(el) {
    if (el) el.style.borderColor = '#d1d5db';
  }

  function setFieldError(el) {
    if (el) el.style.borderColor = '#ef4444';
  }

  function validate() {
    var ok = true;
    [fldTrade, fldDesc, fldName, fldEmail].forEach(clearFieldError);

    if (!fldTrade || !fldTrade.value) { setFieldError(fldTrade); ok = false; }
    if (!fldDesc || !fldDesc.value.trim()) { setFieldError(fldDesc); ok = false; }
    else if (fldDesc.value.trim().length < 20) { setFieldError(fldDesc); ok = false; }
    if (!fldName || !fldName.value.trim()) { setFieldError(fldName); ok = false; }
    if (!fldEmail || !fldEmail.value.trim()) { setFieldError(fldEmail); ok = false; }

    if (!ok) showFormError('Please fill in all required fields (description must be at least 20 characters).');
    return ok;
  }

  // ── Render estimate ───────────────────────────────────────────────────────
  function renderEstimate(est) {
    // Project type
    if (elProjectType) elProjectType.textContent = est.project_type || '';

    // Price range
    if (elPriceRange) {
      var minP = est.min_price || 0;
      var maxP = est.max_price || 0;
      elPriceRange.textContent = '$' + minP.toLocaleString() + ' \u2013 $' + maxP.toLocaleString();
    }

    // Timeline
    if (elTimelineBadge) elTimelineBadge.textContent = est.timeline || '';

    // Features
    var features = est.features_included || [];
    if (elFeaturesList && elFeaturesBlock) {
      if (features.length) {
        elFeaturesList.innerHTML = features.map(function (f) {
          return '<li class="flex items-start gap-2 text-xs text-gray-700">'
            + '<svg class="shrink-0 mt-0.5" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#15803d" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'
            + '<span>' + escHtml(f) + '</span></li>';
        }).join('');
        elFeaturesBlock.classList.remove('hidden');
      } else {
        elFeaturesBlock.classList.add('hidden');
      }
    }

    // Breakdown table
    var breakdown = est.breakdown || [];
    if (elBreakdownBody && elBreakdownBlock) {
      if (breakdown.length) {
        elBreakdownBody.innerHTML = breakdown.map(function (row, i) {
          var bg = i % 2 === 0 ? '#f8fafc' : '#ffffff';
          return '<tr style="background:' + bg + '">'
            + '<td class="px-3 py-2 text-xs text-gray-700">' + escHtml(row.item || '') + '</td>'
            + '<td class="px-3 py-2 text-xs text-gray-700 text-right font-medium">' + escHtml(row.cost || '') + '</td>'
            + '</tr>';
        }).join('');
        elBreakdownBlock.classList.remove('hidden');
      } else {
        elBreakdownBlock.classList.add('hidden');
      }
    }

    // Assumptions
    if (elAssumptions && elAssumptionsText) {
      var assumptions = est.assumptions || '';
      if (assumptions) {
        elAssumptionsText.textContent = assumptions;
        elAssumptions.classList.remove('hidden');
      } else {
        elAssumptions.classList.add('hidden');
      }
    }

    // Disclaimer
    if (elDisclaimer) elDisclaimer.textContent = est.disclaimer || '';
  }

  // Simple HTML escape
  function escHtml(str) {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ── PDF download ──────────────────────────────────────────────────────────
  function downloadPdf() {
    if (!lastEstimate) return;

    var payload = {
      estimate: lastEstimate,
      name: lastFormData.name || '',
      trade: lastFormData.trade || '',
      project_description: lastFormData.project_description || '',
    };

    if (btnPdf) {
      btnPdf.textContent = 'Generating PDF\u2026';
      btnPdf.disabled = true;
    }

    fetch('/api/web-quote/pdf/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'same-origin',
      body: JSON.stringify(payload),
    })
      .then(function (res) {
        if (!res.ok) throw new Error('PDF generation failed');
        return res.blob();
      })
      .then(function (blob) {
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = 'web_estimate.pdf';
        document.body.appendChild(a);
        a.click();
        setTimeout(function () {
          URL.revokeObjectURL(url);
          document.body.removeChild(a);
        }, 100);
      })
      .catch(function () {
        alert('Could not generate PDF. Please try again.');
      })
      .finally(function () {
        if (btnPdf) {
          btnPdf.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg> Download PDF Estimate';
          btnPdf.disabled = false;
        }
      });
  }

  // ── Form submit ───────────────────────────────────────────────────────────
  if (submitBtn) {
    submitBtn.addEventListener('click', function () {
      if (!validate()) return;

      var fd = new FormData();
      fd.append('name', fldName ? fldName.value.trim() : '');
      fd.append('email', fldEmail ? fldEmail.value.trim() : '');
      fd.append('phone', fldPhone ? fldPhone.value.trim() : '');
      fd.append('trade', fldTrade ? fldTrade.value : '');
      fd.append('budget_range', fldBudget ? fldBudget.value : '');
      fd.append('timeline_pref', fldTimeline ? fldTimeline.value : '');
      fd.append('project_description', fldDesc ? fldDesc.value.trim() : '');

      lastFormData = {
        name: fldName ? fldName.value.trim() : '',
        trade: fldTrade ? fldTrade.value : '',
        project_description: fldDesc ? fldDesc.value.trim() : '',
      };

      setSubmitting(true);
      showResultCol();
      showPanel('loading');
      startLoading();

      fetch('/api/web-quote/submit/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        credentials: 'same-origin',
        body: fd,
      })
        .then(function (res) { return res.json(); })
        .then(function (data) {
          stopLoading();
          if (data.success && data.estimate) {
            lastEstimate = data.estimate;
            renderEstimate(data.estimate);
            showPanel('success');
          } else {
            var msg = (data.error) || (data.errors ? Object.values(data.errors).join(' ') : 'Something went wrong.');
            if (elErrMsg) elErrMsg.textContent = msg;
            showPanel('error');
          }
        })
        .catch(function () {
          stopLoading();
          if (elErrMsg) elErrMsg.textContent = 'Could not reach the server. Please check your connection and try again.';
          showPanel('error');
        })
        .finally(function () {
          setSubmitting(false);
        });
    });
  }

  // ── Retry buttons ─────────────────────────────────────────────────────────
  if (btnRetry) btnRetry.addEventListener('click', showFormCol);
  if (btnRetryErr) btnRetryErr.addEventListener('click', showFormCol);

  // ── PDF button ────────────────────────────────────────────────────────────
  if (btnPdf) btnPdf.addEventListener('click', downloadPdf);

})();

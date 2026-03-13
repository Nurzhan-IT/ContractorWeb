/* ============================================================
   main.js — ContractorWeb Django Template
   Vanilla JS only — no frameworks
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ─────────────────────────────────────────
  // 1. HEADER SHADOW ON SCROLL
  // ─────────────────────────────────────────
  var header = document.getElementById('site-header');
  if (header) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 10) {
        header.classList.add('shadow-md', 'scrolled');
      } else {
        header.classList.remove('shadow-md', 'scrolled');
      }
    });
  }

  // ─────────────────────────────────────────
  // 2. MOBILE MENU
  // ─────────────────────────────────────────
  var menuBtn = document.getElementById('mobile-menu-btn');
  var menuClose = document.getElementById('mobile-menu-close');
  var mobileMenu = document.getElementById('mobile-menu');

  function openMenu() {
    if (mobileMenu) {
      mobileMenu.style.display = 'block';
      document.body.style.overflow = 'hidden';
    }
  }

  function closeMenu() {
    if (mobileMenu) {
      mobileMenu.style.display = 'none';
      document.body.style.overflow = '';
    }
  }

  if (menuBtn) menuBtn.addEventListener('click', openMenu);
  if (menuClose) menuClose.addEventListener('click', closeMenu);

  // Close when clicking a nav link
  if (mobileMenu) {
    mobileMenu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', closeMenu);
    });
  }

  // ─────────────────────────────────────────
  // 3. SCROLL ANIMATIONS (IntersectionObserver)
  // ─────────────────────────────────────────
  var animatedSections = document.querySelectorAll('.animate-section');
  if (animatedSections.length && 'IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });

    animatedSections.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    // Fallback for browsers without IntersectionObserver
    animatedSections.forEach(function (el) {
      el.classList.add('visible');
    });
  }

  // ─────────────────────────────────────────
  // 4. FAQ ACCORDION
  // ─────────────────────────────────────────
  var faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(function (item) {
    var trigger = item.querySelector('.faq-trigger');
    if (!trigger) return;
    trigger.addEventListener('click', function () {
      var isOpen = item.classList.contains('open');
      // Close all
      faqItems.forEach(function (i) { i.classList.remove('open'); });
      // Open this one if it was closed
      if (!isOpen) {
        item.classList.add('open');
      }
    });
  });

  // ─────────────────────────────────────────
  // 5. CONTACT FORM — validation + CSRF fetch
  // ─────────────────────────────────────────
  var contactForm = document.getElementById('contact-form');
  var formSuccess = document.getElementById('form-success');
  var formError = document.getElementById('form-error');

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

  function showMessage(el, duration) {
    if (!el) return;
    el.classList.remove('hidden');
    setTimeout(function () { el.classList.add('hidden'); }, duration || 5000);
  }

  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();

      // Basic validation
      var required = contactForm.querySelectorAll('[required]');
      var valid = true;
      required.forEach(function (field) {
        field.style.borderColor = '';
        if (!field.value.trim()) {
          valid = false;
          field.style.borderColor = '#ef4444';
        }
      });

      if (!valid) {
        if (formError) {
          formError.textContent = 'Please fill in all required fields.';
          showMessage(formError, 4000);
        }
        return;
      }

      var submitBtn = contactForm.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending…';
      }

      var formData = new FormData(contactForm);
      var csrfToken = getCookie('csrftoken');

      fetch(contactForm.action, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
        body: formData,
        credentials: 'same-origin'
      })
        .then(function (response) {
          if (response.ok) {
            contactForm.reset();
            if (formSuccess) {
              formSuccess.textContent = 'Your message has been sent successfully!';
              showMessage(formSuccess, 5000);
            }
          } else {
            throw new Error('Server error');
          }
        })
        .catch(function () {
          if (formError) {
            formError.textContent = 'Something went wrong. Please try again.';
            showMessage(formError, 5000);
          }
        })
        .finally(function () {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Send Message <svg style="display:inline;vertical-align:middle;margin-left:8px" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>';
          }
        });
    });
  }

  // ─────────────────────────────────────────
  // 6. FILE UPLOAD LABEL UPDATE
  // ─────────────────────────────────────────
  var fileInput = document.getElementById('file-upload');
  var fileLabel = document.getElementById('file-label-text');
  if (fileInput && fileLabel) {
    fileInput.addEventListener('change', function () {
      if (fileInput.files && fileInput.files[0]) {
        fileLabel.textContent = fileInput.files[0].name;
      } else {
        fileLabel.textContent = 'Upload logo, brand guidelines, or inspiration';
      }
    });
  }

});

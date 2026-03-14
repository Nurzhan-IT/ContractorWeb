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

});
// Web quote form logic lives in web_quote.js

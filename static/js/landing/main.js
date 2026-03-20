/* ============================================================
   main.js — ContractorWebDev Django Template
   Vanilla JS only — no frameworks
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

  // ─────────────────────────────────────────
  // 1. SCROLL ANIMATIONS (IntersectionObserver)
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
  // 2. NAVBAR SCROLL + MOBILE MENU
  // ─────────────────────────────────────────
  var mainNav    = document.getElementById('main-nav');
  var navBurger  = document.getElementById('nav-burger');
  var mobileMenu = document.getElementById('mobile-menu');
  var menuOpen   = false;

  function updateNavScroll() {
    if (mainNav) mainNav.classList.toggle('nav-scrolled', window.scrollY > 60);
  }
  window.addEventListener('scroll', updateNavScroll, { passive: true });
  updateNavScroll();

  if (navBurger) {
    navBurger.addEventListener('click', function () {
      menuOpen = !menuOpen;
      mainNav.classList.toggle('menu-open', menuOpen);
      mobileMenu.style.maxHeight = menuOpen ? mobileMenu.scrollHeight + 'px' : '0';
    });
  }

  document.querySelectorAll('.nav-mobile-link').forEach(function (link) {
    link.addEventListener('click', function () {
      menuOpen = false;
      if (mainNav) mainNav.classList.remove('menu-open');
      if (mobileMenu) mobileMenu.style.maxHeight = '0';
    });
  });

  document.addEventListener('click', function (e) {
    if (menuOpen && mainNav && !mainNav.contains(e.target)) {
      menuOpen = false;
      mainNav.classList.remove('menu-open');
      mobileMenu.style.maxHeight = '0';
    }
  });

  // ─────────────────────────────────────────
  // 3. FAQ ACCORDION
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

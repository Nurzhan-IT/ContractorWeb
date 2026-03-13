# CRO Fix Prompt — ContractorWeb Demo Site

You are implementing a full CRO (Conversion Rate Optimization) fix pass on a Django + Jinja2 contractor demo site. A detailed audit has already been completed and saved in `CRO_analyse_results.md`. Read that file first to understand the full context, then implement every fix below in order of priority.

The site is at: c:\CODES\ContractorWebDev\website_django\
Key templates: templates/landing/index.html, templates/base.html, templates/demo_hub.html, templates/booking/index.html

Before touching any file, read it fully. Make all changes using the Edit tool, not Write. Do not rewrite files from scratch. Do not modify anything beyond what is explicitly listed below.

---

## BATCH 1 — CRITICAL FIXES (do these first, in order)

### FIX 1 — Unify brand name across landing and demo pages
- In `templates/base.html`: change the nav logo text from `ContractorPro <span class="text-blue-400">DEMO</span>` to `ContractorWeb <span class="text-blue-400">DEMO</span>`
- Also update the footer copyright line from "ContractorPro" to "ContractorWeb"

### FIX 2 — Fix grammar error in Pro pricing tier
- In `templates/landing/index.html`, find `1 months support` inside the Pro pricing card and change it to `1 month support`

### FIX 3 — Fix all dead "Try it →" feature buttons in the Features section
- In `templates/landing/index.html`, find the Features section (id="features"). There are 6 feature cards, each with a `<button>` tag containing "Try it →" or similar. Convert each `<button>` to an `<a>` tag pointing to:
  - Feature 01 "Instant Quote Calculator" → href="/demo/quote/"
  - Feature 02 "Photo Upload Form" → href="/demo/quote/"
  - Feature 03 "Google Calendar Booking" → href="/demo/booking/"
  - Feature 04 "Personal Lead Dashboard" → href="/demo/"
  - Feature 05 "Auto City Pages for SEO" → href="/demo/service-area/"
  - Feature 06 "Emergency Request Button" → href="/demo/emergency/"
- Keep the same CSS classes, just change `<button>` to `<a href="...">` and remove `type` attribute if present.

### FIX 4 — Fix dead "View Site" portfolio buttons
- In `templates/landing/index.html`, find the Portfolio section (id="portfolio"). There are 4 portfolio cards, each containing a `<button>` with "View Site" and an external link SVG icon.
- Remove the `<button class="... View Site ...">` element from each portfolio card entirely.
- In its place, add a testimonial quote block. Use this exact HTML structure inside each card's overlay div (replace the button):
  ```html
  <p class="px-6 text-center text-white text-sm italic font-medium drop-shadow-lg">
    "Our leads tripled in the first 3 months."
  </p>
  ```
- Do this for all 4 portfolio cards (same quote is fine — or vary per card if you prefer).

### FIX 5 — Add a phone number to the desktop nav and contact section
- In `templates/landing/index.html`, find the desktop navigation `<div class="hidden md:flex items-center gap-8">`. Before the "Get Quote" button, add:
  ```html
  <a href="tel:+15551234567" class="text-sm font-medium text-gray-700 hover:text-cyan-600 transition-colors flex items-center gap-1">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 13.5a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.61 3h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 10.6a16 16 0 0 0 6 6l.96-.96a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 17v-.08z"/></svg>
    (555) 123-4567
  </a>
  ```
- In the mobile menu `<div id="mobile-menu" ...>`, add the same phone link as a block item after the Live Demo link.
- In the Contact section (id="contact"), find the `<h2>Ready to Grow Your Business?</h2>` heading block and add this paragraph directly below the subtitle:
  ```html
  <p class="text-base text-gray-500 mt-2">
    Prefer to talk? Call us: <a href="tel:+15551234567" class="font-semibold text-cyan-600 hover:underline">(555) 123-4567</a>
    <span class="text-gray-400 text-sm"> — Mon–Fri 8am–6pm EST</span>
  </p>
  ```

### FIX 6 — Add satisfaction guarantee badge to the pricing section
- In `templates/landing/index.html`, find the pricing section. After the `<div class="mt-12 text-center animate-section">` that contains "All plans include source code ownership…", add a new div:
  ```html
  <div class="mt-8 flex justify-center animate-section">
    <div class="inline-flex items-center gap-3 px-6 py-4 rounded-2xl bg-green-50 border border-green-200">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
      <div class="text-left">
        <p class="text-sm font-bold text-green-800">100% Satisfaction Guarantee</p>
        <p class="text-xs text-green-700 mt-0.5">Not happy with the initial design? We revise until you love it — or refund your deposit. No questions asked.</p>
      </div>
    </div>
  </div>
  ```

### FIX 7 — Rewrite the contact form submit button copy
- In `templates/landing/index.html`, find the contact form submit button. Change its text from `"Send Message"` to `"Get My Custom Quote — Free"`.
- Find the SVG arrow icon inside the button and keep it.
- Below the `<button type="submit">` closing tag (before the success/error divs), add:
  ```html
  <p class="text-center text-xs text-gray-500 mt-3">🔒 Your information is private and never shared. We respond within 4 business hours.</p>
  ```

### FIX 8 — Rewrite "Django Backend Power" card to contractor language
- In `templates/landing/index.html`, find the "Why Choose Us" section. Find Card 2 with `<h3>Django Backend Power</h3>`.
- Change `<h3>Django Backend Power</h3>` to `<h3>Built for Heavy Traffic</h3>`
- Change the paragraph from "Built on the same technology used by Instagram and NASA. Fast, secure, and scalable with enterprise-grade reliability." to: "Whether it's a slow Tuesday or a storm that sends 500 homeowners to your site at once — your website stays fast. No crashes, no slow pages, no lost leads."
- Keep the badge "99.9% Uptime" unchanged.

---

## BATCH 2 — IMPORTANT FIXES

### FIX 9 — Add a sticky mobile CTA bar
- In `templates/landing/index.html`, find the closing `</body>` tag (or just before the `<script src="static(...)">` landing scripts block at the end of the file). Add this before the `</body>` tag:
  ```html
  <!-- Sticky mobile CTA -->
  <div id="sticky-mobile-cta" class="fixed bottom-0 left-0 right-0 z-50 md:hidden bg-white border-t border-gray-200 shadow-lg p-3">
    <a href="#contact" class="block w-full text-center bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-3 rounded-xl font-semibold text-sm">
      Get Your Free Quote →
    </a>
  </div>
  <script>
    // Hide sticky CTA once the contact form is visible
    (function() {
      var cta = document.getElementById('sticky-mobile-cta');
      var form = document.getElementById('contact-form');
      if (!cta || !form) return;
      var obs = new IntersectionObserver(function(entries) {
        cta.style.display = entries[0].isIntersecting ? 'none' : '';
      }, { threshold: 0.1 });
      obs.observe(form);
    })();
  </script>
  ```

### FIX 10 — Fix the "Your Custom Feature" card on the demo hub
- In `templates/demo_hub.html`, find the 6th card which is a `<div class="flex flex-col bg-white rounded-2xl border-2 border-dashed ...">`.
- Change the outer element from `<div>` to `<a href="/demo/booking/">` and close with `</a>`.
- Change the inner CTA span text from `"Let's Talk →"` to `"Tell us your idea →"`.
- Add `cursor-pointer` to the outer element's class list.

### FIX 11 — Add urgency signal near pricing
- In `templates/landing/index.html`, find the pricing section heading block (the `<div class="text-center mb-16 animate-section">` containing "Transparent Pricing"). After the `<p class="text-xl ...">One-time payment...</p>` line, add:
  ```html
  <p class="mt-4 text-sm font-medium text-amber-700 inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-amber-50 border border-amber-200">
    <span class="inline-block w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
    Currently accepting new clients — spots fill fast during contractor season
  </p>
  ```

### FIX 12 — Add "What happens next?" steps above the contact form
- In `templates/landing/index.html`, inside the contact section, find the `<div class="animate-section relative">` that wraps the `<form id="contact-form">`. Immediately BEFORE that div, add:
  ```html
  <div class="grid grid-cols-3 gap-4 mb-8 animate-section">
    <div class="text-center p-4 rounded-xl bg-gray-50 border border-gray-200">
      <div class="text-2xl mb-2">📝</div>
      <p class="text-xs font-bold text-gray-800">Step 1</p>
      <p class="text-xs text-gray-500 mt-1">Fill the form<br>(2 minutes)</p>
    </div>
    <div class="text-center p-4 rounded-xl bg-gray-50 border border-gray-200">
      <div class="text-2xl mb-2">⚡</div>
      <p class="text-xs font-bold text-gray-800">Step 2</p>
      <p class="text-xs text-gray-500 mt-1">We send a custom<br>proposal in 24h</p>
    </div>
    <div class="text-center p-4 rounded-xl bg-gray-50 border border-gray-200">
      <div class="text-2xl mb-2">🚀</div>
      <p class="text-xs font-bold text-gray-800">Step 3</p>
      <p class="text-xs text-gray-500 mt-1">Your site goes live<br>in 48h–3 weeks</p>
    </div>
  </div>
  ```

### FIX 13 — Add business outcome sub-labels to demo hub feature cards
- In `templates/demo_hub.html`, for each of the 5 active feature cards, add a small stat line between the description `<p>` and the `<div class="mt-3 sm:mt-5">` CTA div. One line per card:
  - Quote Calculator card: `<p class="text-xs text-blue-500 font-medium mt-1 hidden sm:block">Clients report 2–3x more qualified leads</p>`
  - Emergency card: `<p class="text-xs text-red-500 font-medium mt-1 hidden sm:block">Capture high-value urgent jobs 24/7</p>`
  - Service Area card: `<p class="text-xs text-green-600 font-medium mt-1 hidden sm:block">Reduce wasted quotes by showing your zone upfront</p>`
  - Portfolio card: `<p class="text-xs text-purple-500 font-medium mt-1 hidden sm:block">Customers who see before/after photos book 60% faster</p>`
  - Booking card: `<p class="text-xs text-amber-600 font-medium mt-1 hidden sm:block">30% of bookings happen after 9pm — capture them automatically</p>`

### FIX 14 — Move FullCalendar out of base.html global load
- In `templates/base.html`, find the FullCalendar CSS link:
  `<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.css" />`
  Remove it from `base.html`.
- In `templates/base.html`, find the FullCalendar JS script:
  `<script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js"></script>`
  Remove it from `base.html`.
- In `templates/booking/index.html`, add both FullCalendar tags inside the `{% block extra_head %}` block (the CSS link) and `{% block extra_js %}` block (the JS script), BEFORE the existing Cal.com embed script.

### FIX 15 — Add privacy note and "What to expect" copy near contact form
- In `templates/landing/index.html`, find `<p class="text-sm text-gray-600">We typically respond within 4 business hours &bull; Your information is never shared</p>` at the bottom of the contact section.
- Replace it with:
  ```html
  <p class="text-sm text-gray-600">
    ✅ We typically respond within 4 business hours &nbsp;&bull;&nbsp;
    🔒 Your information is never shared &nbsp;&bull;&nbsp;
    📋 <a href="#faq" class="underline hover:text-cyan-600">See FAQ</a> for common questions
  </p>
  ```

---

## BATCH 3 — DEMO PAGES CONTEXT FIX

### FIX 16 — Add a context banner to the booking page
- In `templates/booking/index.html`, find the page header section `<section class="bg-gradient-to-br from-blue-700 ...">`. Inside that section, after the Cal.com pill badge `</span>`, add:
  ```html
  <p class="mt-4 text-blue-200 text-xs max-w-md">
    💡 <strong>Demo context:</strong> This shows how your customers would book appointments on your website. Switch service types above to see how multiple services work.
  </p>
  ```

---

## VALIDATION CHECKLIST

After completing all fixes, verify:
- [ ] Nav logo reads "ContractorWeb DEMO" on demo pages
- [ ] All 6 feature "Try it →" elements are `<a>` tags with correct hrefs
- [ ] All 4 portfolio "View Site" buttons are removed
- [ ] "1 months support" is gone — reads "1 month support"
- [ ] Phone number (555) 123-4567 appears in desktop nav and contact section
- [ ] Green satisfaction guarantee badge appears below pricing tiers
- [ ] Contact form button reads "Get My Custom Quote — Free"
- [ ] "Django Backend Power" card reads "Built for Heavy Traffic"
- [ ] Sticky mobile CTA bar is present and hides when contact form is visible
- [ ] "Your Custom Feature" card on demo hub is a clickable `<a>` to /demo/booking/
- [ ] FullCalendar CSS/JS is no longer in base.html
- [ ] Demo hub feature cards show outcome stat lines

Do NOT change:
- The landing app logic or any Python views
- Any URL routing
- The existing Tailwind CDN tag (leave as-is)
- The Cal.com embed code in booking/index.html
- The `CLAUDE.md` file
- Any JS in static/js/ files

# CRO Audit Report — ContractorWeb Demo Site
**Auditor:** Claude Sonnet 4.6 (CRO / UX / Behavioral Economics Analysis)
**Date:** 2026-03-14
**Site scope:** `/` (landing) · `/demo/` (hub) · `/demo/quote/` · `/demo/emergency/` · `/demo/service-area/` · `/demo/portfolio/` · `/demo/booking/`
**Primary audience:** Local contractors (plumbers, electricians, roofers) considering a custom website

---

## PHASE 1 — TECHNICAL RECONNAISSANCE

### Site Map & User Journey

```
/ (landing)
 ├── #features   → demo feature cards (Try it →) ← DEAD BUTTONS (not linked)
 ├── #portfolio  → 4 case studies (View Site ←) ← DEAD BUTTONS (not linked)
 ├── #pricing    → 3 tiers ($999 / $2,999 / $9,999) → #contact
 ├── #contact    → lead form → "Send Message"
 ├── #faq        → 8 questions → #contact
 └── /demo/      → Demo Hub

/demo/ (hub)
 ├── /demo/quote/         → AI Quote Calculator
 ├── /demo/emergency/     → Emergency 24/7 Request
 ├── /demo/service-area/  → Service Area Map
 ├── /demo/portfolio/     → Before/After Gallery
 ├── /demo/booking/       → Online Booking (Cal.com)
 └── "Your Custom Feature" → no link (grey placeholder)
```

### Primary Conversion Goal
**Lead capture via contact form** → contractor submits Name, Email, Phone, Trade, Project Description → agency replies within 4 business hours.

### Secondary Micro-Conversions
- Click "Explore the Demo" → visit `/demo/`
- Interact with any demo feature (quote, emergency, booking)
- FAQ accordion engagement
- "Book a Call" on demo hub → booking page

### Technical Observations
- All JS via CDN (Tailwind, Leaflet, FullCalendar, Cal.com) — no build step, fast deployment
- FullCalendar loaded globally in `base.html` but not used on any current page (dead weight)
- Tailwind loaded via CDN (play CDN) — not production-grade, slower than compiled CSS
- External images from Unsplash with long query strings — no caching control
- Rate limit (5 req/hr) on quote API is good for abuse prevention
- **Brand name inconsistency**: Landing page = "ContractorWeb", all demo pages = "ContractorPro DEMO"

---

## PHASE 2 — CONVERSION FUNNEL ANALYSIS

### Primary Funnel Steps (Landing → Lead)

| Step | Page/Action | Friction Level |
|---|---|---|
| 1 | Visitor lands on `/` | — |
| 2 | Reads hero headline | Low |
| 3 | Scrolls past Why Choose Us | Medium — "Django Backend Power" alienates non-tech audience |
| 4 | Reaches Features section | Medium — "Try it →" buttons are non-functional |
| 5 | Sees portfolio case studies | Medium — "View Site" buttons are dead links |
| 6 | Reaches pricing section | Low — pricing is clear |
| 7 | Reads FAQ | Low |
| 8 | Reaches contact form | Low — but form CTA is generic |
| 9 | Submits form | High — no guarantee, no risk reversal nearby |

### CTA Audit

| CTA | Location | Copy | Type | Issue |
|---|---|---|---|---|
| "Get Your Custom Quote" | Hero | Good — outcome-focused | Anchor to #contact | Scrolls to bottom, long journey |
| "View Our Work" | Hero | Neutral | Anchor to #portfolio | Secondary CTA competes |
| "Try it →" | Features grid (6x) | Weak | **Non-functional buttons** | Kills demo flow |
| "View Site" | Portfolio (4x) | Neutral | **Non-functional buttons** | Destroys credibility |
| "Get Started" / "Start Growing" / "Scale Your Business" | Pricing | Good | Anchor to #contact | Consistent |
| "Send Message" | Contact form | **Weak — generic** | Form submit | No outcome, no urgency |
| "Book a Call" | Demo Hub CTA | Good | Link to /demo/booking/ | Buried below fold |

### Form Field Count (Contact Form)
- Required: Name, Email, Trade (select), Project Description = **4 required fields + 1 textarea**
- Optional: Phone, File Upload
- Assessment: Appropriate for a high-ticket service ($999–$9,999). Not excessive.

---

## PHASE 3 — PSYCHOLOGICAL BARRIER AUDIT

### Trust & Credibility Barriers

**T1 — Brand name inconsistency kills trust**
- **Principle:** Brand coherence / first impressions (primacy effect)
- Landing says "ContractorWeb" (logo, nav, footer). Demo pages say "ContractorPro DEMO". A contractor who clicks "Live Demo" from the landing page suddenly sees a different brand name in the navbar. This creates cognitive dissonance: *"Did I go to a different site? Is this the same company?"*
- The "DEMO" suffix in the nav further undermines the agency's professionalism.

**T2 — Dead portfolio "View Site" buttons actively destroy credibility**
- **Principle:** Trust violation / commitment-consistency (Cialdini)
- 4 portfolio case studies labeled "Live" with green badges each have a "View Site" button. Every single one does nothing. A prospect who clicks "View Site" on a case study marked "Live" and gets zero response will immediately question whether the "150+ Contractors Served" claim is fabricated. This is the single highest-trust-destroying element on the page.

**T3 — No named, photographed testimonials**
- **Principle:** Social proof (Cialdini) — specific, named, attributed proof > anonymous stats
- The 4 case studies have impressive metrics (+215% leads, $125k revenue) but zero quotes from actual people. No contractor's name, no photo, no company logo. This makes results feel invented rather than real.

**T4 — Unverifiable stats in hero**
- **Principle:** Vague social proof is noise
- "150+ Contractors Served", "3x Average Lead Increase", "48h Launch Time" — no source, no methodology. For a $2,999–$9,999 purchase, contractors will be skeptical. Compare to: *"Mike Martinez, Martinez Plumbing: 'We went from 3 leads/week to 11 in 90 days.'"*

**T5 — No guarantee or risk reversal**
- **Principle:** Loss aversion (Kahneman) — people fear losing more than they value gaining
- The pricing page shows one-time payments from $999 to $9,999. There is zero mention of a satisfaction guarantee, revision guarantee, or money-back clause. For a contractor who has never bought a custom website, this is a large emotional leap into the unknown.

**T6 — Anonymous agency (no team, no founder)**
- **Principle:** Authority + likeability (Cialdini)
- There is no "About Us" section. No founder photo, no team page, no LinkedIn link, no physical address. Contractors are relationship-driven buyers who want to know who they're hiring. A faceless agency asking for $2,999 upfront faces high resistance.

**T7 — Grammar error in Pro pricing tier**
- **Principle:** Error effect on trust (cognitive fluency)
- "1 months support" (should be "1 month") on the Pro plan ($2,999). A typo in a pricing table signals lack of attention to detail — exactly the opposite of what you want to convey when selling custom website development.

---

### Cognitive Load Barriers

**C1 — "Django Backend Power" card addresses the wrong audience**
- **Principle:** Relevance / cognitive mismatch
- The middle "Why Choose Us" card is titled "Django Backend Power" and says "Built on the same technology used by Instagram and NASA." A plumber or electrician does not know what Django is and does not care. Worse, "Instagram and NASA" implies complexity and price, not reliability for a local business. The badge says "99.9% Uptime" — which is the actual benefit. Lead with that.

**C2 — Features section "Try it →" buttons create a dead-end loop**
- **Principle:** Zeigarnik effect + frustration — interrupted actions cause cognitive stress
- Visitors read "Instant Quote Calculator" and see "Try it →". They click. Nothing happens. They click again. Nothing. This loop creates confusion and erodes confidence in the product they're being sold.

**C3 — Demo navigation exposes internal architecture to prospects**
- **Principle:** Cognitive overhead — too much technical information breaks the buying mindset
- The demo nav bar (Landing | Hub | Quote | Emergency | Service Area | Portfolio | Booking) is a developer's internal navigation, not a prospect's journey. A contractor visiting to evaluate a potential vendor is suddenly given a confusing site map. The demo should feel like a polished product tour, not a dev preview.

**C4 — "Your Custom Feature" card is a missed opportunity**
- **Principle:** The endowment effect — people want to personalize/own
- The greyed-out "Your Custom Feature" card on the demo hub has no link and says "Let's Talk →" but does nothing. This is the highest-intent moment in the demo flow (the visitor is already thinking about their own feature) and it dead-ends.

---

### Motivation & Urgency Barriers

**U1 — Zero scarcity or urgency signals**
- **Principle:** Scarcity (Cialdini) + temporal discounting
- No "Currently accepting 3 new clients this month", no "Next available slot: [date]", no early-bird pricing. A contractor who leaves this page has no reason to return urgently. Urgency is completely absent.

**U2 — Hero secondary CTA "View Our Work" sends visitors away from the conversion path**
- **Principle:** Paradox of choice / distraction cost
- The hero has two CTAs side by side: "Get Your Custom Quote" (primary, correct) and "View Our Work" (secondary). The secondary anchor-scrolls to the portfolio section which has dead "View Site" buttons. It's a distraction that costs conversion without delivering the promised payoff.

**U3 — The demo-to-lead pipeline has no closing hook**
- **Principle:** Recency effect — the last thing a visitor experiences is what they remember
- After exploring all 5 demo features, a prospect returns to... nothing. There is no persistent CTA strip, no exit-intent popup, no final nudge that says "Impressed? Here's how to get this for your business." The demo hub has a "Book a Call" CTA at the bottom but it's easy to miss.

**U4 — Contact form positioned last on a very long page**
- **Principle:** Distance creates friction (spatial barrier)
- The contact form is the 5th section (below Why Choose Us → Features → Portfolio → Pricing). A mobile visitor who is convinced by the hero must scroll through ~4,000 pixels of content to reach the form. Many will drop off before arriving.

---

### Anxiety & Risk Barriers

**A1 — No phone number for action-oriented contractors**
- **Principle:** Channel preference / matching — different buyers prefer different contact modes
- The target audience (plumbers, electricians, roofers) are hands-on tradespeople who often prefer to call over filling out forms. There is no phone number on the page. This excludes a large segment of motivated buyers who will leave rather than fill a form.

**A2 — No privacy note near contact form**
- **Principle:** Anxiety reduction / data minimization
- The contact form collects name, email, phone, and project description. There is no "We respect your privacy. Your information is never sold." note immediately adjacent to the submit button. The small text at the bottom ("Your information is never shared") is too far below the fold to reduce form-submit anxiety.

**A3 — Price anchoring without context**
- **Principle:** Anchoring — without reference points, prices feel arbitrary
- $9,999 is shown with no competitive comparison ("vs. $25,000 for a custom agency", "vs. $199/mo WordPress maintenance"). The "40% lower than competitors" claim in the Why Choose Us section is not substantiated or referenced back on the pricing page.

**A4 — Demo banner may signal "this isn't real" to cold traffic**
- **Principle:** Credibility halo effect
- The prominent yellow "⚡ This is an interactive demo. All data is simulated" banner in `base.html` is visible on ALL demo pages including when clients who came from the landing page arrive. It's necessary for honesty but should be positioned to reassure rather than alarm: a first-time visitor might interpret "all data is simulated" as "this feature doesn't actually work."

---

### Friction & Usability Barriers

**F1 — Hero CTA "Get Your Custom Quote" scrolls to a very distant form**
- A click on the hero CTA triggers an anchor scroll of ~3,500px. No sticky CTA, no floating button, no interstitial. On mobile this is a 30+ swipe journey.

**F2 — FullCalendar CSS/JS loaded on every page but used nowhere**
- `base.html` loads both FullCalendar CSS and JS globally. These are large libraries (~50KB CSS + 200KB JS) loaded on every page including the landing. This degrades Core Web Vitals (LCP, FID) for zero benefit on most pages. **This is particularly harmful on the landing page which does not use FullCalendar at all.**

**F3 — Tailwind CDN Play build is not production-grade**
- The CDN Play version of Tailwind (used on both landing and demo pages) is significantly slower than a compiled/purged build. It ships the entire Tailwind library and runs in the browser. This costs performance on mobile 3G connections — a real concern for contractors who may be on job sites.

**F4 — Contact form success/error state placement**
- Form success message "Your message has been sent successfully!" appears below the submit button, not at the top of the form. On a mobile viewport the success message may be scrolled out of view, leaving the user uncertain whether the form submitted.

**F5 — Demo hub "Your Custom Feature" card is not a link**
- The 6th card on the demo hub is a `<div>` (not an `<a>`), so it's not keyboard-accessible and does not produce a pointer cursor on hover (despite hover styles). This violates basic accessibility expectations.

---

## PHASE 4 — HEURISTIC SCORING

### Landing Page `/`

| Dimension | Score (0–10) | Notes |
|---|---|---|
| Clarity of value proposition | **7/10** | Headline is good ("Bring More Jobs to Local Contractors"). Subheadline lists features, not benefits. |
| Trust & credibility signals | **4/10** | Stats and case study metrics present but unverifiable. No real testimonials, no team, no phone, no guarantee. |
| CTA strength & placement | **5/10** | Good copy on hero CTA but dead buttons in features, dead "View Site" in portfolio, generic "Send Message" on form. |
| Friction level (lower = better) | **5/10** | Long scroll to form, dead interactive elements, FullCalendar loaded unnecessarily. |
| Emotional resonance | **6/10** | "Bring More Jobs" resonates. But "Django Backend Power" kills momentum. No real human stories. |
| Mobile experience | **6/10** | Responsive design works, but hero-to-form journey is very long. No sticky CTA. |
| **Overall conversion readiness** | **5/10** | Strong visual design masks significant trust and friction gaps. |

### Demo Hub `/demo/`

| Dimension | Score (0–10) | Notes |
|---|---|---|
| Clarity of value proposition | **8/10** | "See Your Future Website in Action" — very clear. |
| Trust & credibility signals | **5/10** | Demo banner may undermine trust. Brand name differs from landing. |
| CTA strength & placement | **6/10** | "Book a Call" CTA at bottom is adequate but undersized for the payoff moment. |
| Friction level (lower = better) | **7/10** | Clean navigation, but "Your Custom Feature" is a dead end. |
| Emotional resonance | **7/10** | Good anticipation built by the feature card grid. |
| Mobile experience | **7/10** | 2-column card grid works well on mobile. |
| **Overall conversion readiness** | **6/10** | Strong entry point but drops the ball at the bottom. |

### Quote Calculator `/demo/quote/`

| Dimension | Score (0–10) | Notes |
|---|---|---|
| Clarity of value proposition | **9/10** | "Get a price in 15 seconds" — extremely clear. |
| Trust & credibility signals | **7/10** | AI-powered estimate is impressive. Rate limiting protects from abuse. |
| CTA strength & placement | **8/10** | "Get AI Estimate — Free & Instant" is outcome-focused and strong. |
| Friction level (lower = better) | **7/10** | Form is logical and not overwhelming. |
| Emotional resonance | **8/10** | Photo upload + AI feels futuristic and impressive to contractors. |
| Mobile experience | **7/10** | Two-column layout collapses well. |
| **Overall conversion readiness** | **8/10** | Best-performing demo page. |

### Booking Page `/demo/booking/`

| Dimension | Score (0–10) | Notes |
|---|---|---|
| Clarity of value proposition | **7/10** | Purpose is clear. "Powered by Cal.com" is a trust signal. |
| Trust & credibility signals | **7/10** | Calendar integrations grid adds credibility. Payment integrations are a strong bonus. |
| CTA strength & placement | **7/10** | Cal.com embed handles its own CTA. |
| Friction level (lower = better) | **6/10** | Only 3 service types shown; "Plumbing Repair" etc. confuses agency demo context. |
| Emotional resonance | **6/10** | Functional but clinical. |
| Mobile experience | **7/10** | Cal.com embed adapts well. |
| **Overall conversion readiness** | **7/10** | Solid. Context confusion (repair booking vs agency booking) is the main issue. |

---

## PHASE 5 — PRIORITIZED RECOMMENDATIONS

### 🔴 CRITICAL — Fix within 1 week

---

**CRIT-1: Fix all dead CTA buttons before they kill trust**

- **Problem:** 10+ "Try it →" and "View Site" buttons across the site do nothing when clicked. These are the single highest-priority fixes because they actively destroy credibility at peak engagement moments.
- **Psychology:** Betrayed expectation creates negative affect — a visitor who clicks something and nothing happens feels lied to. The effect compounds when the site claims to have "Live" case studies (green badge) but clicking "View Site" produces no response.
- **Exact fix:**
  - In the Features section of `/` — change each feature card's `<button class="... flex items-center gap-1">Try it →</button>` to a real `<a href="/demo/quote/">Try it →</a>` etc. Map each feature to its demo URL:
    - Instant Quote Calculator → `/demo/quote/`
    - Photo Upload Form → `/demo/quote/`
    - Google Calendar Booking → `/demo/booking/`
    - Personal Lead Dashboard → `/demo/` (or create a dashboard demo)
    - Auto City Pages → `/demo/service-area/`
    - Emergency Request Button → `/demo/emergency/`
  - In the Portfolio section — either: (a) link "View Site" cards to the corresponding demo pages as illustrative examples, OR (b) remove the "View Site" button entirely and replace with a quote: *"'Our leads tripled in 3 months.' — Carlos Martinez, Martinez Plumbing"*

---

**CRIT-2: Unify the brand name across landing and demo pages**

- **Problem:** Landing page = "ContractorWeb". Demo nav = "ContractorPro DEMO". A prospect who follows the flow from `/` to `/demo/` sees two different company names.
- **Psychology:** Brand coherence is a foundational trust signal. Inconsistency triggers suspicion and subconscious "something's off" reactions that prospects can't articulate but feel strongly.
- **Exact fix:** Pick one name and use it everywhere. If the agency is called "ContractorWeb," update `base.html` (demo nav logo) to "ContractorWeb | Demo" or simply "ContractorWeb." Alternatively, update the landing page to match "ContractorPro."

---

**CRIT-3: Fix the grammar error in the Pro pricing tier**

- **Problem:** Pro tier lists "1 months support" — a typo visible in a $2,999 pricing card.
- **Psychology:** Error effect — small errors in high-stakes contexts (pricing) disproportionately reduce perceived competence and trustworthiness.
- **Exact fix:** Change to "1 month support" (or "30-day support" for clarity).

---

**CRIT-4: Add a phone number (click-to-call) in the navigation and contact section**

- **Problem:** No phone number exists anywhere on the site. Contractors are not form-first buyers — they call. This excludes the highest-intent, action-ready segment.
- **Psychology:** Channel matching — forcing prospects into an unfamiliar mode (web form) when they prefer calling creates immediate abandonment.
- **Exact fix:**
  - Add `<a href="tel:+1XXXXXXXXXX">(555) XXX-XXXX</a>` to the desktop nav (right side, before "Get Quote" button).
  - Add the same number prominently above the contact form:
    *"Prefer to talk? Call us: **(555) XXX-XXXX** — Mon–Fri 8am–6pm"*
  - On mobile, make it a large tap target with a phone icon.

---

**CRIT-5: Add a risk reversal / satisfaction guarantee to the pricing section**

- **Problem:** Zero mention of refund, revision, or satisfaction guarantee anywhere near the pricing cards.
- **Psychology:** Loss aversion (Kahneman & Tversky) — people are 2x more sensitive to losses than gains. A $999–$9,999 purchase with no guarantee triggers the lizard brain to say "what if I hate it?"
- **Exact fix:** Add below the pricing grid:
  ```
  ✅ 100% Satisfaction Guarantee
  Not happy with the initial design? We'll revise until you love it — or refund
  your deposit. No questions asked.
  ```
  Make it a prominent badge, not a footnote.

---

### 🟡 IMPORTANT — Fix within 1 month

---

**IMP-1: Replace "Django Backend Power" with contractor-language benefits**

- **Problem:** "Django Backend Power" with "Built on the same technology used by Instagram and NASA" is developer speak that alienates plumbers, electricians, and roofers.
- **Psychology:** Relevance principle — irrelevant information doesn't just fail to persuade, it actively lowers engagement and perceived fit.
- **Exact fix — rewrite the card:**
  - **Headline:** "Built to Handle Any Job Load"
  - **Body:** "Whether it's a slow Tuesday or a storm that sends 500 homeowners to your site at once — your website stays fast. No crashes, no slow pages, no lost leads."
  - **Badge:** Keep "99.9% Uptime" — this is the actual benefit, and it's contractor-understandable.

---

**IMP-2: Add real, attributed testimonials with photos**

- **Problem:** The 4 portfolio case studies have impressive metrics but zero human faces or names. Social proof without specificity is noise.
- **Psychology:** Social proof is most powerful when it is specific (named person), similar (same trade), and verifiable (real company). A generic "+215% leads" stat is 10x less convincing than:
  *"In 90 days, we went from getting 3 quote requests a week to 11. The quote calculator alone pays for the website every month."
  **— Carlos Martinez, Owner, Martinez Plumbing (Austin, TX)***
- **Exact fix:**
  - Add a `<blockquote>` with photo, name, company, and city to each portfolio card.
  - If you don't have real testimonials yet, add a "Testimonials" section after launch and seed it with your first 3 clients.
  - Remove the "View Site" button and replace it with the quote.

---

**IMP-3: Add a sticky/floating CTA for mobile visitors**

- **Problem:** The hero CTA scrolls to a contact form that is ~3,500px below on mobile. Most mobile visitors won't scroll that far.
- **Psychology:** Spatial distance as friction — every pixel a user must travel to complete an action reduces conversion probability.
- **Exact fix:** Add a fixed bottom bar on mobile only:
  ```html
  <!-- Fixed mobile CTA -->
  <div class="fixed bottom-0 left-0 right-0 z-50 md:hidden bg-white border-t p-3">
    <a href="#contact" class="block w-full text-center bg-cyan-500 text-white py-3 rounded-lg font-semibold">
      Get Your Free Quote
    </a>
  </div>
  ```

---

**IMP-4: Rewrite the contact form submit CTA**

- **Problem:** "Send Message" is the most generic, low-conviction CTA in web design history. It describes the mechanical action, not the outcome.
- **Psychology:** Outcome-focused CTAs (Joanna Wiebe / CopyHackers) — people click toward outcomes, not actions. "Send Message" means nothing. "Get My Custom Quote" means something.
- **Exact fix — new button copy:**
  - **Primary version:** `"Get My Custom Quote — Free"`
  - **Alternative:** `"Start My Project — Get a Quote in 24 Hours"`
  - Add below the button: `🔒 Your information is private and never shared. We respond within 4 business hours.`

---

**IMP-5: Add a "Your Custom Feature" link on the demo hub**

- **Problem:** The 6th card ("Your Custom Feature") is a `<div>` with no link. It's the highest-intent card (a prospect imagining their own feature) and it dead-ends.
- **Psychology:** Reciprocity + curiosity gap — when someone is imagining owning something, closing the loop is critical. A dead CTA at this moment breaks the buying imagination.
- **Exact fix:** Make the card an `<a href="#contact">` (or `/demo/booking/` for a call) with the CTA text:
  - `"Tell us your idea →"` instead of `"Let's Talk →"`
  - Link to the contact form or booking page.

---

**IMP-6: Add urgency/scarcity signals**

- **Problem:** Zero urgency signals. A visitor who leaves the page faces no cost of delay.
- **Psychology:** Present bias — humans discount future benefits heavily. Without a "why now" signal, "I'll think about it" wins every time.
- **Exact fix options (pick one per test):**
  - Near the pricing section: *"We're currently accepting 4 new clients for Q2. Spots fill fast during contractor season."*
  - Below the hero stats: *"⚡ 2 slots available this month — typically books 2-3 weeks ahead"*
  - On the contact form: *"Get a response this week — we typically send custom proposals within 24 hours."*

---

**IMP-7: Add an "About Us" / founder section**

- **Problem:** The agency is faceless. No name, no photo, no city, no backstory.
- **Psychology:** Likeability + authority (Cialdini) — people buy from people they like and trust. A 3-sentence founder blurb with a photo and name increases trust significantly.
- **Exact fix — simple section between Portfolio and Pricing:**
  ```
  [Photo]  Hi, I'm [Name]. I built ContractorWeb after watching my uncle's
  roofing business lose leads to competitors with fancier websites.
  I've since helped 150+ contractors across 30 states. Let's build yours.
  ```

---

### 🟢 OPTIMIZATIONS — Fix within 3 months

---

**OPT-1: Remove FullCalendar from base.html global load**

- **Problem:** FullCalendar CSS (~50KB) and JS (~200KB gzipped) are loaded on every page including the landing page where they are unused.
- **Impact:** Measurable LCP and FID improvements. Google PageSpeed score increase → better SEO → more organic traffic.
- **Fix:** Move FullCalendar CDN tags to `booking/index.html`'s `{% block extra_head %}` and `{% block extra_js %}` blocks. Remove from `base.html`.

---

**OPT-2: Add a privacy policy link near the contact form**

- **Problem:** No privacy policy link adjacent to the form. Required for GDPR compliance if serving EU visitors. Also a trust signal.
- **Fix:** Add below the submit button: `By submitting, you agree to our [Privacy Policy].`

---

**OPT-3: Contextualize the demo booking page for the agency sale**

- **Problem:** The booking page shows "Plumbing Repair, Faucet/Toilet Replacement, Electrical Work" as service types — which is the contractor's service menu, not the web agency's. A prospect visiting the booking demo to understand what they'd offer their customers is confused by service types that don't match the agency context.
- **Fix option A:** Add a brief intro above the service tabs: *"Demo: This is how your customers would book a service. Below, you can switch between different service types and see the booking experience from your client's perspective."*
- **Fix option B:** Create a separate "Book a Discovery Call with ContractorWeb" CTA that links to a real Cal.com page for the agency, separate from the contractor booking demo.

---

**OPT-4: Replace "Explore the Demo" demo CTA with outcome-oriented copy**

- **Current copy:** "See Every Feature in Action → Explore the Demo"
- **Problem:** "Explore" is a passive, low-commitment verb. It doesn't create the mental picture of what the visitor will get.
- **Rewrite:** *"Try It Yourself → See How Your Future Website Would Work"* or *"Take a 3-Minute Tour → See What Your Site Could Do"*

---

**OPT-5: Add before/after conversion metrics to the demo hub**

- **Problem:** The demo hub shows features but doesn't frame them in business outcomes. A plumber sees "Instant Quote Calculator" — not what it means for his revenue.
- **Fix:** Add a single stat line under each demo card:
  - Quote Calculator: *"Clients report 2–3x more qualified leads"*
  - Emergency 24/7: *"Capture high-value urgent jobs your competitors miss"*
  - Service Area Map: *"Reduce wasted quotes by 40%"*
  - Portfolio: *"Customers who see before/after photos book 60% faster"*
  - Online Booking: *"Eliminate phone tag — 30% of bookings happen after 9pm"*

---

**OPT-6: Add a competitive comparison table to the pricing section**

- **Problem:** "$999 one-time" has no reference frame. Is it cheap or expensive relative to alternatives?
- **Fix:** Add a simple 3-column comparison below the pricing tiers:

| | ContractorWeb | DIY Website Builder | Traditional Agency |
|---|---|---|---|
| Price | $999–$9,999 (one-time) | $25–$50/mo forever | $10,000–$50,000+ |
| Custom features | ✅ | ❌ | ✅ |
| You own the code | ✅ | ❌ | Varies |
| Quote calculator | ✅ | ❌ | Extra cost |
| Launch time | 48h–3 weeks | Days | 3–6 months |

---

**OPT-7: Add a "What happens after I submit?" flow near the contact form**

- **Problem:** Form submission is an anxiety point — people don't know what happens next.
- **Fix:** Add a 3-step "What happens next?" mini-section above the form:
  1. **You submit** → takes 2 minutes
  2. **We review** → custom proposal in 24 hours
  3. **We build** → live in 48h–3 weeks

---

## PHASE 6 — A/B TEST HYPOTHESES

### Test 1 — Contact Form CTA Copy
**Ranked by expected lift: #1 (Est. +18–35% form conversion)**

| | Control | Variant |
|---|---|---|
| CTA button | "Send Message" | "Get My Custom Quote — Free" |
| Sub-text | "We typically respond within 4 business hours" | "🔒 Custom proposal emailed within 24 hours. No obligation." |

- **Principle:** Outcome-focused CTAs vs. action-focused CTAs (Joanna Wiebe copy principle)
- **Measure:** Form submission rate, contact-to-quote conversion rate
- **Hypothesis:** Renaming from generic action to specific outcome will increase submission rate by 20–35%.

---

### Test 2 — Risk Reversal on Pricing Page
**Ranked by expected lift: #2 (Est. +12–25% contact form clicks from pricing)**

| | Control | Variant |
|---|---|---|
| Pricing section | No guarantee | "✅ Satisfaction guaranteed — revise until you love it, or we refund your deposit" badge below all 3 tiers |

- **Principle:** Loss aversion (Kahneman) — a guarantee reduces perceived downside risk, making the purchase decision feel safer
- **Measure:** CTA click-through rate from pricing section → contact form
- **Hypothesis:** A visible satisfaction guarantee will increase pricing CTA clicks by 15–25%.

---

### Test 3 — Hero Headline Framing
**Ranked by expected lift: #3 (Est. +8–20% scroll depth / engagement)**

| | Control | Variant |
|---|---|---|
| H1 | "We Build Websites That Bring More Jobs to Local Contractors" | "Your Competitors Are Getting Your Jobs Because Their Website Is Better" |
| Sub | "Custom Quote Calculators • Online Booking • Lead Dashboards" | "We fix that. Fast. Starting at $999." |

- **Principle:** Pain-first framing vs. aspiration-first (loss aversion + competitive threat activates stronger response than future benefit)
- **Measure:** Scroll depth, time on page, contact form conversion rate
- **Hypothesis:** Fear of competitive loss will produce higher engagement and slightly higher form conversion in the target demographic (contractors who already feel behind).

---

### Test 4 — Portfolio Section Format
**Ranked by expected lift: #4 (Est. +10–18% trust score / form conversion)**

| | Control | Variant |
|---|---|---|
| Portfolio cards | Metrics + "View Site" (dead) button | Metrics + Real photo testimonial quote from contractor |

- **Principle:** Specific named social proof vs. anonymous statistics
- **Measure:** Scroll past portfolio section rate, time spent on portfolio section, form conversion rate for visitors who reach portfolio
- **Hypothesis:** Adding real human quotes will increase form conversion for visitors who scroll past the portfolio section.

---

### Test 5 — Sticky Mobile CTA
**Ranked by expected lift: #5 (Est. +15–30% mobile form conversions)**

| | Control | Variant |
|---|---|---|
| Mobile experience | No sticky CTA | Fixed bottom bar: "Get Your Free Quote →" |

- **Principle:** Reducing spatial friction — the cost of traveling 3,500px to a form on mobile is too high for impulse-driven decisions
- **Measure:** Mobile-specific form submission rate
- **Hypothesis:** A persistent mobile CTA will capture the ~40–60% of mobile visitors who never scroll to the contact form but had positive intent.

---

## PHASE 7 — EXECUTIVE SUMMARY

### Plain-Language Business Owner Summary

**What is working:**

Your demo site makes a strong first impression. The hero section clearly communicates the value of having a custom contractor website. The pricing is transparent and the one-time payment model is a genuine competitive advantage — most contractors are tired of monthly fees. The actual demo features (quote calculator, service area map, booking) are technically impressive and do a good job showing what the end product can do. The FAQ section is comprehensive and addresses real objections.

**The 3 biggest reasons visitors are NOT converting right now:**

1. **They don't trust you yet.** There's no face behind the business, no real names attached to your case studies, and the "View Site" buttons on your portfolio don't work — which makes your "+215% leads" numbers feel made up. A $999–$9,999 purchase requires trust, and right now you're asking for it without earning it.

2. **You're making them work too hard to say yes.** On mobile, the contact form is buried 30+ scrolls below the hero. The features section has "Try it →" buttons that do nothing. The contact form says "Send Message" instead of something that makes them feel excited about what happens next. Every one of these frictions adds up to people leaving before they decide.

3. **There's no reason to act today.** Zero urgency signals exist on the page — no limited slots, no deadline, no "we're booking up fast." A contractor who's interested but not ready will leave and never come back because nothing reminded them why today is better than next month.

**The single highest-leverage action to take first:**

Fix the dead "Try it →" buttons in the Features section and the dead "View Site" buttons in the Portfolio section. These are easy 30-minute code changes, but they eliminate the #1 trust-destroying element on your site. A prospect who clicks something and gets no response immediately doubts whether your actual product works. Link those buttons to your demo pages and your real case study portfolio, and you'll see a measurable increase in demo engagement within days.

**Realistic conversion improvement estimate:**

Implementing the Critical (1-week) fixes alone — dead buttons, brand unification, grammar fix, phone number, guarantee — is likely to improve contact form conversion rate by **15–25%**. Adding the Important (1-month) fixes (testimonials, sticky mobile CTA, rewritten form CTA, urgency) would push total improvement to an estimated **35–55%** above baseline. A/B testing the highest-priority copy changes (Tests 1–3) could compound this further to **50–70% improvement** over 90 days. These estimates assume current organic traffic baseline remains constant.

---

*Report generated by automated CRO analysis — ContractorWeb Demo Site — 2026-03-14*

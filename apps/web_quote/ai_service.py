import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class WebQuoteAIService:
    """Calls OpenRouter (google/gemini-2.5-flash-lite) to generate a website development cost estimate."""

    SYSTEM_PROMPT = (
        "You are a senior web development consultant and project estimator for a web agency "
        "that builds professional websites for local contractors (plumbers, electricians, "
        "roofers, HVAC, landscapers, and general contractors). Our agency prices are "
        "intentionally 20-35% below the US market average.\n\n"
        "Your job is to analyze a client's project description and provide an honest, "
        "detailed cost estimate.\n\n"
        "PRICING TIERS:\n"
        "Launch    ($2,499): 6-page website, AI instant quote calculator, self-serve booking (Cal.com), "
        "Google Reviews auto-sync widget, mobile responsive design, on-page SEO (title, meta, schema markup), "
        "Google Maps + GMB setup, lead notification (email), 30-day support.\n"
        "Growth    ($5,499): Everything in Launch, plus: Emergency 24/7 request button, "
        "service area map (zip code checker), before/after portfolio slider, blog setup, "
        "10 local SEO city/area pages, PageSpeed 90+ optimization, 3 months support.\n"
        "Authority ($11,999): Everything in Growth, plus: 25 local SEO city/area pages, "
        "review request automation (SMS + email), financing calculator (GreenSky/Wisetack), "
        "Spanish language version, CRM integration (Jobber, ServiceTitan, or HousecallPro), "
        "Google Analytics 4 + conversion tracking, lead dashboard, "
        "6 months priority support, project documentation.\n\n"
        "ADD-ON FEATURE PRICES (piecemeal pricing — each add-on ordered separately costs more "
        "due to individual scoping, project management, and integration testing overhead):\n"
        "  AI Quote Calculator (custom to trade):          +$600 \u2013 $900\n"
        "  Online Booking Calendar (Cal.com):              +$400 \u2013 $700\n"
        "  Emergency 24/7 Request Button:                  +$400 \u2013 $600\n"
        "  Interactive Service Area Map:                   +$550 \u2013 $800\n"
        "  Before/After Portfolio Slider:                  +$400 \u2013 $600\n"
        "  Blog / News Section:                            +$150 \u2013 $250\n"
        "  City SEO Pages (per 5 pages):                   +$325 \u2013 $550\n"
        "  PageSpeed 90+ Optimization:                     +$250 \u2013 $450\n"
        "  Lead Dashboard (admin panel):                   +$600 \u2013 $1,100\n"
        "  Review Request Automation (SMS + email):        +$600 \u2013 $1,100\n"
        "  Financing Calculator (GreenSky/Wisetack):       +$700 \u2013 $1,100\n"
        "  Spanish Language Version:                       +$500 \u2013 $1,800\n"
        "  CRM Integration (Jobber, ServiceTitan, etc.):   +$1,100 \u2013 $2,200\n"
        "  Google Analytics 4 + Conversion Tracking:       +$500 \u2013 $800\n"
        "  Photo Upload Job Forms:                         +$350 \u2013 $550\n"
        "  SMS Notifications (lead alerts):                +$350 \u2013 $550\n"
        "  Live Chat Widget Integration:                   +$200 \u2013 $300\n"
        "  Recurring Service Scheduler:                    +$600 \u2013 $1,000\n"
        "  Project Documentation:                          +$150 \u2013 $300\n\n"
        "SUPPORT PACKAGES (sold as fixed packages only — 1, 3, 6, or 12 months):\n"
        "  Support 1 month:   $160\n"
        "  Support 3 months:  $450\n"
        "  Support 6 months:  $800\n"
        "  Support 12 months: $1,500\n"
        "Each tier already includes support: Launch = 1 month ($160), Growth = 3 months ($450), "
        "Authority = 6 months ($800). When a client wants to extend beyond their tier's included "
        "support, charge only the DELTA (desired package price minus tier's included package price). "
        "Example: Growth client upgrading to 12 months pays $1,500 \u2013 $450 = +$1,050.\n\n"
        "PRICING LOGIC RULES:\n"
        "1. ADD-ONS TO LAUNCH: If a client wants Launch tier plus 1-3 specific features, "
        "DO NOT automatically upgrade them to Growth. Price it as Launch + each add-on "
        "individually. Only recommend Growth when: (a) the client needs 4+ major add-ons, "
        "or (b) the total (Launch + add-ons) exceeds or approaches the Growth price of $5,499.\n"
        "2. ADD-ONS TO GROWTH: If a client wants Growth tier plus features exclusive to Authority, "
        "DO NOT automatically upgrade them to Authority unless: (a) they need 4+ Authority-level "
        "add-ons, or (b) the total (Growth + add-ons) exceeds or approaches the Authority price of $11,999.\n"
        "3. VALUE CHECK: Always compute base tier + add-ons total. If the total approaches the "
        "next tier's price, note in assumptions that the next tier bundles all those features at a "
        "similar or lower price AND includes coordinated delivery with integration guarantees — "
        "recommend upgrading. The bundle is always the smarter choice when totals are close.\n"
        "4. UNKNOWN FEATURES: If a client requests a feature not in the add-on list, "
        "estimate its price based on complexity relative to similar features in the list. "
        "Our agency is 20-35% cheaper than the US market. Explain the estimate in assumptions.\n"
        "5. BREAKDOWN FORMAT: Always show the base tier as the first breakdown line, then "
        "each add-on as a separate line with a '+' prefix on its cost.\n"
        "6. Output ONLY valid JSON, no markdown, no explanation outside JSON.\n"
        "7. min_price and max_price are the totals (base + all add-ons combined).\n"
        "8. Round prices to the nearest $50.\n"
        "9. timeline is a short string like \"2-3 weeks\" or \"4-5 weeks\".\n"
        "10. features_included is an array of 3-6 short strings.\n"
        "11. If the description is vague, note it in assumptions and give a wider range.\n\n"
        "Return exactly this JSON structure:\n"
        "{\n"
        "  \"project_type\": \"Growth Website + CRM Integration\",\n"
        "  \"min_price\": 6399,\n"
        "  \"max_price\": 7299,\n"
        "  \"timeline\": \"3-4 weeks\",\n"
        "  \"breakdown\": [\n"
        "    {\"item\": \"Growth Website\",                   \"cost\": \"$5,499\"},\n"
        "    {\"item\": \"CRM Integration (Jobber)\",         \"cost\": \"+$900 \u2013 $1,800\"}\n"
        "  ],\n"
        "  \"features_included\": [\n"
        "    \"AI instant quote calculator\",\n"
        "    \"Self-serve booking (Cal.com)\",\n"
        "    \"Emergency 24/7 request button\",\n"
        "    \"Service area map\",\n"
        "    \"CRM sync with Jobber\",\n"
        "    \"3 months support\"\n"
        "  ],\n"
        "  \"assumptions\": \"Client on Growth tier with Jobber CRM add-on. Growth already includes the core features needed.\",\n"
        "  \"disclaimer\": \"Final price confirmed after discovery call. Prices in USD.\"\n"
        "}"
    )

    def get_estimate(
        self,
        project_description: str,
        trade: str,
        budget_range: str,
        timeline_pref: str,
    ) -> dict:
        """
        Generate a website development cost estimate via OpenRouter AI.

        Args:
            project_description: Client's description of the project.
            trade: Type of contractor trade (e.g. plumbing, electrical).
            budget_range: Client's stated budget range (e.g. "$5k–$15k").
            timeline_pref: Client's preferred timeline (e.g. "ASAP", "Flexible").

        Returns:
            Parsed AI JSON dict, or {"error": "..."} on failure.
        """
        try:
            from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError
        except ImportError:
            logger.error("openai package not installed")
            return {"error": "AI service not configured. Please contact support."}

        user_text = (
            f"Trade/industry: {trade}\n"
            f"Budget range they mentioned: {budget_range or 'Not specified'}\n"
            f"Preferred timeline: {timeline_pref or 'Not specified'}\n"
            f"Project description: {project_description}\n\n"
            "Please analyze and provide a website development cost estimate."
        )

        try:
            client = OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL,
            )
            response = client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_text},
                ],
                max_tokens=1200,
                temperature=0.2,
            )
        except APIConnectionError as e:
            logger.error("OpenRouter connection error: %s", e)
            return {"error": "Connection to AI service failed"}
        except RateLimitError as e:
            logger.warning("OpenRouter rate limit: %s", e)
            return {"error": "Service busy, please try again in 30 seconds"}
        except APIStatusError as e:
            logger.error("OpenRouter API error %s: %s", e.status_code, e)
            return {"error": f"AI service error: {e.status_code}"}
        except Exception as e:
            logger.exception("Unexpected error calling OpenRouter: %s", e)
            return {"error": "Unexpected error, please try again"}

        raw = response.choices[0].message.content or ""

        # Strip markdown code fences if the model wrapped its output
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        try:
            result = json.loads(cleaned)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error("Failed to parse AI response: %s | raw: %.300s", e, raw)
            return {"error": "Could not parse AI response", "raw": raw[:500]}

        return result

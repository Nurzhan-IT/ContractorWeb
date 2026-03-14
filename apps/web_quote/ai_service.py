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
        "Basic   ($1,999 \u2013 $3,499): 5-page site, responsive design, contact form, "
        "Google Maps, basic SEO, 2 weeks support.\n"
        "Pro     ($3,999 \u2013 $11,999): Everything in Basic, bundled with: AI Quote Calculator, "
        "Photo Upload Forms, Online Booking Calendar, 10 city SEO pages, Lead Dashboard, "
        "Emergency 24/7 Button, 1 month support.\n"
        "Premium ($17,999 \u2013 $29,999): Everything in Pro, bundled with: Advanced Analytics, "
        "CRM Integration, 50+ city pages, Recurring Scheduler, Review Management, 3 months support.\n\n"
        "ADD-ON FEATURE PRICES (can be added individually to ANY tier):\n"
        "  AI Quote Calculator (custom to trade):        +$600 \u2013 $900\n"
        "  Online Booking Calendar (Cal.com):            +$400 \u2013 $700\n"
        "  Emergency 24/7 Request Button:                +$250 \u2013 $400\n"
        "  Interactive Service Area Map:                 +$350 \u2013 $550\n"
        "  Before/After Photo Slider (gallery):          +$250 \u2013 $400\n"
        "  Photo Upload Job Forms:                       +$350 \u2013 $550\n"
        "  Lead Dashboard (admin panel):                 +$400 \u2013 $800\n"
        "  Blog / News Section:                          +$80 \u2013 $150\n"
        "  City SEO Pages (per 5 additional pages):      +$200 \u2013 $350\n"
        "  SMS Notifications:                            +$350 \u2013 $550\n"
        "  Live Chat Widget Integration:                 +$200 \u2013 $300\n"
        "  Review Management System:                     +$450 \u2013 $750\n"
        "  Advanced Analytics (GA4 + dashboards):        +$350 \u2013 $600\n"
        "  CRM Integration (Jobber, HousecallPro, etc.): +$900 \u2013 $1,800\n"
        "  Recurring Service Scheduler:                  +$600 \u2013 $1,000\n\n"
        "PRICING LOGIC RULES:\n"
        "1. ADD-ONS TO BASIC: If a client wants Basic tier plus 1-3 specific features, "
        "DO NOT automatically upgrade them to Pro. Price it as Basic + each add-on "
        "individually. Only recommend Pro when: (a) the client needs 4+ major add-ons, "
        "or (b) the total (Basic + add-ons) exceeds or approaches the Pro min price of $3,999.\n"
        "2. VALUE CHECK: Always compute Basic + add-ons total. If the total approaches "
        "$3,999, note in assumptions that Pro bundles more features at a similar price "
        "and recommend it.\n"
        "3. UNKNOWN FEATURES: If a client requests a feature not in the add-on list, "
        "estimate its price based on complexity relative to similar features in the list. "
        "Our agency is 20-35% cheaper than the US market. Explain the estimate in assumptions.\n"
        "4. BREAKDOWN FORMAT: Always show the base tier as the first breakdown line, then "
        "each add-on as a separate line with a '+' prefix on its cost.\n"
        "5. Output ONLY valid JSON, no markdown, no explanation outside JSON.\n"
        "6. min_price and max_price are the totals (base + all add-ons combined).\n"
        "7. Round prices to the nearest $50.\n"
        "8. timeline is a short string like \"2-3 weeks\" or \"4-5 weeks\".\n"
        "9. features_included is an array of 3-6 short strings.\n"
        "10. If the description is vague, note it in assumptions and give a wider range.\n\n"
        "Return exactly this JSON structure:\n"
        "{\n"
        "  \"project_type\": \"Basic Website + AI Quote Calculator + Booking Calendar\",\n"
        "  \"min_price\": 2999,\n"
        "  \"max_price\": 4899,\n"
        "  \"timeline\": \"3-4 weeks\",\n"
        "  \"breakdown\": [\n"
        "    {\"item\": \"Basic Website (5 pages)\",     \"cost\": \"$1,999 \u2013 $3,499\"},\n"
        "    {\"item\": \"AI Quote Calculator\",          \"cost\": \"+$600 \u2013 $900\"},\n"
        "    {\"item\": \"Online Booking Calendar\",      \"cost\": \"+$400 \u2013 $700\"}\n"
        "  ],\n"
        "  \"features_included\": [\n"
        "    \"Responsive mobile-first design\",\n"
        "    \"AI-powered quote calculator\",\n"
        "    \"Online booking calendar (Cal.com)\",\n"
        "    \"Contact form with email notifications\",\n"
        "    \"Google Maps integration\",\n"
        "    \"2 weeks support\"\n"
        "  ],\n"
        "  \"assumptions\": \"Client wants Basic + two add-ons. Total approaches Pro tier price; noted.\",\n"
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

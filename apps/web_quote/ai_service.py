import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class WebQuoteAIService:
    """Calls OpenRouter (google/gemini-2.5-flash-lite) to generate a website development cost estimate."""

    SYSTEM_PROMPT = (
        "You are a senior web development consultant and project estimator for a US-based "
        "web agency that builds professional websites for local contractors (plumbers, "
        "electricians, roofers, HVAC, landscapers, and general contractors).\n\n"
        "Your job is to analyze a client's project description and provide an honest, "
        "detailed cost estimate for building their business website.\n\n"
        "PRICING REFERENCE:\n"
        "- Basic site (3-5 pages, no CMS, contact form only):         $2,000 \u2013 $3,500\n"
        "- Pro site (5-10 pages, CMS/blog, booking, gallery):         $4,000 \u2013 $12,000\n"
        "- Premium site (10+ pages, custom features, integrations):   $18,000 \u2013 $30,000\n\n"
        "TYPICAL DELIVERABLES BY TIER:\n"
        "Basic:   Responsive design, contact form, Google Maps embed, SEO basics, 1 revision round\n"
        "Pro:     Everything in Basic + online booking, blog/news, before/after gallery, "
        "Google Analytics, 3 revision rounds, 3 months support\n"
        "Premium: Everything in Pro + custom quote calculator, CRM integration, multi-location "
        "support, custom animations, 6 months support, dedicated project manager\n\n"
        "RULES:\n"
        "- Always return a JSON object, nothing else.\n"
        "- Output ONLY valid JSON, no markdown, no explanation outside JSON.\n"
        "- min_price is the realistic best-case (simple scope, few revisions).\n"
        "- max_price is the realistic worst-case (scope creep, more integrations, more rounds).\n"
        "- Round prices to the nearest $100.\n"
        "- timeline is a short string like \"2\u20133 weeks\" or \"4\u20136 weeks\".\n"
        "- features_included is an array of 3\u20136 short strings.\n"
        "- If the description is vague, note it in assumptions and give a wider range.\n"
        "- Never give a range spanning more than one tier.\n"
        "- Return exactly this structure:\n"
        "{\n"
        "  \"project_type\": \"Pro Website \u2014 5-10 pages\",\n"
        "  \"min_price\": 4000,\n"
        "  \"max_price\": 7500,\n"
        "  \"timeline\": \"3\u20135 weeks\",\n"
        "  \"breakdown\": [\n"
        "    {\"item\": \"UX Design & Wireframing\", \"cost\": \"$800 \u2013 $1,200\"},\n"
        "    {\"item\": \"Frontend Development\", \"cost\": \"$1,200 \u2013 $2,000\"},\n"
        "    {\"item\": \"Backend & CMS Setup\", \"cost\": \"$1,000 \u2013 $2,500\"},\n"
        "    {\"item\": \"Online Booking Integration\", \"cost\": \"$500 \u2013 $1,000\"},\n"
        "    {\"item\": \"SEO & Analytics Setup\", \"cost\": \"$300 \u2013 $500\"},\n"
        "    {\"item\": \"Testing & Launch\", \"cost\": \"$200 \u2013 $300\"}\n"
        "  ],\n"
        "  \"features_included\": [\n"
        "    \"Responsive mobile-first design\",\n"
        "    \"Online booking calendar\",\n"
        "    \"Before/after photo gallery\",\n"
        "    \"Contact form with email notifications\",\n"
        "    \"Google Analytics & Search Console setup\",\n"
        "    \"3 rounds of design revisions\"\n"
        "  ],\n"
        "  \"assumptions\": \"Assumed standard contractor site with booking. No custom CRM integration.\",\n"
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

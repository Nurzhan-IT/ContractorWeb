import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class WebQuoteAIService:
    """Calls OpenRouter (google/gemini-2.5-flash-lite) to generate a website development cost estimate."""

    SYSTEM_PROMPT = (
        'You are a senior web development consultant and project estimator for a web agency '
        'that builds professional websites for local contractors (plumbers, electricians, '
        'roofers, HVAC, landscapers, and general contractors). Our agency prices are '
        'intentionally 20-35% below the US market average.\n\n'
        "Your job is to analyze a client's project description and provide an honest, "
        'detailed cost estimate.\n\n'
        'BASE PACKAGE — Complete ($1,499):\n'
        'Everything a contractor needs in one flat price: 6-page custom website, AI instant quote '
        'calculator, self-serve booking (Cal.com), Google Reviews auto-sync widget, mobile-first '
        'responsive design, on-page SEO (title, meta, schema markup), Google Maps + GMB setup, '
        'lead notification (email), blog setup, 10 local SEO city/area pages, PageSpeed 90+ '
        'optimization, financing calculator (GreenSky/Wisetack), Spanish language version, '
        '3 months post-launch support.\n\n'
        'ADD-ON FEATURE PRICES (features NOT included in Complete, priced individually):\n'
        '  Emergency 24/7 Request Button:                  +$400 – $600\n'
        '  Interactive Service Area Map:                   +$550 – $800\n'
        '  Before/After Portfolio Slider:                  +$400 – $600\n'
        '  City SEO Pages (per 5 pages, beyond 10):        +$325 – $550\n'
        '  Lead Dashboard (admin panel):                   +$600 – $1,100\n'
        '  Review Request Automation (SMS + email):        +$600 – $1,100\n'
        '  CRM Integration (Jobber, ServiceTitan, etc.):   +$1,100 – $2,200\n'
        '  Google Analytics 4 + Conversion Tracking:       +$500 – $800\n'
        '  Photo Upload Job Forms:                         +$350 – $550\n'
        '  SMS Notifications (lead alerts):                +$350 – $550\n'
        '  Live Chat Widget Integration:                   +$200 – $300\n'
        '  Recurring Service Scheduler:                    +$600 – $1,000\n'
        '  Project Documentation:                          +$150 – $300\n\n'
        'SUPPORT EXTENSION (beyond the 3 months already included in Complete):\n'
        '  Extend to 6 months total:  +$350\n'
        '  Extend to 12 months total: +$1,050\n\n'
        'PRICING LOGIC RULES:\n'
        '1. BASE: Always start with the Complete package ($1,499). Every client gets the full '
        'base package — there is no lower tier.\n'
        '2. ADD-ONS: Price only features the client requests that are NOT already included in '
        'Complete. Do not charge for AI quote calculator, booking calendar, blog, 10 city SEO '
        'pages, PageSpeed optimization, financing calculator, Spanish version, or 3 months '
        'support — those are all in the base.\n'
        '3. UNKNOWN FEATURES: If a client requests a feature not in the add-on list, '
        'estimate its price based on complexity relative to similar features in the list. '
        'Our agency is 20-35% cheaper than the US market. Explain the estimate in assumptions.\n'
        "4. BREAKDOWN FORMAT: Always show 'Complete Website' as the first breakdown line at "
        "$1,499, then each add-on as a separate line with a '+' prefix on its cost.\n"
        '5. Output ONLY valid JSON, no markdown, no explanation outside JSON.\n'
        '6. min_price and max_price are the totals (base + all add-ons combined).\n'
        '7. Round prices to the nearest $50.\n'
        '8. timeline is a short string like "2-3 weeks" or "4-5 weeks".\n'
        '9. features_included is an array of 3-6 short strings.\n'
        '10. If the description is vague, note it in assumptions and give a wider range.\n\n'
        'Return exactly this JSON structure:\n'
        '{\n'
        '  "project_type": "Complete Website + CRM Integration",\n'
        '  "min_price": 2599,\n'
        '  "max_price": 3699,\n'
        '  "timeline": "3-4 weeks",\n'
        '  "breakdown": [\n'
        '    {"item": "Complete Website",                  "cost": "$1,499"},\n'
        '    {"item": "CRM Integration (Jobber)",          "cost": "+$1,100 – $2,200"}\n'
        '  ],\n'
        '  "features_included": [\n'
        '    "AI instant quote calculator",\n'
        '    "Self-serve booking (Cal.com)",\n'
        '    "10 local SEO city pages",\n'
        '    "Financing calculator (GreenSky/Wisetack)",\n'
        '    "CRM sync with Jobber",\n'
        '    "3 months support"\n'
        '  ],\n'
        '  "assumptions": "Client on Complete package with Jobber CRM add-on. All other requested features are already included in the base.",\n'
        '  "disclaimer": "Final price confirmed after discovery call. Prices in USD."\n'
        '}'
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
            from openai import APIConnectionError, APIStatusError, OpenAI, RateLimitError
        except ImportError:
            logger.error('openai package not installed')
            return {'error': 'AI service not configured. Please contact support.'}

        user_text = (
            f'Trade/industry: {trade}\n'
            f'Budget range they mentioned: {budget_range or "Not specified"}\n'
            f'Preferred timeline: {timeline_pref or "Not specified"}\n'
            f'Project description: {project_description}\n\n'
            'Please analyze and provide a website development cost estimate.'
        )

        try:
            client = OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL,
            )
            response = client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=[
                    {'role': 'system', 'content': self.SYSTEM_PROMPT},
                    {'role': 'user', 'content': user_text},
                ],
                max_tokens=1200,
                temperature=0.2,
            )
        except APIConnectionError as e:
            logger.error('OpenRouter connection error: %s', e)
            return {'error': 'Connection to AI service failed'}
        except RateLimitError as e:
            logger.warning('OpenRouter rate limit: %s', e)
            return {'error': 'Service busy, please try again in 30 seconds'}
        except APIStatusError as e:
            logger.error('OpenRouter API error %s: %s', e.status_code, e)
            return {'error': f'AI service error: {e.status_code}'}
        except Exception as e:
            logger.exception('Unexpected error calling OpenRouter: %s', e)
            return {'error': 'Unexpected error, please try again'}

        raw = response.choices[0].message.content or ''

        # Strip markdown code fences if the model wrapped its output
        cleaned = raw.strip()
        if cleaned.startswith('```'):
            lines = cleaned.splitlines()
            lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            cleaned = '\n'.join(lines).strip()

        try:
            result = json.loads(cleaned)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error('Failed to parse AI response: %s | raw: %.300s', e, raw)
            return {'error': 'Could not parse AI response', 'raw': raw[:500]}

        return result

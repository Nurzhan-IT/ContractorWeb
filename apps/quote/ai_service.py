import json
import logging

from django.conf import settings

from .price_list import PRICE_LIST_TEXT

logger = logging.getLogger(__name__)


class QuoteAIService:
    """Calls OpenRouter (google/gemini-2.5-flash-lite) to generate a price estimate."""

    SYSTEM_PROMPT = (
        "You are a professional contractor estimator for a home repair company "
        "in Atlanta, GA. Your job is to analyze the customer's problem description "
        "and any provided photos, then give an honest price estimate based on the "
        "company's price list below.\n\n"
        "PRICE LIST:\n"
        + PRICE_LIST_TEXT
        + "\n\nRULES:\n"
        "- Always return a JSON object, nothing else.\n"
        "- Output ONLY valid JSON, no markdown, no explanation outside JSON.\n"
        "- Price range should be realistic: min is best-case, max is worst-case.\n"
        "- If photos show additional issues not mentioned in the description, include them.\n"
        "- If the problem is unclear, note it in the \"assumptions\" field.\n"
        "- Currency: USD. Round to nearest $50.\n"
        "- Return exactly this structure:\n"
        "{\n"
        "  \"service_type\": \"Category — Specific Service\",\n"
        "  \"min_price\": 250,\n"
        "  \"max_price\": 450,\n"
        "  \"breakdown\": [\n"
        "    {\"item\": \"Emergency call-out fee\", \"cost\": \"$85\"},\n"
        "    {\"item\": \"Labor and materials\", \"cost\": \"$120 - $280\"}\n"
        "  ],\n"
        "  \"urgency_note\": \"...\",\n"
        "  \"assumptions\": \"...\",\n"
        "  \"disclaimer\": \"Final price after on-site inspection.\"\n"
        "}"
    )

    def get_estimate(
        self,
        problem_description: str,
        address: str,
        images_base64: list,
    ) -> dict:
        """
        Generate a price estimate via OpenRouter AI.

        Args:
            problem_description: Customer's description of the problem.
            address: Service address string.
            images_base64: List of {"data": "<base64>", "media_type": "image/jpeg"}.

        Returns:
            Parsed AI JSON dict, or {"error": "..."} on failure.
        """
        try:
            from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError
        except ImportError:
            logger.error("openai package not installed")
            return {"error": "AI service not configured. Please contact support."}

        # Build user message content (multimodal)
        user_content = [
            {
                "type": "text",
                "text": (
                    f"Customer problem: {problem_description}\n"
                    f"Service address: {address}\n"
                    "Please analyze and provide a price estimate."
                ),
            }
        ]

        for img in images_base64:
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{img['media_type']};base64,{img['data']}"
                },
            })

        try:
            client = OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url=settings.OPENROUTER_BASE_URL,
            )
            response = client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
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
            # Drop opening fence line (e.g. "```json" or "```")
            lines = lines[1:]
            # Drop closing fence line if present
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        try:
            result = json.loads(cleaned)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error("Failed to parse AI response: %s | raw: %.300s", e, raw)
            return {"error": "Could not parse AI response", "raw": raw[:500]}

        return result

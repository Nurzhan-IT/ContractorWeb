# Pricing logic for the Quote Calculator.
#
# Formula: (base_min + unit_count * per_unit) * urgency_multiplier
# Output is always a RANGE (min, max) — never a single number.

PRICING_CONFIG = {
    "plumbing_leak": {"base": (150, 300),  "per_unit": 50, "unit_label": "pipes/points"},
    "faucet_toilet": {"base": (120, 250),  "per_unit": 30, "unit_label": "fixtures"},
    "water_heater":  {"base": (800, 1400), "per_unit": 0,  "unit_label": None},
    "electrical":    {"base": (200, 500),  "per_unit": 75, "unit_label": "outlets/panels"},
    "roofing":       {"base": (300, 600),  "per_unit": 2,  "unit_label": "sq ft"},
}

URGENCY_MULTIPLIERS = {
    "normal":    1.0,
    "urgent":    1.4,
    "emergency": 2.0,
}


def calculate_price(service_type: str, unit_count: int, urgency: str) -> tuple[int, int]:
    """Return (min_price, max_price) for the given job parameters."""
    config = PRICING_CONFIG[service_type]
    multiplier = URGENCY_MULTIPLIERS[urgency]
    base_min, base_max = config["base"]
    per_unit = config["per_unit"]
    min_price = round((base_min + unit_count * per_unit) * multiplier)
    max_price = round((base_max + unit_count * per_unit) * multiplier)
    return min_price, max_price

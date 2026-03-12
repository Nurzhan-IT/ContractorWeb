"""
Pricing logic for the Quote Calculator.

Formula: (base_min/max + unit_count × per_unit) × urgency_multiplier
Output is always a RANGE — never a single number (legal/realistic requirement).
"""

PRICING_CONFIG = {
    "plumbing_leak": {
        "base": (150, 300),
        "per_unit": 50,
        "unit_label": "pipes/points",
        "display": "Plumbing Leak Repair",
    },
    "faucet_toilet": {
        "base": (120, 250),
        "per_unit": 30,
        "unit_label": "fixtures",
        "display": "Faucet / Toilet Replacement",
    },
    "water_heater": {
        "base": (800, 1400),
        "per_unit": 0,
        "unit_label": None,
        "display": "Water Heater Installation",
    },
    "electrical": {
        "base": (200, 500),
        "per_unit": 75,
        "unit_label": "outlets/panels",
        "display": "Electrical Work",
    },
    "roofing": {
        "base": (300, 600),
        "per_unit": 2,
        "unit_label": "sq ft",
        "display": "Roof Repair / Replacement",
    },
}

URGENCY_MULTIPLIERS = {
    "normal":    1.0,
    "urgent":    1.4,
    "emergency": 2.0,
}


def calculate_price(service: str, unit_count: int, urgency: str) -> dict:
    """
    Return a price estimate dict for the given job parameters.

    Returns:
        {
            "min_price": int,
            "max_price": int,
            "breakdown": {
                "base": "$X – $Y",
                "units": "$Z (N units × $per_unit)"  # or None
                "urgency_surcharge": "$A – $B (40% surge)"  # or None
            }
        }
    """
    config = PRICING_CONFIG[service]
    multiplier = URGENCY_MULTIPLIERS[urgency]
    base_min, base_max = config["base"]
    per_unit = config["per_unit"]

    # Pre-multiplier subtotals
    raw_min = base_min + unit_count * per_unit
    raw_max = base_max + unit_count * per_unit

    # Final prices
    min_price = round(raw_min * multiplier)
    max_price = round(raw_max * multiplier)

    # Breakdown — units line
    units_line = None
    if per_unit > 0:
        units_total = unit_count * per_unit
        units_line = f"${units_total:,} ({unit_count} {config['unit_label']} × ${per_unit})"

    # Breakdown — urgency surcharge line
    surcharge_line = None
    if multiplier > 1.0:
        surcharge_min = round(raw_min * (multiplier - 1.0))
        surcharge_max = round(raw_max * (multiplier - 1.0))
        pct = round((multiplier - 1.0) * 100)
        surcharge_line = f"${surcharge_min:,} – ${surcharge_max:,} ({pct}% surge)"

    return {
        "min_price": min_price,
        "max_price": max_price,
        "breakdown": {
            "base": f"${base_min:,} – ${base_max:,}",
            "units": units_line,
            "urgency_surcharge": surcharge_line,
        },
    }

"""
ContractorPro Atlanta — Master Price List
Used as system context for the AI estimator.
"""

PRICE_LIST_TEXT = """
CONTRACTORPRO — SERVICE PRICE LIST
Atlanta, GA Metro Area | Effective 2025

GENERAL POLICY
- Minimum service call / trip fee: $85 (applied to all jobs, credited toward work if booked)
- All prices include labor and standard materials unless noted
- Emergency rate multiplier: ×2.0 (same-day, nights, weekends)
- Urgent rate multiplier: ×1.4 (next business day priority)
- Normal rate multiplier: ×1.0 (standard scheduling, 1–3 business days)
- Tax not included in estimates; Georgia sales tax applies to materials (~8%)
- Final price confirmed after on-site inspection

────────────────────────────────────────────────────────────────
PLUMBING SERVICES
────────────────────────────────────────────────────────────────
Emergency dispatch / after-hours call-out: $85–$125
Leak detection (non-invasive): $95–$175

Pipe repair:
  Minor repair (accessible pipe, single joint): $150–$300
  Moderate repair (under-sink, visible pipe section): $200–$400
  Major repair (in-wall or under-slab access required): $500–$1,200

Fixture replacement:
  Kitchen faucet (standard): $120–$200
  Bathroom faucet: $100–$180
  Toilet replacement (standard): $250–$450
  Toilet replacement (comfort height / dual-flush): $350–$600
  Showerhead replacement: $85–$150
  Garbage disposal installation: $180–$320

Water heater:
  Standard tank replacement (40–50 gal, electric): $800–$1,100
  Standard tank replacement (40–50 gal, gas): $900–$1,300
  High-efficiency tankless (electric): $1,200–$2,000
  High-efficiency tankless (gas, incl. venting): $1,500–$2,800
  Flush / maintenance service: $95–$150

Drain cleaning:
  Single drain (kitchen or bath): $120–$200
  Main sewer line (hydro-jet): $350–$600

────────────────────────────────────────────────────────────────
ELECTRICAL SERVICES
────────────────────────────────────────────────────────────────
Electrical inspection / diagnostic: $95–$175

Outlets & switches:
  Single outlet replacement: $85–$150
  GFCI outlet installation: $100–$175
  Switch replacement: $85–$130
  Dimmer switch installation: $100–$180
  USB outlet installation: $110–$190

Lighting:
  Ceiling light / fan installation (existing box): $120–$220
  Recessed can light installation (existing wiring): $150–$250 per light
  Outdoor security light: $175–$300
  Chandelier installation (up to 50 lbs): $200–$400

Panel & wiring:
  Circuit breaker replacement (single): $150–$280
  Whole-panel upgrade (100A → 200A, labor only): $1,200–$2,500
  New circuit run (up to 50 ft, labor only): $300–$600
  Whole-home surge protector installation: $250–$400

EV charger installation (Level 2, 240V, dedicated circuit): $500–$900

────────────────────────────────────────────────────────────────
ROOFING SERVICES
────────────────────────────────────────────────────────────────
Roof inspection: $95–$175 (waived if repair booked same day)

Repairs:
  Minor patch / single shingle replacement: $150–$350
  Flashing repair (chimney, skylight, valley): $200–$500
  Ridge cap replacement (per 10 lin ft): $150–$250
  Soft-spot repair (up to 4×4 ft decking): $300–$600

Partial re-roof / section replacement:
  Materials + labor: $3.50–$6.00 per sq ft
  (includes tear-off of one layer, underlayment, architectural shingles)

Full roof replacement (standard 2-12 pitch):
  Asphalt architectural shingles: $4.00–$7.50 per sq ft
  Metal standing-seam: $9.00–$14.00 per sq ft
  Note: Additional layers to tear off add $0.50–$1.00/sq ft

Gutters:
  Section repair / re-hanging: $150–$300
  Full gutter replacement (per lin ft): $8–$14

────────────────────────────────────────────────────────────────
HVAC SERVICES
────────────────────────────────────────────────────────────────
Diagnostic / system inspection: $95–$150

Maintenance:
  Filter replacement (standard 1"): $35–$65 (includes filter)
  Seasonal tune-up (AC or heat): $120–$200
  Duct cleaning (per vent): $30–$50

Repairs:
  Capacitor replacement: $150–$300
  Contactor replacement: $175–$325
  Refrigerant recharge (per lb, R-410A): $85–$130
  Blower motor replacement: $350–$650
  Thermostat replacement (smart): $200–$400

System replacement:
  Central AC unit (2–3 ton, split system, labor + equip): $3,500–$6,500
  Gas furnace replacement (80,000 BTU): $2,500–$4,500
  Heat pump system (2–3 ton): $4,000–$7,000
  Mini-split installation (1 zone): $1,800–$3,500

────────────────────────────────────────────────────────────────
IMPORTANT NOTES FOR ESTIMATES
────────────────────────────────────────────────────────────────
- All price ranges assume standard residential construction
- Older homes (pre-1980) may have aluminum wiring, galvanized pipes, or knob-and-tube;
  additional labor/materials costs apply
- Prices do not include permit fees (typically $75–$300 depending on municipality)
- Asbestos, mold, or lead paint remediation billed separately if discovered
- Atlanta metro area only; distances over 30 miles from I-285 add travel surcharge
"""

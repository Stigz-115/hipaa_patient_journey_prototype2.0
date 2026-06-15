"""
Synthetic Patient Journey Data Generator
=========================================
HIPAA COMPLIANCE NOTICE:
  - This module generates 100% SYNTHETIC data only.
  - NO real patient identifiers (name, DOB, SSN, MRN, address, IP, email, zip) are generated.
  - All journey data is aggregated at the COHORT level, never individual.
  - Timestamps rounded to weekly grain (Safe Harbor §164.514(b) date precision).
  - De-identification method: HIPAA Safe Harbor (18 identifiers removed).
  - For production use, apply Expert Determination per §164.514(b)(1) with qualified statistician.
"""

import random
import math
from datetime import datetime, timedelta
from typing import Optional
import hashlib

SEED = 42
random.seed(SEED)

# ── Domain constants ──────────────────────────────────────────────────────────

CONDITION_AREAS = ["oncology", "cardiology", "orthopedics", "neurology", "diabetes", "womens_health", "respiratory"]
CHANNELS = ["paid_search", "social_media", "display_ads", "email_crm", "organic_content", "hcp_referral", "dtc_content", "connected_tv"]
STAGES = ["awareness", "interest", "intent", "appointment_booked", "outcome"]
GEO_REGIONS = ["northeast", "southeast", "midwest", "southwest", "west"]  # Census regions only
DEVICE_TYPES = ["desktop", "mobile", "tablet"]
OUTCOMES = ["positive", "ongoing_treatment", "referred_specialist", "no_show", "declined"]
CONSENT_TYPES = ["full_consent", "limited_consent", "opted_out"]
DE_ID_METHODS = ["safe_harbor", "expert_determination"]
WALLED_GARDENS = {"social_media", "connected_tv"}  # channels w/ restricted direct measurement

# Channel display names
CHANNEL_LABELS = {
    "paid_search": "Paid Search",
    "social_media": "Social Media",
    "display_ads": "Display Ads",
    "email_crm": "Email / CRM",
    "organic_content": "Organic Content",
    "hcp_referral": "HCP Referral",
    "dtc_content": "DTC Content",
    "connected_tv": "Connected TV",
}

CONDITION_LABELS = {
    "oncology": "Oncology",
    "cardiology": "Cardiology",
    "orthopedics": "Orthopedics",
    "neurology": "Neurology",
    "diabetes": "Diabetes Management",
    "womens_health": "Women's Health",
    "respiratory": "Respiratory",
}

# Channel conversion propensity (synthetic, representative of typical healthcare performance)
CHANNEL_PROPENSITY = {
    "paid_search": 0.18,
    "social_media": 0.09,
    "display_ads": 0.05,
    "email_crm": 0.22,
    "organic_content": 0.14,
    "hcp_referral": 0.35,
    "dtc_content": 0.11,
    "connected_tv": 0.06,
}

CONDITION_CONVERSION = {
    "oncology": 0.21,
    "cardiology": 0.19,
    "orthopedics": 0.23,
    "neurology": 0.15,
    "diabetes": 0.28,
    "womens_health": 0.24,
    "respiratory": 0.17,
}


def _week_start(dt: datetime) -> str:
    """Round to Monday of week — Safe Harbor date precision."""
    monday = dt - timedelta(days=dt.weekday())
    return monday.strftime("%Y-%m-%d")


def _cohort_id(condition: str, region: str, channel: str, week: str) -> str:
    """Generate a non-linkable cohort identifier. NOT a patient ID."""
    raw = f"cohort|{condition}|{region}|{channel}|{week}"
    return "CHT-" + hashlib.sha256(raw.encode()).hexdigest()[:12].upper()


def generate_funnel_data(
    condition_filter: Optional[str] = None,
    region_filter: Optional[str] = None,
    weeks: int = 26,
) -> dict:
    """
    Returns aggregated funnel stage counts.
    No individual patient records — cohort-level only.
    """
    conditions = [condition_filter] if condition_filter else CONDITION_AREAS
    regions = [region_filter] if region_filter else GEO_REGIONS

    stage_counts = {s: 0 for s in STAGES}
    stage_counts["awareness"] = 0

    rng = random.Random(SEED)

    for condition in conditions:
        base = rng.randint(800, 2200)
        conv = CONDITION_CONVERSION.get(condition, 0.18)
        stage_counts["awareness"] += base
        interest = int(base * rng.uniform(0.45, 0.60))
        stage_counts["interest"] += interest
        intent = int(interest * rng.uniform(0.38, 0.52))
        stage_counts["intent"] += intent
        booked = int(intent * conv * rng.uniform(0.85, 1.15))
        stage_counts["appointment_booked"] += booked
        outcome = int(booked * rng.uniform(0.72, 0.90))
        stage_counts["outcome"] += outcome

    return {
        "stages": [
            {"stage": s, "label": s.replace("_", " ").title(), "count": stage_counts[s]}
            for s in STAGES
        ],
        "total_journeys": stage_counts["awareness"],
        "conversion_rate": round(stage_counts["appointment_booked"] / max(stage_counts["awareness"], 1) * 100, 2),
        "de_id_method": "safe_harbor",
        "data_grain": "weekly_cohort",
    }


def generate_channel_funnel(condition_filter: Optional[str] = None) -> list:
    """Channel → stage breakdown for Sankey diagram. Aggregated, no PHI."""
    rng = random.Random(SEED + 1)
    conditions = [condition_filter] if condition_filter else CONDITION_AREAS
    rows = []

    for condition in conditions:
        for channel in CHANNELS:
            prop = CHANNEL_PROPENSITY[channel]
            base = rng.randint(100, 600)
            awareness = base
            interest = int(awareness * rng.uniform(0.30, 0.65))
            intent = int(interest * rng.uniform(0.30, 0.55))
            booked = int(intent * prop * rng.uniform(0.80, 1.20))
            rows.append({
                "condition_area": condition,
                "condition_label": CONDITION_LABELS[condition],
                "channel": channel,
                "channel_label": CHANNEL_LABELS[channel],
                "awareness": awareness,
                "interest": interest,
                "intent": intent,
                "appointment_booked": booked,
                "walled_garden": channel in WALLED_GARDENS,
                "measurement_type": "modeled" if channel in WALLED_GARDENS else "observed",
            })
    return rows


def generate_touchpoint_sequences(n_journeys: int = 2000) -> list:
    """
    Generate anonymized journey sequences for MTA model input.
    journey_id is a non-linkable hash — NOT a patient identifier.
    """
    rng = random.Random(SEED + 2)
    journeys = []

    channel_weights = [CHANNEL_PROPENSITY[c] for c in CHANNELS]
    total_w = sum(channel_weights)
    channel_weights = [w / total_w for w in channel_weights]

    for i in range(n_journeys):
        n_touches = rng.choices([1, 2, 3, 4, 5, 6], weights=[20, 28, 22, 15, 10, 5])[0]
        touches = rng.choices(CHANNELS, weights=channel_weights, k=n_touches)
        days_to_convert = rng.randint(3, 120)

        # Conversion probability based on last touch + journey length bonus
        last_ch = touches[-1]
        conv_prob = CHANNEL_PROPENSITY[last_ch] * (1 + 0.05 * n_touches)
        converted = rng.random() < min(conv_prob, 0.45)

        jid = "JRN-" + hashlib.sha256(f"journey|{i}|{SEED}".encode()).hexdigest()[:10].upper()
        journeys.append({
            "journey_id": jid,
            "touches": touches,
            "n_touches": n_touches,
            "days_to_convert": days_to_convert,
            "converted": converted,
            "condition_area": rng.choice(CONDITION_AREAS),
            "geo_region": rng.choice(GEO_REGIONS),
        })
    return journeys


def generate_channel_performance(condition_filter: Optional[str] = None) -> list:
    """Channel-level KPIs for performance table. Aggregated — no PHI."""
    rng = random.Random(SEED + 3)
    rows = []
    for channel in CHANNELS:
        prop = CHANNEL_PROPENSITY[channel]
        impressions = rng.randint(80_000, 600_000)
        clicks = int(impressions * rng.uniform(0.008, 0.045))
        conversions = int(clicks * prop * rng.uniform(0.7, 1.3))
        cost = rng.randint(8_000, 95_000)
        cpa = cost / max(conversions, 1)
        rows.append({
            "channel": channel,
            "channel_label": CHANNEL_LABELS[channel],
            "impressions": impressions,
            "clicks": clicks,
            "ctr": round(clicks / impressions * 100, 2),
            "conversions": conversions,
            "cost": cost,
            "cpa": round(cpa, 2),
            "walled_garden": channel in WALLED_GARDENS,
            "measurement_type": "modeled" if channel in WALLED_GARDENS else "observed",
            "trend": [rng.randint(max(0, conversions - 30), conversions + 30) for _ in range(8)],
        })
    return sorted(rows, key=lambda x: x["conversions"], reverse=True)


def generate_weekly_trend(weeks: int = 26) -> list:
    """Weekly aggregated journey volume — no individual data."""
    rng = random.Random(SEED + 5)
    base_date = datetime(2025, 1, 6)  # Start of year (Monday)
    rows = []
    base = 320
    for w in range(weeks):
        dt = base_date + timedelta(weeks=w)
        vol = int(base * (1 + 0.3 * math.sin(w / 4)) + rng.gauss(0, 15))
        booked = int(vol * rng.uniform(0.14, 0.22))
        rows.append({
            "week": _week_start(dt),
            "journeys": max(vol, 50),
            "appointments": max(booked, 5),
        })
        base = vol * 0.85 + base * 0.15
    return rows


def generate_audit_log(n: int = 40) -> list:
    """Simulated audit log entries (HIPAA §164.312(b) audit controls)."""
    rng = random.Random(SEED + 10)
    users = ["analyst_mk01", "coordinator_sr02", "admin_jt03", "marketer_pl04", "analyst_ch05"]
    queries = [
        "GET /api/journey/funnel?condition=oncology",
        "GET /api/attribution?model=shapley",
        "GET /api/channel/performance",
        "GET /api/journey/sankey",
        "GET /api/compliance/status",
        "GET /api/journey/trend",
    ]
    legal_bases = ["Business Associate Agreement", "Marketing Authorization", "Operations Analytics"]
    data_categories = ["Aggregated Cohort", "Attribution Model Output", "Channel KPIs", "Compliance Metadata"]

    log = []
    base_ts = datetime(2026, 6, 1, 8, 0, 0)
    for i in range(n):
        ts = base_ts + timedelta(minutes=rng.randint(0, 60 * 24 * 14))
        log.append({
            "log_id": f"AUD-{str(i+1).zfill(5)}",
            "timestamp": ts.isoformat() + "Z",
            "user_id": rng.choice(users),
            "action": rng.choice(queries),
            "data_category": rng.choice(data_categories),
            "legal_basis": rng.choice(legal_bases),
            "phi_accessed": False,   # Always false — PHI never enters analytics layer
            "de_id_confirmed": True,
        })
    return sorted(log, key=lambda x: x["timestamp"], reverse=True)


def generate_consent_summary() -> dict:
    """Consent and opt-out cohort sizing."""
    rng = random.Random(SEED + 20)
    total = rng.randint(18_000, 22_000)
    full = int(total * rng.uniform(0.62, 0.70))
    limited = int(total * rng.uniform(0.18, 0.24))
    opted_out = total - full - limited
    return {
        "total_cohort_size": total,
        "full_consent": full,
        "limited_consent": limited,
        "opted_out": opted_out,
        "opted_out_excluded": True,  # Opted-out cohorts always excluded from analytics
        "consent_framework": "HIPAA Marketing Authorization + State Law Overlay",
    }


def generate_state_law_matrix() -> list:
    """State/federal law applicability matrix."""
    return [
        {
            "law": "HIPAA Privacy Rule",
            "jurisdiction": "Federal",
            "applies_to": "All covered entities & BAs",
            "key_requirement": "Min. necessary; marketing auth for PHI use; BAAs required",
            "status": "active",
            "effective": "2003",
        },
        {
            "law": "My Health MY Data Act",
            "jurisdiction": "Washington State",
            "applies_to": "Any entity collecting consumer health data (regardless of HIPAA)",
            "key_requirement": "Opt-in consent; no geofencing health facilities; right to deletion",
            "status": "active",
            "effective": "2024-03-31",
        },
        {
            "law": "CMIA (Confidentiality of Medical Info Act)",
            "jurisdiction": "California",
            "applies_to": "Providers, health plans, contractors",
            "key_requirement": "Stricter than HIPAA; no selling medical info; explicit consent",
            "status": "active",
            "effective": "1981 (amended 2023)",
        },
        {
            "law": "THIPA (Texas Health & Safety Code §181)",
            "jurisdiction": "Texas",
            "applies_to": "Covered entities + downstream vendors",
            "key_requirement": "Express consent for marketing; training requirements",
            "status": "active",
            "effective": "2012",
        },
        {
            "law": "FTC Health Breach Notification Rule",
            "jurisdiction": "Federal",
            "applies_to": "PHR vendors and related entities",
            "key_requirement": "60-day breach notification; expanded to cover health apps (2024)",
            "status": "active",
            "effective": "2024 (amended)",
        },
    ]

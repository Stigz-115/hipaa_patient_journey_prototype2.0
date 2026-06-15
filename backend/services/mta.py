"""
Multi-Touch Attribution (MTA) Models
======================================
HIPAA NOTE: All inputs are anonymized journey sequences (journey_id hash, channel list).
No PHI fields are processed. These models operate on de-identified touchpoint sequences only.

Models implemented:
  1. First Touch        — 100% credit to first touchpoint
  2. Last Touch         — 100% credit to last touchpoint
  3. Linear             — Equal credit across all touchpoints
  4. Time Decay         — Exponentially more credit to touchpoints closer to conversion
  5. Data-Driven        — Shapley value approximation (game-theoretic, channel marginal contribution)
"""

from collections import defaultdict
from itertools import combinations
from typing import Literal
import math


ModelName = Literal["first_touch", "last_touch", "linear", "time_decay", "data_driven"]

ALL_MODELS: list[ModelName] = ["first_touch", "last_touch", "linear", "time_decay", "data_driven"]

MODEL_LABELS = {
    "first_touch": "First Touch",
    "last_touch": "Last Touch",
    "linear": "Linear",
    "time_decay": "Time Decay",
    "data_driven": "Data-Driven (Shapley)",
}

MODEL_DESCRIPTIONS = {
    "first_touch": "Assigns 100% of conversion credit to the first touchpoint. Best for measuring awareness-driving channels.",
    "last_touch": "Assigns 100% of conversion credit to the final touchpoint before conversion. Favors bottom-of-funnel channels like HCP referral.",
    "linear": "Distributes credit equally across all touchpoints in the journey. Simple and unbiased but ignores position effects.",
    "time_decay": "Assigns exponentially more credit to touchpoints closer to conversion. Suitable for shorter sales cycles.",
    "data_driven": "Uses Shapley values (game theory) to estimate each channel's marginal contribution to conversion. Gold standard for healthcare MTA but requires sufficient conversion volume.",
}

HEALTHCARE_CONTEXT = {
    "first_touch": "For pharma/device marketers: use to optimize top-of-funnel disease awareness campaigns. Good for new indication launches.",
    "last_touch": "For pharma/device marketers: overstates HCP referral and paid search; undervalues long-cycle disease awareness. Use with caution for budget allocation.",
    "linear": "For pharma/device marketers: undervalues the HCP referral that often closes the journey; use as a neutral baseline.",
    "time_decay": "For pharma/device marketers: appropriate for condition areas with short decision cycles (e.g., acute respiratory). Less suitable for oncology (long research phase).",
    "data_driven": "For pharma/device marketers: recommended for mature programs with 500+ conversions/month. Reveals true marginal value of each channel — critical for ROAS optimization in walled-garden environments.",
}


def _normalize(credits: dict[str, float]) -> dict[str, float]:
    total = sum(credits.values())
    if total == 0:
        return credits
    return {k: round(v / total, 4) for k, v in credits.items()}


def first_touch(journeys: list[dict]) -> dict[str, float]:
    credits: dict[str, float] = defaultdict(float)
    for j in journeys:
        if j["converted"] and j["touches"]:
            credits[j["touches"][0]] += 1.0
    return _normalize(dict(credits))


def last_touch(journeys: list[dict]) -> dict[str, float]:
    credits: dict[str, float] = defaultdict(float)
    for j in journeys:
        if j["converted"] and j["touches"]:
            credits[j["touches"][-1]] += 1.0
    return _normalize(dict(credits))


def linear_attribution(journeys: list[dict]) -> dict[str, float]:
    credits: dict[str, float] = defaultdict(float)
    for j in journeys:
        if j["converted"] and j["touches"]:
            share = 1.0 / len(j["touches"])
            for ch in j["touches"]:
                credits[ch] += share
    return _normalize(dict(credits))


def time_decay(journeys: list[dict], half_life_days: float = 7.0) -> dict[str, float]:
    """Exponential decay: touchpoints closer to conversion get more credit."""
    credits: dict[str, float] = defaultdict(float)
    for j in journeys:
        if j["converted"] and j["touches"]:
            n = len(j["touches"])
            days = j["days_to_convert"]
            # Distribute days across touchpoints linearly
            weights = []
            for pos in range(n):
                days_before = days * (n - 1 - pos) / max(n - 1, 1)
                w = math.exp(-math.log(2) * days_before / half_life_days)
                weights.append(w)
            total_w = sum(weights)
            for ch, w in zip(j["touches"], weights):
                credits[ch] += w / total_w
    return _normalize(dict(credits))


def shapley_attribution(journeys: list[dict]) -> dict[str, float]:
    """
    Approximate Shapley values via sampled coalition method.
    Full Shapley is 2^n — this uses marginal contribution sampling for efficiency.
    """
    # Build conversion rates per channel set (sample-based)
    channel_conversions: dict[str, list[int]] = defaultdict(list)
    for j in journeys:
        for ch in set(j["touches"]):
            channel_conversions[ch].append(1 if j["converted"] else 0)

    # Channel conversion rates (marginal baseline)
    ch_rates = {
        ch: sum(v) / max(len(v), 1)
        for ch, v in channel_conversions.items()
    }

    # Shapley via marginal contribution across sampled orderings
    all_channels = list(ch_rates.keys())
    shapley_vals: dict[str, float] = defaultdict(float)
    n_samples = 500
    import random as _rng
    _r = _rng.Random(42)

    for _ in range(n_samples):
        perm = all_channels[:]
        _r.shuffle(perm)
        prev_val = 0.0
        for i, ch in enumerate(perm):
            coalition = set(perm[:i+1])
            # Coalition value = weighted avg conversion rate of members
            val = sum(ch_rates.get(c, 0) for c in coalition) / len(coalition)
            shapley_vals[ch] += val - prev_val
            prev_val = val

    for ch in shapley_vals:
        shapley_vals[ch] /= n_samples

    return _normalize(dict(shapley_vals))


def run_model(model: ModelName, journeys: list[dict]) -> dict:
    if model == "first_touch":
        credits = first_touch(journeys)
    elif model == "last_touch":
        credits = last_touch(journeys)
    elif model == "linear":
        credits = linear_attribution(journeys)
    elif model == "time_decay":
        credits = time_decay(journeys)
    elif model == "data_driven":
        credits = shapley_attribution(journeys)
    else:
        raise ValueError(f"Unknown model: {model}")

    return {
        "model": model,
        "model_label": MODEL_LABELS[model],
        "description": MODEL_DESCRIPTIONS[model],
        "healthcare_context": HEALTHCARE_CONTEXT[model],
        "credits": credits,
        "phi_used": False,
        "input_data": "anonymized_journey_sequences",
    }


def run_all_models(journeys: list[dict]) -> list[dict]:
    return [run_model(m, journeys) for m in ALL_MODELS]

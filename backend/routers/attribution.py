from fastapi import APIRouter, Query
from typing import Optional
from backend.data.synthetic_generator import (
    generate_touchpoint_sequences,
    generate_channel_performance,
    CHANNEL_LABELS,
)
from backend.services.mta import run_model, run_all_models, ALL_MODELS, MODEL_LABELS

router = APIRouter(prefix="/api/attribution", tags=["attribution"])

# Pre-generate journeys once (cached in module scope)
_JOURNEYS = generate_touchpoint_sequences(n_journeys=2000)


@router.get("/models")
def list_models():
    """Available MTA models."""
    return {"models": [{"value": m, "label": MODEL_LABELS[m]} for m in ALL_MODELS]}


@router.get("/run")
def run_attribution(model: str = Query("data_driven")):
    """Run a single MTA model. Returns channel credit scores summing to 1.0."""
    if model not in ALL_MODELS:
        model = "data_driven"
    result = run_model(model, _JOURNEYS)
    # Shape for frontend: list of {channel, channel_label, credit, pct}
    credits = result["credits"]
    rows = sorted(
        [
            {
                "channel": ch,
                "channel_label": CHANNEL_LABELS.get(ch, ch),
                "credit": credits.get(ch, 0.0),
                "pct": round(credits.get(ch, 0.0) * 100, 1),
            }
            for ch in CHANNEL_LABELS
        ],
        key=lambda x: x["credit"],
        reverse=True,
    )
    return {**result, "rows": rows}


@router.get("/compare")
def compare_all_models():
    """Run all 5 MTA models and return side-by-side comparison."""
    results = run_all_models(_JOURNEYS)
    channels = list(CHANNEL_LABELS.keys())
    channel_labels = list(CHANNEL_LABELS.values())

    # Build matrix: channel → {model: pct}
    matrix = []
    for ch in channels:
        row = {
            "channel": ch,
            "channel_label": CHANNEL_LABELS[ch],
        }
        for r in results:
            row[r["model"]] = round(r["credits"].get(ch, 0.0) * 100, 1)
        matrix.append(row)

    return {
        "models": [{"value": r["model"], "label": r["model_label"], "description": r["description"], "healthcare_context": r["healthcare_context"]} for r in results],
        "matrix": matrix,
        "phi_used": False,
        "input": "anonymized_journey_sequences",
    }

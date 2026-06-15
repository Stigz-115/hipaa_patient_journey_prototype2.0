from fastapi import APIRouter
from backend.data.synthetic_generator import (
    generate_channel_performance,
    generate_audit_log,
    generate_consent_summary,
    generate_state_law_matrix,
    CHANNEL_LABELS,
)

router = APIRouter(prefix="/api", tags=["channel", "compliance"])


@router.get("/channel/performance")
def get_channel_performance():
    """Channel KPI table. Aggregated — no PHI."""
    return {"channels": generate_channel_performance()}


@router.get("/compliance/audit-log")
def get_audit_log():
    """Simulated HIPAA §164.312(b) audit log. Confirms no PHI accessed."""
    return {
        "entries": generate_audit_log(),
        "phi_in_log": False,
        "retention_policy": "6 years (HIPAA §164.530(j))",
    }


@router.get("/compliance/consent")
def get_consent():
    """Consent and opt-out cohort summary."""
    return generate_consent_summary()


@router.get("/compliance/laws")
def get_laws():
    """State and federal law applicability matrix."""
    return {"laws": generate_state_law_matrix()}


@router.get("/compliance/status")
def get_compliance_status():
    """Overall compliance posture for dashboard badge."""
    return {
        "status": "compliant",
        "de_id_method": "HIPAA Safe Harbor (§164.514(b)(2))",
        "phi_in_pipeline": False,
        "audit_controls": True,
        "baa_required": True,
        "last_verified": "2026-06-15T00:00:00Z",
        "frameworks": ["HIPAA", "WA_MHMD", "CA_CMIA", "TX_THIPA", "FTC_HBNR"],
    }


@router.get("/dashboard/kpis")
def get_kpis():
    """Top-level KPIs for dashboard overview."""
    from backend.data.synthetic_generator import generate_funnel_data, generate_touchpoint_sequences
    funnel = generate_funnel_data()
    journeys = generate_touchpoint_sequences(500)
    n_converted = sum(1 for j in journeys if j["converted"])
    avg_touches = sum(j["n_touches"] for j in journeys) / max(len(journeys), 1)

    stages = {s["stage"]: s["count"] for s in funnel["stages"]}
    return {
        "total_journeys_analyzed": funnel["total_journeys"],
        "appointment_conversion_rate": funnel["conversion_rate"],
        "avg_touchpoints_to_book": round(avg_touches, 1),
        "journeys_with_positive_outcome": stages.get("outcome", 0),
        "data_note": "Cohort-level aggregation. HIPAA Safe Harbor de-identified.",
    }

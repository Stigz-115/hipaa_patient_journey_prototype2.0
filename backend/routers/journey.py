from fastapi import APIRouter, Query
from typing import Optional
from backend.data.synthetic_generator import (
    generate_funnel_data,
    generate_channel_funnel,
    generate_weekly_trend,
    CONDITION_AREAS,
    CONDITION_LABELS,
    GEO_REGIONS,
)

router = APIRouter(prefix="/api/journey", tags=["journey"])


@router.get("/funnel")
def get_funnel(
    condition: Optional[str] = Query(None, description="Filter by condition area"),
    region: Optional[str] = Query(None, description="Filter by census region"),
):
    """Aggregated funnel stage counts. Cohort-level only. No PHI."""
    cond = condition if condition in CONDITION_AREAS else None
    reg = region if region in GEO_REGIONS else None
    return generate_funnel_data(condition_filter=cond, region_filter=reg)


@router.get("/sankey")
def get_sankey(condition: Optional[str] = Query(None)):
    """Channel → stage flow data for Sankey diagram. Aggregated, no PHI."""
    cond = condition if condition in CONDITION_AREAS else None
    return {"flows": generate_channel_funnel(condition_filter=cond)}


@router.get("/trend")
def get_trend():
    """Weekly journey volume trend. No individual data."""
    return {"weeks": generate_weekly_trend()}


@router.get("/filters")
def get_filters():
    """Available filter options."""
    return {
        "conditions": [{"value": k, "label": v} for k, v in CONDITION_LABELS.items()],
        "regions": GEO_REGIONS,
    }

# HIPAA-Safe Patient Journey & MTA Prototype

## Context

Healthcare, pharma, and medical device marketers need to understand the full patient journey — from initial awareness through conversion (appointment booking) to outcomes — while operating under HIPAA, state health data laws (WA My Health MY Data Act, CA CMIA, etc.), and FTC regulations. Traditional ad-tech attribution cannot legally touch PHI in analytics pipelines, so the prototype must demonstrate a **privacy-safe MTA architecture**: aggregated, de-identified, no PHI in the analytics layer.

This prototype uses **100% synthetic data** — no real patients, no real PHI — and is designed to show stakeholders what a compliant analytics experience would look like in production.

---

## Scope & Non-Goals

**In scope:**
- Synthetic patient journey data generator (HIPAA-safe: no real PHI ever)
- Multi-touch attribution (MTA) models: first-touch, last-touch, linear, time-decay, data-driven (Shapley)
- Funnel visualization: Awareness → Interest → Intent → Appointment Booked → Outcome
- Channel/touchpoint breakdown: paid search, social, display, email, organic, DTC content, HCP referral
- Compliance posture page: explains what data is and isn't used, audit log mock-up, consent flags
- De-identification layer explanation (Safe Harbor vs. Expert Determination)
- Privacy governance dashboard: data lineage mock, access control display

**Non-goals (v1):**
- Real patient data ingestion of any kind
- Live API integrations (ad platforms, CRMs, EMRs)
- Authentication system (prototype only; note: production must have RBAC + MFA)
- Real-time streaming data

---

## Compliance Architecture Principles

These govern every design decision in the prototype and must be visible in the UI:

1. **No PHI in analytics layer** — All journey data is aggregated or synthetic. No individual identifiers (name, DOB, MRN, address, device ID, IP, email) touch the analytics pipeline.
2. **Minimum Necessary Standard** — Only data attributes needed for attribution are used. Shown via field-level tagging in data schema view.
3. **De-identification methods** — Safe Harbor (18 identifiers removed) or Expert Determination. Prototype labels which method applies to each dataset.
4. **Consent & Opt-out** — Every journey segment shows consent flag. Opted-out cohorts excluded automatically.
5. **Audit Log** — Every data access is logged with: user, timestamp, query, data category, legal basis.
6. **State law overlay** — WA My Health MY Data (2024), CA CMIA, TX THIPA flagged. Stricter of federal/state applies.
7. **Walled Garden Handling** — Pharma/device ad platforms (Meta Health, Google Health Audiences) shown with their data restrictions; modeled attribution used where direct measurement is blocked.

---

## Tech Stack

| Layer | Choice |
|---|---|
| Backend | Python 3.12 + FastAPI |
| Frontend | React 18 + TypeScript + Tailwind + shadcn/ui |
| Data | 100% synthetic, generated in-memory with Faker + custom healthcare logic |
| Charts | Recharts (React) |
| MTA Models | Pure Python: Shapley values, time-decay, linear attribution |
| Dev tooling | uv (deps), Vite (frontend), uvicorn (backend) |

Template base: **React App (I9QtVh1syu3rpegx3bu7)**

---

## Application Structure

```
hipaa_patient_journey_prototype/
├── backend/
│   ├── main.py                  # FastAPI app, CORS, routers
│   ├── data/
│   │   ├── synthetic_generator.py   # Faker-based patient journey data
│   │   └── models.py                # Pydantic schemas (no PHI fields)
│   ├── services/
│   │   ├── mta.py               # Attribution model logic
│   │   ├── funnel.py            # Funnel stage aggregation
│   │   └── compliance.py        # Audit log + de-id metadata
│   └── routers/
│       ├── journey.py           # /api/journey/* endpoints
│       ├── attribution.py       # /api/attribution/* endpoints
│       └── compliance.py        # /api/compliance/* endpoints
└── frontend/
    └── src/
        ├── pages/
        │   ├── Dashboard.tsx        # Overview KPIs
        │   ├── JourneyMap.tsx       # Sankey/funnel journey view
        │   ├── Attribution.tsx      # MTA model comparison
        │   ├── ChannelAnalysis.tsx  # Channel performance
        │   └── Compliance.tsx       # Privacy posture + audit log
        └── components/
            ├── FunnelChart.tsx
            ├── SankeyDiagram.tsx
            ├── AttributionComparison.tsx
            ├── AuditLogTable.tsx
            └── ComplianceBadge.tsx
```

---

## Synthetic Data Model

**Journey Event** (what flows through the system — no PHI):
```
cohort_id        string   # Non-identifying segment ID (not patient ID)
journey_stage    enum     # awareness | interest | intent | booked | outcome
channel          enum     # paid_search | social | display | email | organic | hcp_referral | dtc_content
touchpoint_ts    datetime # Rounded to week (Safe Harbor date precision)
condition_area   enum     # oncology | cardiology | orthopedics | neurology | diabetes
geo_region       enum     # Census region only (not zip, not city — Safe Harbor)
device_type      enum     # desktop | mobile | tablet
consent_status   bool     # true = consented
de_id_method     enum     # safe_harbor | expert_determination
```

No individual patient ID. Cohort-level aggregation only. All timestamps rounded to weekly grain.

**Attribution Touchpoint** (for MTA model input):
```
journey_id       string   # Anonymized journey hash (not linkable to patient)
channel          string
position         int      # Ordinal position in journey
days_to_convert  int
converted        bool
```

---

## Pages & Features

### 1. Dashboard (overview)
- KPI cards: Total journeys analyzed, Conversion rate, Avg. touchpoints to book, Top converting channel
- Journey stage funnel (bar chart)
- Channel mix donut
- Compliance status banner (green/amber/red)

### 2. Patient Journey Map
- Sankey diagram: channel → stage → stage → conversion
- Filter by: condition area, geo region, date range, consent status
- Hover: shows aggregated cohort stats (never individual)
- Data privacy label on every chart: "Aggregated cohort data. De-identified per HIPAA Safe Harbor."

### 3. Multi-Touch Attribution
- Model selector: First Touch / Last Touch / Linear / Time-Decay / Data-Driven (Shapley)
- Side-by-side bar chart comparing channel credit across models
- Explanation panel: what each model means for healthcare marketing decisions
- "What this means for pharma/device" tooltip layer

### 4. Channel Analysis
- Table + sparkline: channel → impressions → clicks → conversions → attributed value
- Walled garden indicator: channels where direct measurement is restricted (Meta, Google Health)
- Modeled vs. observed attribution flag

### 5. Compliance Posture
- De-identification method badge per dataset
- Consent funnel: consented vs. opted-out cohort sizes
- State law applicability matrix (HIPAA / WA / CA / TX)
- Audit log table: simulated access log entries
- Data lineage diagram: source → de-id layer → analytics layer (shows PHI never enters analytics)

---

## Implementation Steps

1. Clone React App template → establish project scaffold
2. Set up `uv` Python environment; install FastAPI, uvicorn, faker, pydantic
3. Build `synthetic_generator.py` — generates ~10k journey events with full compliance field set
4. Build MTA service — implement all 5 attribution models in pure Python
5. Build FastAPI routers (journey, attribution, compliance)
6. Wire start.sh — runs both FastAPI (port $APP_PORT) and Vite dev server
7. Build React pages in order: Dashboard → JourneyMap → Attribution → ChannelAnalysis → Compliance
8. Add compliance banner component (visible on every page)
9. Add "Privacy Architecture" sidebar panel explaining data flow
10. Verify all endpoints with curl; visual smoke-test each page

---

## Verification

- `curl /api/journey/funnel` returns aggregated stage counts (no individual IDs)
- `curl /api/attribution?model=shapley` returns channel credit scores summing to 1.0
- `curl /api/compliance/audit-log` returns mock log entries
- UI: Sankey renders without individual patient labels
- UI: Every chart has compliance label visible
- UI: Compliance page shows de-id method for each dataset segment
- No field named `patient_id`, `name`, `dob`, `ssn`, `mrn`, `email`, `ip`, `zip` in any API response

"""
PathIQ — HIPAA-Safe Patient Journey Analytics (Streamlit)
===========================================================
HIPAA COMPLIANCE NOTICE:
  All data is 100% SYNTHETIC. No PHI. No real patient records.
  De-identified per HIPAA Safe Harbor §164.514(b)(2).
  For presentation to healthcare marketing, pharma, and medical device stakeholders.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import altair as alt
import pandas as pd

from backend.data.synthetic_generator import (
    generate_funnel_data,
    generate_channel_funnel,
    generate_weekly_trend,
    generate_touchpoint_sequences,
    generate_channel_performance,
    generate_audit_log,
    generate_consent_summary,
    generate_state_law_matrix,
    CONDITION_LABELS,
    CHANNEL_LABELS,
)
from backend.services.mta import (
    run_model, run_all_models, ALL_MODELS,
    MODEL_LABELS, MODEL_DESCRIPTIONS, HEALTHCARE_CONTEXT,
)

# ── Palette ───────────────────────────────────────────────────────────────────
TEAL  = "#2dd4bf"
AMBER = "#fbbf24"
GREEN = "#4ade80"
RED   = "#f87171"

CHANNEL_COLORS = {
    "paid_search":     "#2dd4bf",
    "social_media":    "#818cf8",
    "display_ads":     "#38bdf8",
    "email_crm":       "#4ade80",
    "organic_content": "#fb923c",
    "hcp_referral":    "#f472b6",
    "dtc_content":     "#a78bfa",
    "connected_tv":    "#fbbf24",
}

MODEL_COLORS = {
    "first_touch":  "#38bdf8",
    "last_touch":   "#f472b6",
    "linear":       "#a78bfa",
    "time_decay":   "#fb923c",
    "data_driven":  "#2dd4bf",
}

STAGE_COLORS = ["#2dd4bf", "#14b8a6", "#0d9488", "#0f766e", "#115e59"]

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PathIQ · Patient Journey Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Password gate ─────────────────────────────────────────────────────────────
def _check_password() -> bool:
    if st.session_state.get("_authenticated"):
        return True

    st.markdown("""
    <div style="max-width:400px;margin:80px auto 0;text-align:center;">
        <div style="font-family:'DM Serif Display',serif;font-size:2rem;color:#e8f0fe;margin-bottom:6px;">PathIQ</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#4a6080;
            letter-spacing:0.12em;text-transform:uppercase;margin-bottom:32px;">
            Patient Journey Analytics · Restricted Access
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, col_c, _ = st.columns([1, 2, 1])
    with col_c:
        pwd = st.text_input("Password", type="password", placeholder="Enter access password")
        if st.button("Access →", use_container_width=True):
            correct = st.secrets.get("APP_PASSWORD", "")
            if pwd == correct and correct != "":
                st.session_state["_authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.markdown('<div style="text-align:center;font-family:\'IBM Plex Mono\',monospace;font-size:9px;color:#4a6080;margin-top:16px;">🔒 HIPAA-Safe Prototype · Synthetic Data Only</div>', unsafe_allow_html=True)
    return False

if not _check_password():
    st.stop()

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=IBM+Plex+Mono:wght@400;500;600&family=Instrument+Sans:wght@400;500;600&display=swap');
html, body, [class*="st-"] { font-family: 'Instrument Sans', sans-serif; }
.stApp {
    background: #040d1a;
    background-image: linear-gradient(rgba(45,212,191,0.025) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(45,212,191,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071228 0%, #040d1a 100%);
    border-right: 1px solid rgba(45,212,191,0.12);
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(12,30,61,0.95), rgba(7,18,40,0.95));
    border: 1px solid rgba(45,212,191,0.15);
    border-radius: 12px;
    padding: 20px !important;
}
[data-testid="stMetricValue"] { font-family:'IBM Plex Mono',monospace !important; color:#2dd4bf !important; font-size:2rem !important; }
[data-testid="stMetricLabel"] { color:#94a3b8 !important; font-size:11px !important; font-weight:600 !important; letter-spacing:0.08em !important; text-transform:uppercase !important; }
h1,h2,h3 { font-family:'DM Serif Display',serif !important; color:#e8f0fe !important; }
[data-testid="stDataFrame"] { border:1px solid rgba(45,212,191,0.15) !important; border-radius:8px !important; }
[data-testid="stTabs"] button { font-family:'IBM Plex Mono',monospace !important; font-size:11px !important; letter-spacing:0.05em !important; text-transform:uppercase !important; color:#4a6080 !important; }
[data-testid="stTabs"] button[aria-selected="true"] { color:#2dd4bf !important; border-bottom-color:#2dd4bf !important; }
hr { border-color:rgba(45,212,191,0.12) !important; }
p, span, li { color:#94a3b8; }
strong { color:#e8f0fe !important; }
</style>
""", unsafe_allow_html=True)

# ── Cached data ───────────────────────────────────────────────────────────────
@st.cache_data
def load_journeys():       return generate_touchpoint_sequences(2000)
@st.cache_data
def load_channel_perf():   return generate_channel_performance()
@st.cache_data
def load_audit_log():      return generate_audit_log()
@st.cache_data
def load_consent():        return generate_consent_summary()
@st.cache_data
def load_laws():           return generate_state_law_matrix()
@st.cache_data
def load_mta_comparison(): return run_all_models(load_journeys())
@st.cache_data
def load_weekly_trend():   return generate_weekly_trend()
@st.cache_data
def load_filters():        return [{"value": k, "label": v} for k, v in CONDITION_LABELS.items()]

# ── Helpers ───────────────────────────────────────────────────────────────────
def compliance_strip(msg="Aggregated cohort · HIPAA Safe Harbor · No PHI · Timestamps rounded to weekly grain"):
    st.markdown(f'<div style="display:flex;align-items:center;gap:8px;padding:7px 14px;border-radius:8px;background:rgba(45,212,191,0.05);border:1px solid rgba(45,212,191,0.2);margin-bottom:18px;"><span style="color:#2dd4bf;">🔒</span><span style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;color:#4a6080;">{msg}</span></div>', unsafe_allow_html=True)

def section_header(title, sub=""):
    st.markdown(f'<h2 style="font-family:\'DM Serif Display\',serif;font-size:1.8rem;color:#e8f0fe;margin:0 0 4px 0;">{title}</h2>{"" if not sub else f\'<p style="font-size:13px;color:#94a3b8;margin:0 0 20px 0;">{sub}</p>"}', unsafe_allow_html=True)

def ch_color_scale():
    """Altair color scale for channels."""
    return alt.Scale(
        domain=list(CHANNEL_LABELS.keys()),
        range=[CHANNEL_COLORS.get(c, TEAL) for c in CHANNEL_LABELS.keys()]
    )

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:0 0 16px 0;border-bottom:1px solid rgba(45,212,191,0.1);margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:34px;height:34px;background:linear-gradient(135deg,#14b8a6,#2dd4bf);border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:18px;">⚕</div>
            <div>
                <div style="font-family:'DM Serif Display',serif;font-size:16px;color:#e8f0fe;line-height:1.2;">PathIQ</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#4a6080;letter-spacing:0.1em;text-transform:uppercase;">Patient Journey Analytics</div>
            </div>
        </div>
    </div>
    <div style="display:flex;align-items:center;gap:8px;padding:8px 12px;border-radius:8px;background:rgba(74,222,128,0.08);border:1px solid rgba(74,222,128,0.25);margin-bottom:20px;">
        <div style="width:8px;height:8px;border-radius:50%;background:#4ade80;flex-shrink:0;"></div>
        <div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#4ade80;font-weight:600;">HIPAA COMPLIANT</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#4a6080;">PHI in pipeline: NONE ✓</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("Page", ["📊 Overview","🗺️ Patient Journey","🎯 Attribution","📡 Channels","🛡️ Compliance"], label_visibility="collapsed")

    st.markdown("---")
    st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;color:#4a6080;line-height:1.6;">⚠ Synthetic data only.<br>No PHI. De-identified per<br>HIPAA §164.514(b) Safe Harbor.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    section_header("Patient Journey Overview", "Multi-touch attribution analytics · Synthetic data prototype")
    compliance_strip()
    st.info("**Prototype Disclaimer:** All data is 100% synthetic. Demonstrates a HIPAA-compliant analytics architecture for healthcare marketing MTA. No real patient data is used or stored.")

    funnel = generate_funnel_data()
    stages = {s["stage"]: s["count"] for s in funnel["stages"]}
    journeys = load_journeys()
    avg_touches = sum(j["n_touches"] for j in journeys) / len(journeys)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Journeys Analyzed",        f"{funnel['total_journeys']:,}")
    k2.metric("Appointment Conversion",   f"{funnel['conversion_rate']}%")
    k3.metric("Avg Touchpoints to Book",  f"{avg_touches:.1f}")
    k4.metric("Positive Outcomes",        f"{stages.get('outcome',0):,}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([2, 1])

    with col_a:
        df_trend = pd.DataFrame(load_weekly_trend())
        df_trend["week"] = pd.to_datetime(df_trend["week"])
        df_melt = df_trend.melt("week", ["journeys", "appointments"], var_name="Series", value_name="Count")
        color_map = {"journeys": TEAL, "appointments": GREEN}
        chart_trend = (
            alt.Chart(df_melt, title="Journey Volume — 26-Week Trend")
            .mark_area(opacity=0.3, interpolate="monotone")
            .encode(
                x=alt.X("week:T", axis=alt.Axis(format="%b %d", labelAngle=-30)),
                y=alt.Y("Count:Q"),
                color=alt.Color("Series:N", scale=alt.Scale(domain=list(color_map.keys()), range=list(color_map.values()))),
            )
            .properties(height=200)
        )
        line_trend = chart_trend.mark_line(interpolate="monotone", strokeWidth=2)
        st.altair_chart((chart_trend + line_trend).configure_view(strokeOpacity=0), use_container_width=True)

    with col_b:
        ch_data = load_channel_perf()
        df_pie = pd.DataFrame([{"Channel": c["channel_label"], "Conversions": c["conversions"], "color": CHANNEL_COLORS.get(c["channel"], TEAL)} for c in ch_data[:6]])
        chart_pie = (
            alt.Chart(df_pie, title="Channel Mix")
            .mark_arc(innerRadius=45)
            .encode(
                theta=alt.Theta("Conversions:Q"),
                color=alt.Color("Channel:N", scale=alt.Scale(domain=df_pie["Channel"].tolist(), range=df_pie["color"].tolist())),
                tooltip=["Channel", "Conversions"],
            )
            .properties(height=200)
        )
        st.altair_chart(chart_pie.configure_view(strokeOpacity=0), use_container_width=True)

    df_funnel = pd.DataFrame(funnel["stages"])
    df_funnel["color"] = STAGE_COLORS
    chart_funnel = (
        alt.Chart(df_funnel, title="Journey Funnel — All Conditions")
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("label:N", sort=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("count:Q"),
            color=alt.Color("label:N", scale=alt.Scale(domain=df_funnel["label"].tolist(), range=STAGE_COLORS), legend=None),
            tooltip=["label", "count"],
        )
        .properties(height=180)
    )
    st.altair_chart(chart_funnel.configure_view(strokeOpacity=0), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════
# PAGE: PATIENT JOURNEY
# ═══════════════════════════════════════════════════════════════════════
elif page == "🗺️ Patient Journey":
    section_header("Patient Journey Map", "Funnel flow from awareness through appointment booking and outcomes")
    compliance_strip()

    filters = load_filters()
    cond_options = ["All Conditions"] + [f["label"] for f in filters]
    cond_values  = [None] + [f["value"] for f in filters]
    selected_label = st.selectbox("Condition Area", cond_options)
    condition = cond_values[cond_options.index(selected_label)]

    funnel = generate_funnel_data(condition_filter=condition)
    stages = funnel["stages"]
    total  = stages[0]["count"] or 1

    st.markdown(f'<div style="padding:10px 16px;border-radius:8px;background:rgba(45,212,191,0.05);border:1px solid rgba(45,212,191,0.2);margin-bottom:16px;"><span style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;color:#2dd4bf;">Conversion rate: <strong>{funnel["conversion_rate"]}%</strong> · De-id: <strong>Safe Harbor</strong> · Grain: <strong>Weekly Cohort</strong></span></div>', unsafe_allow_html=True)

    cols = st.columns(5)
    for i, (s, col) in enumerate(zip(stages, cols)):
        pct = round(s["count"] / total * 100, 1)
        with col:
            st.markdown(f'<div style="text-align:center;padding:20px 12px;border-radius:12px;background:linear-gradient(180deg,{STAGE_COLORS[i]}18,{STAGE_COLORS[i]}08);border:1px solid {STAGE_COLORS[i]}40;"><div style="font-family:\'IBM Plex Mono\',monospace;font-size:1.4rem;font-weight:700;color:{STAGE_COLORS[i]};line-height:1;">{s["count"]:,}</div><div style="font-size:10px;font-weight:700;color:{STAGE_COLORS[i]};letter-spacing:0.08em;text-transform:uppercase;margin-top:8px;">{s["label"]}</div><div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;color:#4a6080;margin-top:4px;">{pct}%</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    df_f = pd.DataFrame(stages)
    chart_f = (
        alt.Chart(df_f, title="Funnel Stage Distribution")
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("label:N", sort=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("count:Q"),
            color=alt.Color("label:N", scale=alt.Scale(domain=df_f["label"].tolist(), range=STAGE_COLORS), legend=None),
            tooltip=["label", "count"],
        )
        .properties(height=180)
    )
    st.altair_chart(chart_f.configure_view(strokeOpacity=0), use_container_width=True)

    flows = generate_channel_funnel(condition_filter=condition)
    ch_agg: dict = {}
    for row in flows:
        ch = row["channel"]
        if ch not in ch_agg:
            ch_agg[ch] = {"Channel": row["channel_label"], "Type": "🟡 Modeled" if row["walled_garden"] else "🔵 Observed", "Awareness": 0, "Interest": 0, "Intent": 0, "Booked": 0}
        for k in ["awareness","interest","intent"]:
            ch_agg[ch][k.title()] += row[k]
        ch_agg[ch]["Booked"] += row["appointment_booked"]
    df_ch = pd.DataFrame(list(ch_agg.values()))
    df_ch["Conv %"] = (df_ch["Booked"] / df_ch["Awareness"] * 100).round(1).astype(str) + "%"
    st.dataframe(df_ch.sort_values("Booked", ascending=False).reset_index(drop=True), use_container_width=True, hide_index=True)
    st.warning("**Walled Garden Channels (Social, CTV):** Direct pixel-level measurement is restricted. These use **modeled attribution** only. Under WA My Health MY Data Act (2024), health-intent targeting requires affirmative opt-in consent.")


# ═══════════════════════════════════════════════════════════════════════
# PAGE: ATTRIBUTION
# ═══════════════════════════════════════════════════════════════════════
elif page == "🎯 Attribution":
    section_header("Multi-Touch Attribution", "Compare 5 MTA models · De-identified journey sequences only · No PHI")
    compliance_strip("Anonymized journey hashes · No PHI · Credits sum to 1.00")

    journeys = load_journeys()
    all_results = load_mta_comparison()

    col_sel, col_main = st.columns([1, 2])

    with col_sel:
        st.markdown("#### Select MTA Model")
        model_choice = st.radio("Model", options=ALL_MODELS, format_func=lambda m: MODEL_LABELS[m], index=4, label_visibility="collapsed")
        color = MODEL_COLORS[model_choice]
        st.markdown(f'<div style="padding:14px;border-radius:10px;background:rgba(12,30,61,0.8);border:1px solid {color}40;margin-top:10px;"><div style="font-size:11px;color:{color};font-weight:600;margin-bottom:8px;font-family:\'IBM Plex Mono\',monospace;">DESCRIPTION</div><div style="font-size:12px;color:#94a3b8;line-height:1.6;">{MODEL_DESCRIPTIONS[model_choice]}</div><div style="font-size:10px;color:#fbbf24;font-weight:600;margin-top:12px;margin-bottom:6px;font-family:\'IBM Plex Mono\',monospace;">HEALTHCARE CONTEXT</div><div style="font-size:11px;color:#94a3b8;line-height:1.6;">{HEALTHCARE_CONTEXT[model_choice]}</div></div>', unsafe_allow_html=True)

    with col_main:
        result = run_model(model_choice, journeys)
        credits = result["credits"]
        st.markdown(f"#### {MODEL_LABELS[model_choice]} — Channel Credits")

        rows = sorted([{"Channel": CHANNEL_LABELS.get(ch, ch), "channel": ch, "Credit %": round(v*100,1)} for ch,v in credits.items()], key=lambda x: x["Credit %"], reverse=True)
        for row in rows:
            c = CHANNEL_COLORS.get(row["channel"], TEAL)
            st.markdown(f'<div style="margin-bottom:10px;"><div style="display:flex;justify-content:space-between;margin-bottom:4px;"><span style="font-size:12px;color:#94a3b8;">{row["Channel"]}</span><span style="font-family:\'IBM Plex Mono\',monospace;font-size:12px;color:{c};">{row["Credit %"]}%</span></div><div style="height:6px;border-radius:3px;background:rgba(45,212,191,0.1);overflow:hidden;"><div style="height:100%;width:{row["Credit %"]}%;border-radius:3px;background:linear-gradient(90deg,{c}60,{c});"></div></div></div>', unsafe_allow_html=True)

    st.markdown("### All Models — Side-by-Side Comparison")
    matrix = []
    for r in all_results:
        for ch, cred in r["credits"].items():
            matrix.append({"Model": MODEL_LABELS[r["model"]], "Channel": CHANNEL_LABELS.get(ch, ch), "Credit %": round(cred*100,1), "color": MODEL_COLORS[r["model"]]})
    df_cmp = pd.DataFrame(matrix)

    chart_cmp = (
        alt.Chart(df_cmp, title="Attribution Credit by Channel — All Models")
        .mark_bar()
        .encode(
            x=alt.X("Channel:N", axis=alt.Axis(labelAngle=-20)),
            y=alt.Y("Credit %:Q"),
            color=alt.Color("Model:N", scale=alt.Scale(domain=[MODEL_LABELS[m] for m in ALL_MODELS], range=[MODEL_COLORS[m] for m in ALL_MODELS])),
            xOffset="Model:N",
            tooltip=["Model","Channel","Credit %"],
        )
        .properties(height=260)
    )
    st.altair_chart(chart_cmp.configure_view(strokeOpacity=0), use_container_width=True)
    st.info("**Interpretation:** Large divergence on HCP Referral between First Touch and Last Touch indicates this channel plays a strong **closing** role. Data-Driven (Shapley) is recommended for budget allocation — it measures true marginal channel contribution.")


# ═══════════════════════════════════════════════════════════════════════
# PAGE: CHANNELS
# ═══════════════════════════════════════════════════════════════════════
elif page == "📡 Channels":
    section_header("Channel Performance", "Aggregated KPIs · Walled garden channels use modeled attribution")
    compliance_strip("Aggregated channel data · No individual patient records · No PHI")

    ch_data = load_channel_perf()
    show_walled = st.toggle("Show Walled Garden Channels", value=True)
    if not show_walled:
        ch_data = [c for c in ch_data if not c["walled_garden"]]

    df_bar = pd.DataFrame([{"Channel": c["channel_label"], "channel_key": c["channel"], "Appointments": c["conversions"]} for c in ch_data])
    chart_bar = (
        alt.Chart(df_bar, title="Appointments by Channel")
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("Channel:N", sort="-y", axis=alt.Axis(labelAngle=-20)),
            y=alt.Y("Appointments:Q"),
            color=alt.Color("Channel:N", scale=alt.Scale(domain=df_bar["Channel"].tolist(), range=[CHANNEL_COLORS.get(c["channel"], TEAL) for c in ch_data]), legend=None),
            tooltip=["Channel","Appointments"],
        )
        .properties(height=200)
    )
    st.altair_chart(chart_bar.configure_view(strokeOpacity=0), use_container_width=True)

    df_table = pd.DataFrame([{
        "Channel":      c["channel_label"],
        "Type":         "🟡 Modeled" if c["walled_garden"] else "🔵 Observed",
        "Impressions":  f"{c['impressions']//1000:,}k",
        "Clicks":       f"{c['clicks']:,}",
        "CTR":          f"{c['ctr']}%",
        "Appointments": c["conversions"],
        "Spend":        f"${c['cost']//1000:,}k",
        "CPA":          f"${c['cpa']:.0f}",
    } for c in ch_data])
    st.dataframe(df_table, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    c1.warning("**Pharma / Medical Device:** OPDP/DDMAC guidelines apply to all DTC digital content. Fair balance requirements must be met. Off-label promotion is prohibited.")
    c2.info("**HCP Referral:** Tracked via NPI-level aggregation — not patient-level. BAA required with CRM vendors. Sunshine Act reporting obligations apply.")


# ═══════════════════════════════════════════════════════════════════════
# PAGE: COMPLIANCE
# ═══════════════════════════════════════════════════════════════════════
elif page == "🛡️ Compliance":
    section_header("Privacy & Compliance Posture", "De-identification · Consent · Regulatory framework · Audit controls")

    st.markdown('<div style="display:flex;align-items:center;gap:12px;padding:14px 20px;border-radius:10px;background:rgba(74,222,128,0.08);border:1px solid rgba(74,222,128,0.3);margin-bottom:24px;"><div style="width:12px;height:12px;border-radius:50%;background:#4ade80;flex-shrink:0;"></div><div><div style="font-family:\'IBM Plex Mono\',monospace;font-size:13px;color:#4ade80;font-weight:700;">COMPLIANT — All Frameworks</div><div style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;color:#4a6080;">HIPAA Safe Harbor · WA MHMD · CA CMIA · TX THIPA · FTC HBNR · PHI in pipeline: NONE</div></div></div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("De-ID Method",     "Safe Harbor",  "§164.514(b)(2)")
    c2.metric("PHI in Analytics", "None",         "Always excluded")
    c3.metric("Audit Controls",   "Active",       "HIPAA §164.312(b)")
    c4.metric("BAA Required",     "Yes",          "All vendors")

    st.markdown("<br>", unsafe_allow_html=True)
    tab_lineage, tab_consent, tab_laws, tab_audit = st.tabs(["DATA LINEAGE","CONSENT STATUS","REGULATORY MATRIX","AUDIT LOG"])

    with tab_lineage:
        st.markdown("#### PHI Never Enters the Analytics Layer")
        for label, sub, phi_label, phi_color, bg, border in [
            ("Raw Source Data",           "EMR / CRM / Ad Platforms",                         "CONTAINS PHI", "#f87171", "rgba(248,113,113,0.08)", "rgba(248,113,113,0.3)"),
            ("De-Identification Layer",   "Safe Harbor: 18 identifiers removed",              "PHI STRIPPED",  "#fbbf24", "rgba(251,191,36,0.08)",  "rgba(251,191,36,0.3)"),
            ("Aggregation Engine",        "Cohort grouping · Weekly grain · Min. 11 per cell","NO PHI",        "#4ade80", "rgba(74,222,128,0.06)",  "rgba(74,222,128,0.25)"),
            ("Analytics Layer (This App)","Channel MTA · Journey funnels · Outcomes",         "NO PHI",        "#4ade80", "rgba(74,222,128,0.06)",  "rgba(74,222,128,0.3)"),
        ]:
            st.markdown(f'<div style="padding:14px 18px;border-radius:10px;background:{bg};border:1px solid {border};margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;"><div><div style="font-size:13px;font-weight:600;color:#e8f0fe;">{label}</div><div style="font-size:11px;color:#4a6080;margin-top:3px;">{sub}</div></div><span style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;color:{phi_color};border:1px solid {phi_color}50;padding:3px 8px;border-radius:4px;">{phi_label}</span></div>', unsafe_allow_html=True)

    with tab_consent:
        consent = load_consent()
        st.markdown(f"**Framework:** {consent['consent_framework']}")
        st.error(f"⛔ Opted-out cohorts ({consent['opted_out']:,} records) are **automatically excluded** from all analytics pipelines.")

        df_consent = pd.DataFrame([
            {"Type": "Full Consent",           "Count": consent["full_consent"],   "color": GREEN},
            {"Type": "Limited Consent",        "Count": consent["limited_consent"],"color": AMBER},
            {"Type": "Opted Out (Excluded)",   "Count": consent["opted_out"],      "color": RED},
        ])
        chart_consent = (
            alt.Chart(df_consent, title="Consent Status")
            .mark_arc(innerRadius=50)
            .encode(
                theta=alt.Theta("Count:Q"),
                color=alt.Color("Type:N", scale=alt.Scale(domain=df_consent["Type"].tolist(), range=df_consent["color"].tolist())),
                tooltip=["Type","Count"],
            )
            .properties(height=220)
        )
        col_p, col_s = st.columns([1,1])
        with col_p:
            st.altair_chart(chart_consent.configure_view(strokeOpacity=0), use_container_width=True)
        with col_s:
            for _, row in df_consent.iterrows():
                pct = round(row["Count"] / consent["total_cohort_size"] * 100, 1)
                st.markdown(f'<div style="padding:12px 16px;border-radius:8px;background:rgba(12,30,61,0.8);border:1px solid rgba(45,212,191,0.1);margin-bottom:10px;"><div style="font-size:12px;color:#94a3b8;">{row["Type"]}</div><div style="font-family:\'IBM Plex Mono\',monospace;font-size:1.2rem;color:{row["color"]};font-weight:600;">{int(row["Count"]):,} <span style="font-size:11px;color:#4a6080;">({pct}%)</span></div></div>', unsafe_allow_html=True)

    with tab_laws:
        laws = load_laws()
        df_laws = pd.DataFrame([{
            "Law": l["law"], "Jurisdiction": l["jurisdiction"],
            "Applies To": l["applies_to"], "Key Requirement": l["key_requirement"],
            "Effective": l["effective"], "Status": "✅ Active",
        } for l in laws])
        st.dataframe(df_laws, use_container_width=True, hide_index=True)
        st.info("**Strictest standard applies:** When state law is stricter than HIPAA (e.g., WA My Health MY Data Act), the state standard governs.")

    with tab_audit:
        audit = load_audit_log()
        st.markdown(f"**{len(audit)} entries** · HIPAA §164.312(b) · Retention: 6 years · PHI accessed: **NEVER**")
        PAGE_SZ = 10
        total_pages = (len(audit) - 1) // PAGE_SZ + 1
        p = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1) - 1
        df_audit = pd.DataFrame([{
            "Log ID": e["log_id"], "Timestamp": e["timestamp"][:16].replace("T"," "),
            "User": e["user_id"], "Query": e["action"],
            "Data Category": e["data_category"], "Legal Basis": e["legal_basis"], "PHI?": "❌ NONE",
        } for e in audit])
        st.dataframe(df_audit.iloc[p*PAGE_SZ:(p+1)*PAGE_SZ], use_container_width=True, hide_index=True)
        st.caption(f"Page {p+1} of {total_pages}")

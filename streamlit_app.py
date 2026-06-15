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
import plotly.graph_objects as go
import plotly.express as px
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
    GEO_REGIONS,
    CHANNEL_LABELS,
)
from backend.services.mta import run_model, run_all_models, ALL_MODELS, MODEL_LABELS, MODEL_DESCRIPTIONS, HEALTHCARE_CONTEXT

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY   = "#040d1a"
TEAL   = "#2dd4bf"
TEAL_D = "#14b8a6"
AMBER  = "#fbbf24"
GREEN  = "#4ade80"
RED    = "#f87171"
MUTED  = "#94a3b8"
TEXT   = "#e8f0fe"
SURF1  = "#071228"
SURF2  = "#0c1e3d"
BORDER = "rgba(45,212,191,0.2)"

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

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PathIQ · Patient Journey Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Password gate ─────────────────────────────────────────────────────────────
def _check_password() -> bool:
    """Returns True once the correct password has been entered."""
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

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        pwd = st.text_input("Password", type="password", placeholder="Enter access password")
        submitted = st.button("Access →", use_container_width=True)

        if submitted or pwd:
            correct = st.secrets.get("APP_PASSWORD", "")
            if pwd == correct and correct != "":
                st.session_state["_authenticated"] = True
                st.rerun()
            elif pwd:
                st.error("Incorrect password.")

        st.markdown("""
        <div style="text-align:center;margin-top:20px;font-family:'IBM Plex Mono',monospace;
            font-size:9px;color:#4a6080;">
            🔒 HIPAA-Safe Prototype · Synthetic Data Only
        </div>
        """, unsafe_allow_html=True)

    return False

if not _check_password():
    st.stop()

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=IBM+Plex+Mono:wght@300;400;500;600&family=Instrument+Sans:ital,wght@0,400;0,500;0,600;0,700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Instrument Sans', sans-serif;
}

/* Main background */
.stApp {
    background: #040d1a;
    background-image:
        linear-gradient(rgba(45,212,191,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(45,212,191,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071228 0%, #040d1a 100%);
    border-right: 1px solid rgba(45,212,191,0.12);
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #e8f0fe !important; }

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(12,30,61,0.95) 0%, rgba(7,18,40,0.95) 100%);
    border: 1px solid rgba(45,212,191,0.15);
    border-radius: 12px;
    padding: 20px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #2dd4bf !important;
    font-size: 2rem !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Instrument Sans', sans-serif !important;
    color: #94a3b8 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

/* Headers */
h1 { font-family: 'DM Serif Display', serif !important; color: #e8f0fe !important; }
h2, h3 { font-family: 'DM Serif Display', serif !important; color: #e8f0fe !important; }

/* Dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(45,212,191,0.15) !important;
    border-radius: 8px !important;
}

/* Select boxes */
[data-testid="stSelectbox"] > div > div {
    background: rgba(12,30,61,0.9) !important;
    border: 1px solid rgba(45,212,191,0.25) !important;
    color: #e8f0fe !important;
    border-radius: 8px !important;
}

/* Radio buttons */
[data-testid="stRadio"] > div { gap: 8px; }
[data-testid="stRadio"] label {
    background: rgba(12,30,61,0.6) !important;
    border: 1px solid rgba(45,212,191,0.15) !important;
    border-radius: 8px !important;
    padding: 8px 14px !important;
    color: #94a3b8 !important;
    font-size: 13px !important;
    transition: all 0.15s ease;
}

/* Info / warning boxes */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    border-left-width: 3px !important;
}

/* Tabs */
[data-testid="stTabs"] button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    color: #4a6080 !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #2dd4bf !important;
    border-bottom-color: #2dd4bf !important;
}

/* Dividers */
hr { border-color: rgba(45,212,191,0.12) !important; }

/* General text */
p, span, li { color: #94a3b8; }
strong { color: #e8f0fe !important; }

/* Plotly chart backgrounds already set per chart */
</style>
""", unsafe_allow_html=True)


# ── Cached data loaders ───────────────────────────────────────────────────────

@st.cache_data
def load_journeys():
    return generate_touchpoint_sequences(2000)

@st.cache_data
def load_channel_perf():
    return generate_channel_performance()

@st.cache_data
def load_audit_log():
    return generate_audit_log()

@st.cache_data
def load_consent():
    return generate_consent_summary()

@st.cache_data
def load_laws():
    return generate_state_law_matrix()

@st.cache_data
def load_filters():
    return [{"value": k, "label": v} for k, v in CONDITION_LABELS.items()]

@st.cache_data
def load_mta_comparison():
    journeys = load_journeys()
    return run_all_models(journeys)

@st.cache_data
def load_weekly_trend():
    return generate_weekly_trend()


# ── Plotly chart theme ────────────────────────────────────────────────────────

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Mono, monospace", color="#4a6080", size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis=dict(gridcolor="rgba(45,212,191,0.06)", linecolor="rgba(45,212,191,0.1)", zerolinecolor="rgba(45,212,191,0.1)"),
    yaxis=dict(gridcolor="rgba(45,212,191,0.06)", linecolor="rgba(45,212,191,0.1)", zerolinecolor="rgba(45,212,191,0.1)"),
)

def apply_theme(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


# ── Compliance strip ──────────────────────────────────────────────────────────

def compliance_strip(msg="Aggregated cohort · HIPAA Safe Harbor · No PHI · Timestamps rounded to weekly grain"):
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;padding:7px 14px;border-radius:8px;
        background:rgba(45,212,191,0.05);border:1px solid rgba(45,212,191,0.2);margin-bottom:18px;">
        <span style="color:#2dd4bf;font-size:12px;">🔒</span>
        <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#4a6080;letter-spacing:0.04em;">{msg}</span>
    </div>
    """, unsafe_allow_html=True)


def card_html(content: str):
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(12,30,61,0.95) 0%,rgba(7,18,40,0.95) 100%);
        border:1px solid rgba(45,212,191,0.15);border-radius:12px;padding:20px;margin-bottom:12px;">
        {content}
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, sub: str = ""):
    st.markdown(f"""
    <h2 style="font-family:'DM Serif Display',serif;font-size:1.8rem;color:#e8f0fe;margin:0 0 4px 0;">{title}</h2>
    {"" if not sub else f'<p style="font-size:13px;color:#94a3b8;margin:0 0 20px 0;">{sub}</p>'}
    """, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    # Logo
    st.markdown("""
    <div style="padding:0 0 16px 0;border-bottom:1px solid rgba(45,212,191,0.1);margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="width:34px;height:34px;background:linear-gradient(135deg,#14b8a6,#2dd4bf);
                border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:18px;">⚕</div>
            <div>
                <div style="font-family:'DM Serif Display',serif;font-size:16px;color:#e8f0fe;line-height:1.2;">PathIQ</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#4a6080;
                    letter-spacing:0.1em;text-transform:uppercase;">Patient Journey Analytics</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # HIPAA status badge
    st.markdown("""
    <div style="display:flex;align-items:center;gap:8px;padding:8px 12px;border-radius:8px;
        background:rgba(74,222,128,0.08);border:1px solid rgba(74,222,128,0.25);margin-bottom:20px;">
        <div style="width:8px;height:8px;border-radius:50%;background:#4ade80;
            box-shadow:0 0 0 3px rgba(74,222,128,0.2);animation:pulse 2s infinite;flex-shrink:0;"></div>
        <div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#4ade80;font-weight:600;">HIPAA COMPLIANT</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#4a6080;">PHI in pipeline: NONE ✓</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;color:#4a6080;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:8px;">Navigation</div>', unsafe_allow_html=True)

    page = st.radio(
        "Page",
        ["📊 Overview", "🗺️ Patient Journey", "🎯 Attribution", "📡 Channels", "🛡️ Compliance"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("""
    <div style="display:flex;gap:8px;align-items:flex-start;padding:10px 0;">
        <span style="color:#fbbf24;font-size:11px;flex-shrink:0;">⚠</span>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:#4a6080;line-height:1.6;">
            Synthetic data only.<br>No PHI. De-identified per<br>HIPAA §164.514(b) Safe Harbor.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════

if page == "📊 Overview":
    section_header("Patient Journey Overview", "Multi-touch attribution analytics · Synthetic data prototype")
    compliance_strip()

    st.info("**Prototype Disclaimer:** All data is 100% synthetic. This demonstrates a HIPAA-compliant analytics architecture for healthcare marketing MTA. No real patient data is used or stored.")

    # KPIs
    funnel = generate_funnel_data()
    stages = {s["stage"]: s["count"] for s in funnel["stages"]}
    journeys = load_journeys()
    avg_touches = sum(j["n_touches"] for j in journeys) / len(journeys)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Journeys Analyzed", f"{funnel['total_journeys']:,}", help="Total synthetic cohort journeys — aggregated, no individual records")
    k2.metric("Appointment Conversion", f"{funnel['conversion_rate']}%", help="Awareness → Appointment Booked")
    k3.metric("Avg Touchpoints to Book", f"{avg_touches:.1f}", help="Mean channel touchpoints across journeys before booking")
    k4.metric("Positive Outcomes", f"{stages.get('outcome', 0):,}", help="Journeys reaching recorded positive outcome")

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([2, 1])

    with col_a:
        # Weekly trend
        trend_data = load_weekly_trend()
        df_trend = pd.DataFrame(trend_data)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=df_trend["week"], y=df_trend["journeys"],
            name="Journeys", mode="lines", line=dict(color=TEAL, width=2),
            fill="tozeroy", fillcolor="rgba(45,212,191,0.08)",
        ))
        fig_trend.add_trace(go.Scatter(
            x=df_trend["week"], y=df_trend["appointments"],
            name="Appointments", mode="lines", line=dict(color=GREEN, width=2),
            fill="tozeroy", fillcolor="rgba(74,222,128,0.06)",
        ))
        fig_trend.update_layout(title="Journey Volume — 26-Week Trend", legend=dict(orientation="h", y=1.12), **PLOTLY_LAYOUT)
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_b:
        # Channel mix
        ch_data = load_channel_perf()
        labels = [c["channel_label"] for c in ch_data[:7]]
        values = [c["conversions"] for c in ch_data[:7]]
        colors = [CHANNEL_COLORS.get(c["channel"], TEAL) for c in ch_data[:7]]
        fig_pie = go.Figure(go.Pie(
            labels=labels, values=values, hole=0.55,
            marker=dict(colors=colors, line=dict(color=NAVY, width=2)),
            textinfo="none",
        ))
        fig_pie.update_layout(title="Channel Mix", showlegend=True,
            legend=dict(font=dict(size=9, family="IBM Plex Mono"), orientation="v"),
            **PLOTLY_LAYOUT)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Funnel bar
    df_funnel = pd.DataFrame(funnel["stages"])
    stage_colors = ["#2dd4bf", "#14b8a6", "#0d9488", "#0f766e", "#115e59"]
    fig_funnel = go.Figure()
    for i, row in df_funnel.iterrows():
        fig_funnel.add_trace(go.Bar(
            x=[row["label"]], y=[row["count"]],
            marker_color=stage_colors[i], name=row["label"],
            showlegend=False,
        ))
    fig_funnel.update_traces(marker_line_width=0)
    fig_funnel.update_layout(title="Journey Funnel — All Conditions", barmode="group", **PLOTLY_LAYOUT)
    st.plotly_chart(fig_funnel, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════
# PAGE: PATIENT JOURNEY
# ═══════════════════════════════════════════════════════════════════════

elif page == "🗺️ Patient Journey":
    section_header("Patient Journey Map", "Funnel flow from awareness through appointment booking and outcomes")
    compliance_strip()

    filters = load_filters()
    cond_options = ["All Conditions"] + [f["label"] for f in filters]
    cond_values  = [None] + [f["value"] for f in filters]

    col_f1, col_f2 = st.columns([2, 3])
    with col_f1:
        selected_label = st.selectbox("Condition Area", cond_options)
        condition = cond_values[cond_options.index(selected_label)]

    funnel = generate_funnel_data(condition_filter=condition)
    stages = funnel["stages"]
    total  = stages[0]["count"] or 1

    with col_f2:
        st.markdown(f"""
        <div style="padding:12px 18px;border-radius:8px;background:rgba(45,212,191,0.05);
            border:1px solid rgba(45,212,191,0.2);margin-top:28px;">
            <span style="font-family:'IBM Plex Mono',monospace;font-size:11px;color:#2dd4bf;">
                Conversion rate: <strong>{funnel['conversion_rate']}%</strong> &nbsp;·&nbsp;
                De-id: <strong>{funnel['de_id_method'].replace('_',' ').title()}</strong> &nbsp;·&nbsp;
                Grain: <strong>{funnel['data_grain'].replace('_',' ').title()}</strong>
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Funnel stage cards
    stage_colors = ["#2dd4bf", "#14b8a6", "#0d9488", "#0f766e", "#115e59"]
    cols = st.columns(5)
    for i, (s, col) in enumerate(zip(stages, cols)):
        pct = round(s["count"] / total * 100, 1)
        with col:
            st.markdown(f"""
            <div style="text-align:center;padding:20px 12px;border-radius:12px;
                background:linear-gradient(180deg,{stage_colors[i]}18,{stage_colors[i]}08);
                border:1px solid {stage_colors[i]}40;">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:1.5rem;
                    font-weight:700;color:{stage_colors[i]};line-height:1;">{s['count']:,}</div>
                <div style="font-size:10px;font-weight:700;color:{stage_colors[i]};
                    letter-spacing:0.08em;text-transform:uppercase;margin-top:8px;">{s['label']}</div>
                <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#4a6080;margin-top:4px;">{pct}%</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Funnel bar chart
    df_f = pd.DataFrame(stages)
    fig_f = go.Figure()
    for i, row in df_f.iterrows():
        fig_f.add_trace(go.Bar(x=[row["label"]], y=[row["count"]],
            marker_color=stage_colors[i], showlegend=False,
            hovertemplate=f"<b>{row['label']}</b><br>Count: {row['count']:,}<br>{round(row['count']/total*100,1)}% of total<extra></extra>"))
    fig_f.update_layout(title="Funnel Stage Distribution", **PLOTLY_LAYOUT)
    st.plotly_chart(fig_f, use_container_width=True)

    # Channel table
    st.markdown("### Channel → Stage Breakdown")
    flows = generate_channel_funnel(condition_filter=condition)
    ch_agg: dict = {}
    for row in flows:
        ch = row["channel"]
        if ch not in ch_agg:
            ch_agg[ch] = {"Channel": row["channel_label"], "Type": "🟡 Modeled" if row["walled_garden"] else "🔵 Observed",
                          "Awareness": 0, "Interest": 0, "Intent": 0, "Booked": 0}
        ch_agg[ch]["Awareness"] += row["awareness"]
        ch_agg[ch]["Interest"]  += row["interest"]
        ch_agg[ch]["Intent"]    += row["intent"]
        ch_agg[ch]["Booked"]    += row["appointment_booked"]

    df_ch = pd.DataFrame(list(ch_agg.values()))
    df_ch["Conv %"] = (df_ch["Booked"] / df_ch["Awareness"] * 100).round(1).astype(str) + "%"
    df_ch = df_ch.sort_values("Booked", ascending=False).reset_index(drop=True)
    st.dataframe(df_ch, use_container_width=True, hide_index=True)

    st.warning("**Walled Garden Channels (Social, CTV):** Direct pixel-level measurement restricted under HIPAA marketing rules and platform policies. These use **modeled attribution** only. Under WA My Health MY Data Act (2024), health-intent targeting requires affirmative opt-in consent.")


# ═══════════════════════════════════════════════════════════════════════
# PAGE: ATTRIBUTION
# ═══════════════════════════════════════════════════════════════════════

elif page == "🎯 Attribution":
    section_header("Multi-Touch Attribution", "Compare 5 MTA models across channels · De-identified journey sequences only")
    compliance_strip("Anonymized journey hashes · No PHI · Credits sum to 1.00")

    journeys = load_journeys()
    all_results = load_mta_comparison()

    col_sel, col_main = st.columns([1, 2])

    with col_sel:
        st.markdown("#### Select MTA Model")
        model_choice = st.radio(
            "Model",
            options=ALL_MODELS,
            format_func=lambda m: MODEL_LABELS[m],
            index=4,
            label_visibility="collapsed",
        )

        color = MODEL_COLORS[model_choice]
        st.markdown(f"""
        <div style="padding:14px;border-radius:10px;background:rgba(12,30,61,0.8);
            border:1px solid {color}40;margin-top:10px;">
            <div style="font-size:11px;color:{color};font-weight:600;margin-bottom:8px;
                font-family:'IBM Plex Mono',monospace;letter-spacing:0.05em;">DESCRIPTION</div>
            <div style="font-size:12px;color:#94a3b8;line-height:1.6;">{MODEL_DESCRIPTIONS[model_choice]}</div>
            <div style="font-size:10px;color:#fbbf24;font-weight:600;margin-top:12px;margin-bottom:6px;
                font-family:'IBM Plex Mono',monospace;letter-spacing:0.05em;">HEALTHCARE CONTEXT</div>
            <div style="font-size:11px;color:#94a3b8;line-height:1.6;">{HEALTHCARE_CONTEXT[model_choice]}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_main:
        # Single model result
        result = run_model(model_choice, journeys)
        credits = result["credits"]
        credit_sum = round(sum(credits.values()), 4)

        st.markdown(f"#### {MODEL_LABELS[model_choice]} — Channel Credits")
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
            <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#4ade80;
                background:rgba(74,222,128,0.08);border:1px solid rgba(74,222,128,0.2);
                padding:3px 8px;border-radius:6px;">Credits sum: {'✓ 1.00' if credit_sum == 1.0 else f'~{credit_sum}'}</span>
            <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#4a6080;">
                PHI used: {'❌ YES' if result['phi_used'] else '✅ NONE'}</span>
        </div>
        """, unsafe_allow_html=True)

        sorted_ch = sorted(credits.items(), key=lambda x: x[1], reverse=True)
        for ch, cred in sorted_ch:
            label = CHANNEL_LABELS.get(ch, ch)
            pct   = round(cred * 100, 1)
            bar_color = CHANNEL_COLORS.get(ch, TEAL)
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                    <span style="font-size:12px;color:#94a3b8;">{label}</span>
                    <span style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:{bar_color};">{pct}%</span>
                </div>
                <div style="height:6px;border-radius:3px;background:rgba(45,212,191,0.1);overflow:hidden;">
                    <div style="height:100%;width:{pct}%;border-radius:3px;
                        background:linear-gradient(90deg,{bar_color}60,{bar_color});
                        transition:width 0.5s ease;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### All Models — Side-by-Side Comparison")

    # Comparison chart
    comparison = {r["model"]: r["credits"] for r in all_results}
    channels_list = list(CHANNEL_LABELS.keys())

    fig_cmp = go.Figure()
    for model_id, creds in comparison.items():
        fig_cmp.add_trace(go.Bar(
            name=MODEL_LABELS[model_id],
            x=[CHANNEL_LABELS[ch] for ch in channels_list],
            y=[round(creds.get(ch, 0) * 100, 1) for ch in channels_list],
            marker_color=MODEL_COLORS[model_id],
        ))
    fig_cmp.update_layout(
        barmode="group",
        yaxis_title="Credit (%)",
        legend=dict(orientation="h", y=1.12, font=dict(size=10)),
        **PLOTLY_LAYOUT,
    )
    st.plotly_chart(fig_cmp, use_container_width=True)

    st.info("**Interpretation:** Large divergence on HCP Referral between First Touch and Last Touch indicates this channel plays a strong **closing** role but weak awareness role. Data-Driven (Shapley) is recommended for budget allocation — it measures true marginal channel contribution.")


# ═══════════════════════════════════════════════════════════════════════
# PAGE: CHANNELS
# ═══════════════════════════════════════════════════════════════════════

elif page == "📡 Channels":
    section_header("Channel Performance", "Aggregated KPIs by marketing channel · Walled garden channels use modeled attribution")
    compliance_strip("Aggregated channel data · No individual patient records · No PHI")

    ch_data = load_channel_perf()

    show_walled = st.toggle("Show Walled Garden Channels", value=True)
    if not show_walled:
        ch_data = [c for c in ch_data if not c["walled_garden"]]

    # Top bar chart
    df_bar = pd.DataFrame([{
        "Channel": c["channel_label"],
        "Appointments": c["conversions"],
        "color": CHANNEL_COLORS.get(c["channel"], TEAL),
    } for c in ch_data])

    fig_bar = go.Figure()
    for _, row in df_bar.iterrows():
        fig_bar.add_trace(go.Bar(
            x=[row["Channel"]], y=[row["Appointments"]],
            marker_color=row["color"], name=row["Channel"], showlegend=False,
        ))
    fig_bar.update_layout(title="Appointments by Channel", **PLOTLY_LAYOUT)
    st.plotly_chart(fig_bar, use_container_width=True)

    # Performance table
    st.markdown("### Channel KPI Table")
    max_cpa = max(c["cpa"] for c in ch_data)

    df_table = pd.DataFrame([{
        "Channel": c["channel_label"],
        "Type": "🟡 Modeled" if c["walled_garden"] else "🔵 Observed",
        "Impressions": f"{c['impressions']//1000:,}k",
        "Clicks": f"{c['clicks']:,}",
        "CTR": f"{c['ctr']}%",
        "Appointments": c["conversions"],
        "Spend": f"${c['cost']//1000:,}k",
        "CPA": f"${c['cpa']:.0f}",
    } for c in ch_data])

    st.dataframe(df_table, use_container_width=True, hide_index=True)

    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.warning("**Pharma / Medical Device:** OPDP/DDMAC guidelines apply to all DTC digital content. Fair balance requirements must be met in display and search ads. Off-label promotion is prohibited across all channels.")
    with col_n2:
        st.info("**HCP Referral Channel:** Tracked via NPI-level aggregation — not patient-level. BAA required with CRM vendors. Sunshine Act reporting obligations apply to HCP value transfers.")


# ═══════════════════════════════════════════════════════════════════════
# PAGE: COMPLIANCE
# ═══════════════════════════════════════════════════════════════════════

elif page == "🛡️ Compliance":
    section_header("Privacy & Compliance Posture", "De-identification · Consent · Regulatory framework · Audit controls")

    # Status bar
    st.markdown("""
    <div style="display:flex;align-items:center;gap:12px;padding:14px 20px;border-radius:10px;
        background:rgba(74,222,128,0.08);border:1px solid rgba(74,222,128,0.3);margin-bottom:24px;">
        <div style="width:12px;height:12px;border-radius:50%;background:#4ade80;
            box-shadow:0 0 0 4px rgba(74,222,128,0.2);flex-shrink:0;"></div>
        <div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:13px;color:#4ade80;font-weight:700;">
                COMPLIANT — All Frameworks</div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:#4a6080;">
                HIPAA Safe Harbor · WA MHMD · CA CMIA · TX THIPA · FTC HBNR · PHI in pipeline: NONE · Last verified: 2026-06-15</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Compliance KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("De-ID Method", "Safe Harbor", "§164.514(b)(2)")
    c2.metric("PHI in Analytics", "None", "Always excluded")
    c3.metric("Audit Controls", "Active", "HIPAA §164.312(b)")
    c4.metric("BAA Required", "Yes", "All vendors")

    st.markdown("<br>", unsafe_allow_html=True)

    tab_lineage, tab_consent, tab_laws, tab_audit = st.tabs([
        "DATA LINEAGE", "CONSENT STATUS", "REGULATORY MATRIX", "AUDIT LOG"
    ])

    # ── Data Lineage ──────────────────────────────────────────────────
    with tab_lineage:
        st.markdown("#### PHI Never Enters the Analytics Layer")
        steps = [
            ("Raw Source Data", "EMR / CRM / Ad Platforms", "CONTAINS PHI", "#f87171", "rgba(248,113,113,0.08)", "rgba(248,113,113,0.3)"),
            ("De-Identification Layer", "Safe Harbor: 18 identifiers removed", "PHI STRIPPED", "#fbbf24", "rgba(251,191,36,0.08)", "rgba(251,191,36,0.3)"),
            ("Aggregation Engine", "Cohort grouping · Weekly grain · Min. 11 per cell", "NO PHI", "#4ade80", "rgba(74,222,128,0.06)", "rgba(74,222,128,0.25)"),
            ("Analytics Layer (This App)", "Channel MTA · Journey funnels · Outcomes", "NO PHI", "#4ade80", "rgba(74,222,128,0.06)", "rgba(74,222,128,0.3)"),
        ]
        for label, sub, phi_label, phi_color, bg, border in steps:
            st.markdown(f"""
            <div style="padding:14px 18px;border-radius:10px;background:{bg};border:1px solid {border};margin-bottom:8px;
                display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:13px;font-weight:600;color:#e8f0fe;">{label}</div>
                    <div style="font-size:11px;color:#4a6080;margin-top:3px;">{sub}</div>
                </div>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:9px;color:{phi_color};
                    background:rgba(0,0,0,0.2);border:1px solid {phi_color}50;
                    padding:3px 8px;border-radius:4px;white-space:nowrap;">{phi_label}</span>
            </div>
            {"<div style='text-align:center;color:rgba(45,212,191,0.3);font-size:16px;line-height:1;margin:2px 0;'>↓</div>" if phi_label != "NO PHI" or label != "Analytics Layer (This App)" else ""}
            """, unsafe_allow_html=True)

    # ── Consent ───────────────────────────────────────────────────────
    with tab_consent:
        consent = load_consent()
        st.markdown(f"**Framework:** {consent['consent_framework']}")
        st.error(f"⛔ Opted-out cohorts ({consent['opted_out']:,} records) are **automatically excluded** from all analytics pipelines.")

        pie_data = {
            "Consent Type": ["Full Consent", "Limited Consent", "Opted Out (Excluded)"],
            "Count": [consent["full_consent"], consent["limited_consent"], consent["opted_out"]],
        }
        fig_consent = go.Figure(go.Pie(
            labels=pie_data["Consent Type"],
            values=pie_data["Count"],
            hole=0.55,
            marker=dict(colors=[GREEN, AMBER, RED], line=dict(color=NAVY, width=2)),
            textinfo="label+percent",
            textfont=dict(size=11, family="IBM Plex Mono"),
        ))
        fig_consent.update_layout(showlegend=False, **PLOTLY_LAYOUT)
        col_p, col_s = st.columns([1, 1])
        with col_p:
            st.plotly_chart(fig_consent, use_container_width=True)
        with col_s:
            for label, count, color in [
                ("Full Consent", consent["full_consent"], GREEN),
                ("Limited Consent", consent["limited_consent"], AMBER),
                ("Opted Out", consent["opted_out"], RED),
            ]:
                pct = round(count / consent["total_cohort_size"] * 100, 1)
                st.markdown(f"""
                <div style="padding:12px 16px;border-radius:8px;background:rgba(12,30,61,0.8);
                    border:1px solid rgba(45,212,191,0.1);margin-bottom:10px;">
                    <div style="font-size:12px;color:#94a3b8;">{label}</div>
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:1.2rem;color:{color};font-weight:600;">
                        {count:,} <span style="font-size:11px;color:#4a6080;">({pct}%)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Laws ──────────────────────────────────────────────────────────
    with tab_laws:
        laws = load_laws()
        st.markdown("Stricter of federal or state law applies · Updated June 2026")
        df_laws = pd.DataFrame([{
            "Law": l["law"],
            "Jurisdiction": l["jurisdiction"],
            "Applies To": l["applies_to"],
            "Key Requirement": l["key_requirement"],
            "Effective": l["effective"],
            "Status": "✅ Active" if l["status"] == "active" else "⚠️ " + l["status"],
        } for l in laws])
        st.dataframe(df_laws, use_container_width=True, hide_index=True)

        st.info("**Strictest standard applies:** When state law is stricter than HIPAA (e.g., WA My Health MY Data Act requiring opt-in consent for health data), the state standard governs. Always review jurisdiction-specific requirements before campaign deployment.")

    # ── Audit Log ─────────────────────────────────────────────────────
    with tab_audit:
        audit = load_audit_log()
        st.markdown(f"**{len(audit)} entries** · HIPAA §164.312(b) audit controls · Retention: 6 years · PHI accessed: **NEVER**")

        df_audit = pd.DataFrame([{
            "Log ID": e["log_id"],
            "Timestamp": e["timestamp"][:16].replace("T", " "),
            "User": e["user_id"],
            "Query": e["action"],
            "Data Category": e["data_category"],
            "Legal Basis": e["legal_basis"],
            "PHI?": "❌ NONE",
        } for e in audit])

        # Pagination
        PAGE = 10
        total_pages = (len(df_audit) - 1) // PAGE + 1
        audit_page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1) - 1
        st.dataframe(df_audit.iloc[audit_page*PAGE:(audit_page+1)*PAGE], use_container_width=True, hide_index=True)
        st.caption(f"Page {audit_page+1} of {total_pages} · {len(audit)} total entries")

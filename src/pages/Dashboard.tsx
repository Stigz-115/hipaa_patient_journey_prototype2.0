import { useEffect, useState } from "react";
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { Shield, Users, CalendarCheck, TrendingUp, Info, Lock } from "lucide-react";
import { api } from "../lib/api";

const CHANNEL_COLORS: Record<string, string> = {
  paid_search: "#2dd4bf",
  social_media: "#818cf8",
  display_ads: "#38bdf8",
  email_crm: "#4ade80",
  organic_content: "#fb923c",
  hcp_referral: "#f472b6",
  dtc_content: "#a78bfa",
  connected_tv: "#fbbf24",
};

function ComplianceDataLabel() {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: "6px",
      padding: "4px 10px", borderRadius: "6px",
      background: "rgba(45,212,191,0.05)",
      border: "1px solid rgba(45,212,191,0.15)",
      fontFamily: "'IBM Plex Mono', monospace",
      fontSize: "9px", color: "#4a6080", letterSpacing: "0.04em",
    }}>
      <Lock size={9} color="#2dd4bf" />
      Aggregated cohort · HIPAA Safe Harbor de-identified · No PHI
    </div>
  );
}

function KPICard({ value, label, sub, icon: Icon, delay = 0 }: any) {
  return (
    <div className="kpi-card animate-in" style={{ animationDelay: `${delay}ms`, opacity: 0 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
        <div style={{ padding: "8px", borderRadius: "8px", background: "rgba(45,212,191,0.08)", border: "1px solid rgba(45,212,191,0.15)" }}>
          <Icon size={16} color="#2dd4bf" />
        </div>
      </div>
      <div className="kpi-value">{value}</div>
      <div className="kpi-label" style={{ marginTop: "8px" }}>{label}</div>
      {sub && <div style={{ fontSize: "11px", color: "#4a6080", marginTop: "4px" }}>{sub}</div>}
    </div>
  );
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "rgba(7,18,40,0.97)", border: "1px solid rgba(45,212,191,0.2)",
      borderRadius: "8px", padding: "10px 14px", fontFamily: "'IBM Plex Mono', monospace", fontSize: "11px",
    }}>
      <div style={{ color: "#94a3b8", marginBottom: "4px" }}>{label}</div>
      {payload.map((p: any, i: number) => (
        <div key={i} style={{ color: p.color || "#2dd4bf" }}>
          {p.name}: <strong>{p.value?.toLocaleString()}</strong>
        </div>
      ))}
    </div>
  );
};

export function Dashboard() {
  const [kpis, setKpis] = useState<any>(null);
  const [trend, setTrend] = useState<any[]>([]);
  const [channels, setChannels] = useState<any[]>([]);

  useEffect(() => {
    api.kpis().then(setKpis).catch(() => {});
    api.trend().then(d => setTrend(d.weeks || [])).catch(() => {});
    api.channelPerformance().then(d => setChannels(d.channels || [])).catch(() => {});
  }, []);

  const channelMix = channels.slice(0, 6).map(c => ({
    name: c.channel_label,
    value: c.conversions,
    color: CHANNEL_COLORS[c.channel] || "#2dd4bf",
  }));

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: "32px" }} className="animate-in">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <h1 className="section-header" style={{ marginBottom: "6px" }}>Patient Journey Overview</h1>
            <p style={{ fontSize: "13px", color: "#94a3b8", margin: 0 }}>
              Multi-touch attribution analytics for healthcare marketing · Synthetic data prototype
            </p>
          </div>
          <ComplianceDataLabel />
        </div>

        {/* Info banner */}
        <div style={{
          marginTop: "16px", padding: "12px 16px", borderRadius: "10px",
          background: "rgba(251,191,36,0.05)", border: "1px solid rgba(251,191,36,0.2)",
          display: "flex", alignItems: "flex-start", gap: "10px",
        }}>
          <Info size={14} color="#fbbf24" style={{ marginTop: "1px", flexShrink: 0 }} />
          <div style={{ fontSize: "12px", color: "#94a3b8", lineHeight: 1.6 }}>
            <strong style={{ color: "#fbbf24" }}>Prototype Disclaimer:</strong> All data is 100% synthetic.
            This prototype demonstrates a HIPAA-compliant analytics architecture for healthcare marketing MTA.
            No real patient data, PHI, or identifiable information is used or stored.
            Intended for presentation to marketing, pharma, and medical device stakeholders.
          </div>
        </div>
      </div>

      {/* KPIs */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "16px", marginBottom: "32px" }}>
        <KPICard
          icon={Users}
          value={kpis ? kpis.total_journeys_analyzed?.toLocaleString() : "—"}
          label="Journeys Analyzed"
          sub="Aggregated cohort volume"
          delay={0}
        />
        <KPICard
          icon={CalendarCheck}
          value={kpis ? `${kpis.appointment_conversion_rate}%` : "—"}
          label="Appointment Conversion"
          sub="Awareness → Booked"
          delay={50}
        />
        <KPICard
          icon={TrendingUp}
          value={kpis ? kpis.avg_touchpoints_to_book : "—"}
          label="Avg Touchpoints to Book"
          sub="Across all channels"
          delay={100}
        />
        <KPICard
          icon={Shield}
          value={kpis ? kpis.journeys_with_positive_outcome?.toLocaleString() : "—"}
          label="Positive Outcomes"
          sub="Treatment outcomes recorded"
          delay={150}
        />
      </div>

      {/* Charts row */}
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: "20px", marginBottom: "20px" }}>
        {/* Trend chart */}
        <div className="card" style={{ padding: "24px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
            <div>
              <div style={{ fontSize: "14px", fontWeight: 600, color: "#e8f0fe" }}>Journey Volume Trend</div>
              <div style={{ fontSize: "11px", color: "#4a6080", marginTop: "2px", fontFamily: "'IBM Plex Mono', monospace" }}>26-week rolling · weekly cohort grain</div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={trend} margin={{ top: 5, right: 5, bottom: 0, left: -20 }}>
              <defs>
                <linearGradient id="journeyGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2dd4bf" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="apptGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#4ade80" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#4ade80" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="week" tick={{ fontSize: 10 }} tickFormatter={v => v?.slice(5)} interval={5} />
              <YAxis tick={{ fontSize: 10 }} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="journeys" stroke="#2dd4bf" strokeWidth={2} fill="url(#journeyGrad)" name="Journeys" />
              <Area type="monotone" dataKey="appointments" stroke="#4ade80" strokeWidth={2} fill="url(#apptGrad)" name="Appointments" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Channel mix pie */}
        <div className="card" style={{ padding: "24px" }}>
          <div style={{ fontSize: "14px", fontWeight: 600, color: "#e8f0fe", marginBottom: "4px" }}>Channel Mix</div>
          <div style={{ fontSize: "11px", color: "#4a6080", marginBottom: "16px", fontFamily: "'IBM Plex Mono', monospace" }}>By appointment conversions</div>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie data={channelMix} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={2} dataKey="value">
                {channelMix.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: "flex", flexDirection: "column", gap: "4px", marginTop: "8px" }}>
            {channelMix.slice(0, 4).map((c, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "11px" }}>
                <div style={{ width: "8px", height: "8px", borderRadius: "2px", background: c.color, flexShrink: 0 }} />
                <span style={{ color: "#94a3b8", flex: 1 }}>{c.name}</span>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", color: "#e8f0fe" }}>{c.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Funnel bar */}
      <div className="card" style={{ padding: "24px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
          <div>
            <div style={{ fontSize: "14px", fontWeight: 600, color: "#e8f0fe" }}>Journey Funnel — All Conditions</div>
            <div style={{ fontSize: "11px", color: "#4a6080", marginTop: "2px", fontFamily: "'IBM Plex Mono', monospace" }}>Aggregated cohort · no individual records</div>
          </div>
        </div>
        <FunnelBar />
      </div>
    </div>
  );
}

function FunnelBar() {
  const [data, setData] = useState<any[]>([]);
  useEffect(() => {
    api.funnel().then(d => setData(d.stages || [])).catch(() => {});
  }, []);

  const STAGE_COLORS = ["#2dd4bf", "#14b8a6", "#0d9488", "#0f766e", "#115e59"];

  const CustomTooltip2 = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;
    const v = payload[0].value;
    const total = data[0]?.count || 1;
    return (
      <div style={{
        background: "rgba(7,18,40,0.97)", border: "1px solid rgba(45,212,191,0.2)",
        borderRadius: "8px", padding: "10px 14px", fontFamily: "'IBM Plex Mono', monospace", fontSize: "11px",
      }}>
        <div style={{ color: "#2dd4bf", marginBottom: "4px" }}>{label}</div>
        <div style={{ color: "#e8f0fe" }}>Count: {v?.toLocaleString()}</div>
        <div style={{ color: "#94a3b8" }}>of total: {(v / total * 100).toFixed(1)}%</div>
      </div>
    );
  };

  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: -10 }}>
        <XAxis dataKey="label" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 10 }} tickFormatter={v => v >= 1000 ? `${(v/1000).toFixed(0)}k` : v} />
        <Tooltip content={<CustomTooltip2 />} />
        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
          {data.map((_, i) => <Cell key={i} fill={STAGE_COLORS[i] || "#2dd4bf"} />)}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

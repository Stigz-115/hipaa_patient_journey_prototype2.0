import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, FunnelChart, Funnel, LabelList } from "recharts";
import { Lock, Filter, AlertTriangle } from "lucide-react";
import { api } from "../lib/api";

const STAGE_COLORS = ["#2dd4bf", "#14b8a6", "#0d9488", "#0f766e", "#115e59"];
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

function ComplianceStrip() {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: "8px", padding: "8px 14px",
      borderRadius: "8px", background: "rgba(45,212,191,0.05)", border: "1px solid rgba(45,212,191,0.15)",
      fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", color: "#4a6080", letterSpacing: "0.04em",
    }}>
      <Lock size={9} color="#2dd4bf" />
      Aggregated cohort data · HIPAA Safe Harbor · No PHI · Timestamps rounded to weekly grain
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
      <div style={{ color: "#94a3b8", marginBottom: "6px" }}>{label}</div>
      {payload.map((p: any, i: number) => (
        <div key={i} style={{ color: p.color || "#2dd4bf" }}>
          {p.name}: <strong>{typeof p.value === "number" ? p.value.toLocaleString() : p.value}</strong>
        </div>
      ))}
    </div>
  );
};

export function JourneyMap() {
  const [funnel, setFunnel] = useState<any>(null);
  const [flows, setFlows] = useState<any[]>([]);
  const [filters, setFilters] = useState<any>(null);
  const [condition, setCondition] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.filters().then(setFilters).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.funnel(condition || undefined),
      api.sankey(condition || undefined),
    ]).then(([f, s]) => {
      setFunnel(f);
      setFlows(s.flows || []);
    }).finally(() => setLoading(false));
  }, [condition]);

  // Aggregate flows by channel across conditions
  const channelAgg = flows.reduce((acc: any, row: any) => {
    const ch = row.channel;
    if (!acc[ch]) acc[ch] = { channel: ch, label: row.channel_label, awareness: 0, interest: 0, intent: 0, booked: 0, walled: row.walled_garden };
    acc[ch].awareness += row.awareness;
    acc[ch].interest += row.interest;
    acc[ch].intent += row.intent;
    acc[ch].booked += row.appointment_booked;
    return acc;
  }, {});

  const channelRows = Object.values(channelAgg).sort((a: any, b: any) => b.booked - a.booked);

  return (
    <div>
      {/* Header */}
      <div className="animate-in" style={{ marginBottom: "28px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
          <div>
            <h1 className="section-header" style={{ marginBottom: "4px" }}>Patient Journey Map</h1>
            <p style={{ fontSize: "13px", color: "#94a3b8", margin: 0 }}>
              Funnel flow from awareness through appointment booking and outcomes
            </p>
          </div>
          <ComplianceStrip />
        </div>

        {/* Filter */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <Filter size={13} color="#4a6080" />
          <span style={{ fontSize: "12px", color: "#94a3b8" }}>Filter by condition:</span>
          <select
            value={condition}
            onChange={e => setCondition(e.target.value)}
            style={{
              background: "rgba(12,30,61,0.9)", border: "1px solid rgba(45,212,191,0.2)",
              borderRadius: "6px", color: "#e8f0fe", padding: "5px 10px", fontSize: "12px",
              fontFamily: "'Instrument Sans', sans-serif", cursor: "pointer",
            }}
          >
            <option value="">All Conditions</option>
            {filters?.conditions?.map((c: any) => (
              <option key={c.value} value={c.value}>{c.label}</option>
            ))}
          </select>
          {funnel && (
            <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "11px", color: "#4ade80" }}>
              Conversion rate: {funnel.conversion_rate}%
            </span>
          )}
        </div>
      </div>

      {/* Funnel stages */}
      <div className="card animate-in animate-in-delay-1" style={{ padding: "24px", marginBottom: "20px" }}>
        <div style={{ fontSize: "14px", fontWeight: 600, color: "#e8f0fe", marginBottom: "4px" }}>Funnel Stages</div>
        <div style={{ fontSize: "11px", color: "#4a6080", marginBottom: "20px", fontFamily: "'IBM Plex Mono', monospace" }}>
          Cohort-level counts · no individual patient records
        </div>

        {funnel && (
          <div style={{ display: "flex", gap: "8px", marginBottom: "20px" }}>
            {funnel.stages.map((s: any, i: number) => {
              const total = funnel.stages[0]?.count || 1;
              const pct = (s.count / total * 100).toFixed(1);
              return (
                <div key={s.stage} style={{ flex: 1, textAlign: "center" }}>
                  <div style={{
                    height: `${Math.max(40, (s.count / total) * 160)}px`,
                    background: `linear-gradient(180deg, ${STAGE_COLORS[i]}40, ${STAGE_COLORS[i]}20)`,
                    border: `1px solid ${STAGE_COLORS[i]}50`,
                    borderRadius: "8px",
                    display: "flex", alignItems: "flex-end", justifyContent: "center",
                    padding: "8px",
                    transition: "all 0.4s ease",
                    marginBottom: "8px",
                  }}>
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "14px", fontWeight: 600, color: STAGE_COLORS[i] }}>
                      {s.count?.toLocaleString()}
                    </span>
                  </div>
                  <div style={{ fontSize: "10px", fontWeight: 600, color: STAGE_COLORS[i], letterSpacing: "0.05em", textTransform: "uppercase" }}>
                    {s.label}
                  </div>
                  <div style={{ fontSize: "10px", color: "#4a6080", fontFamily: "'IBM Plex Mono', monospace" }}>
                    {pct}% of total
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Channel flow table */}
      <div className="card animate-in animate-in-delay-2" style={{ padding: "24px", marginBottom: "20px" }}>
        <div style={{ fontSize: "14px", fontWeight: 600, color: "#e8f0fe", marginBottom: "4px" }}>Channel → Stage Breakdown</div>
        <div style={{ fontSize: "11px", color: "#4a6080", marginBottom: "20px", fontFamily: "'IBM Plex Mono', monospace" }}>
          Aggregated cohort volume by channel across journey stages
        </div>

        <table className="data-table">
          <thead>
            <tr>
              <th>Channel</th>
              <th>Type</th>
              <th style={{ textAlign: "right" }}>Awareness</th>
              <th style={{ textAlign: "right" }}>Interest</th>
              <th style={{ textAlign: "right" }}>Intent</th>
              <th style={{ textAlign: "right" }}>Booked</th>
              <th style={{ width: "180px" }}>Conversion Flow</th>
            </tr>
          </thead>
          <tbody>
            {channelRows.map((row: any) => {
              const color = CHANNEL_COLORS[row.channel] || "#2dd4bf";
              const pct = Math.round(row.booked / Math.max(row.awareness, 1) * 100);
              return (
                <tr key={row.channel}>
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <div style={{ width: "8px", height: "8px", borderRadius: "2px", background: color, flexShrink: 0 }} />
                      <span style={{ color: "#e8f0fe", fontWeight: 500 }}>{row.label}</span>
                    </div>
                  </td>
                  <td>
                    {row.walled ? (
                      <span className="channel-tag walled">
                        <AlertTriangle size={9} /> Walled Garden
                      </span>
                    ) : (
                      <span className="channel-tag">Observed</span>
                    )}
                  </td>
                  <td style={{ textAlign: "right", fontFamily: "'IBM Plex Mono', monospace", color: "#94a3b8" }}>{row.awareness?.toLocaleString()}</td>
                  <td style={{ textAlign: "right", fontFamily: "'IBM Plex Mono', monospace", color: "#94a3b8" }}>{row.interest?.toLocaleString()}</td>
                  <td style={{ textAlign: "right", fontFamily: "'IBM Plex Mono', monospace", color: "#94a3b8" }}>{row.intent?.toLocaleString()}</td>
                  <td style={{ textAlign: "right", fontFamily: "'IBM Plex Mono', monospace", color }}>
                    <strong>{row.booked?.toLocaleString()}</strong>
                  </td>
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <div className="attr-bar" style={{ flex: 1 }}>
                        <div className="attr-bar-fill" style={{ width: `${pct}%`, background: `linear-gradient(90deg, ${color}80, ${color})` }} />
                      </div>
                      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "10px", color, minWidth: "30px", textAlign: "right" }}>{pct}%</span>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Walled garden note */}
      <div style={{
        padding: "12px 16px", borderRadius: "8px",
        background: "rgba(251,191,36,0.05)", border: "1px solid rgba(251,191,36,0.2)",
        display: "flex", gap: "10px", alignItems: "flex-start",
      }}>
        <AlertTriangle size={13} color="#fbbf24" style={{ marginTop: "1px", flexShrink: 0 }} />
        <div style={{ fontSize: "11px", color: "#94a3b8", lineHeight: 1.6 }}>
          <strong style={{ color: "#fbbf24" }}>Walled Garden Channels (Social, CTV):</strong> Direct measurement is restricted under platform policies and HIPAA marketing rules.
          Conversions for these channels use <strong style={{ color: "#e8f0fe" }}>modeled attribution</strong> — not pixel-level tracking — to remain compliant.
          Under WA My Health MY Data Act (2024), health-intent targeting on social platforms requires affirmative opt-in.
        </div>
      </div>
    </div>
  );
}

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";
import { AlertTriangle, TrendingUp, TrendingDown, Lock, Eye, EyeOff } from "lucide-react";
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

function MiniSparkline({ data, color }: { data: number[]; color: string }) {
  const chartData = data.map((v, i) => ({ i, v }));
  return (
    <ResponsiveContainer width={80} height={28}>
      <LineChart data={chartData} margin={{ top: 2, right: 2, bottom: 2, left: 2 }}>
        <Line type="monotone" dataKey="v" stroke={color} strokeWidth={1.5} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

function CPABar({ value, max }: { value: number; max: number }) {
  const pct = Math.min(100, (value / max) * 100);
  const color = pct < 33 ? "#4ade80" : pct < 66 ? "#fbbf24" : "#f87171";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
      <div className="attr-bar" style={{ flex: 1 }}>
        <div className="attr-bar-fill" style={{ width: `${pct}%`, background: `linear-gradient(90deg, ${color}60, ${color})` }} />
      </div>
      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "11px", color, minWidth: "55px", textAlign: "right" }}>
        ${value.toFixed(0)}
      </span>
    </div>
  );
}

export function ChannelAnalysis() {
  const [channels, setChannels] = useState<any[]>([]);
  const [showWalled, setShowWalled] = useState(true);

  useEffect(() => {
    api.channelPerformance().then(d => setChannels(d.channels || [])).catch(() => {});
  }, []);

  const maxCPA = Math.max(...channels.map(c => c.cpa));
  const filtered = showWalled ? channels : channels.filter(c => !c.walled_garden);

  const barData = channels.slice(0, 8).map(c => ({
    name: c.channel_label?.split(" ")[0],
    conversions: c.conversions,
    fill: CHANNEL_COLORS[c.channel] || "#2dd4bf",
  }));

  return (
    <div>
      {/* Header */}
      <div className="animate-in" style={{ marginBottom: "28px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <h1 className="section-header" style={{ marginBottom: "4px" }}>Channel Performance</h1>
            <p style={{ fontSize: "13px", color: "#94a3b8", margin: 0 }}>
              Aggregated KPIs by marketing channel · No individual patient data · Walled garden channels use modeled attribution
            </p>
          </div>
          <div style={{
            display: "flex", alignItems: "center", gap: "6px", padding: "6px 12px", borderRadius: "8px",
            background: "rgba(45,212,191,0.05)", border: "1px solid rgba(45,212,191,0.15)",
            fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", color: "#4a6080",
          }}>
            <Lock size={9} color="#2dd4bf" /> Aggregated · No PHI
          </div>
        </div>
      </div>

      {/* Top bar chart */}
      <div className="card animate-in animate-in-delay-1" style={{ padding: "24px", marginBottom: "20px" }}>
        <div style={{ fontSize: "14px", fontWeight: 600, color: "#e8f0fe", marginBottom: "4px" }}>Appointments by Channel</div>
        <div style={{ fontSize: "11px", color: "#4a6080", marginBottom: "20px", fontFamily: "'IBM Plex Mono', monospace" }}>Total attributed appointment conversions</div>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={barData} margin={{ top: 5, right: 5, bottom: 5, left: -15 }}>
            <XAxis dataKey="name" tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="conversions" name="Appointments" radius={[4, 4, 0, 0]}>
              {barData.map((entry, i) => (
                <rect key={i} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Toggle walled garden */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
        <div style={{ fontSize: "11px", color: "#94a3b8" }}>
          Showing {filtered.length} channels
        </div>
        <button
          onClick={() => setShowWalled(!showWalled)}
          style={{
            display: "flex", alignItems: "center", gap: "6px",
            padding: "6px 12px", borderRadius: "6px", cursor: "pointer",
            background: "rgba(251,191,36,0.08)", border: "1px solid rgba(251,191,36,0.25)",
            color: "#fbbf24", fontFamily: "'IBM Plex Mono', monospace", fontSize: "10px",
          }}
        >
          {showWalled ? <Eye size={11} /> : <EyeOff size={11} />}
          {showWalled ? "Hide" : "Show"} Walled Garden
        </button>
      </div>

      {/* Channel table */}
      <div className="card animate-in animate-in-delay-2" style={{ padding: "0", overflow: "hidden" }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>Channel</th>
              <th>Measurement</th>
              <th style={{ textAlign: "right" }}>Impressions</th>
              <th style={{ textAlign: "right" }}>Clicks</th>
              <th style={{ textAlign: "right" }}>CTR</th>
              <th style={{ textAlign: "right" }}>Appts</th>
              <th style={{ textAlign: "right" }}>Spend</th>
              <th style={{ width: "160px" }}>CPA</th>
              <th style={{ width: "100px" }}>Trend</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((ch: any) => {
              const color = CHANNEL_COLORS[ch.channel] || "#2dd4bf";
              return (
                <tr key={ch.channel}>
                  <td>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      <div style={{ width: "10px", height: "10px", borderRadius: "2px", background: color, flexShrink: 0 }} />
                      <span style={{ color: "#e8f0fe", fontWeight: 500, fontSize: "13px" }}>{ch.channel_label}</span>
                    </div>
                  </td>
                  <td>
                    {ch.walled_garden ? (
                      <span className="channel-tag walled">
                        <AlertTriangle size={9} /> Modeled
                      </span>
                    ) : (
                      <span className="channel-tag">Observed</span>
                    )}
                  </td>
                  <td style={{ textAlign: "right", fontFamily: "'IBM Plex Mono', monospace", fontSize: "12px", color: "#94a3b8" }}>
                    {(ch.impressions / 1000).toFixed(0)}k
                  </td>
                  <td style={{ textAlign: "right", fontFamily: "'IBM Plex Mono', monospace", fontSize: "12px", color: "#94a3b8" }}>
                    {ch.clicks?.toLocaleString()}
                  </td>
                  <td style={{ textAlign: "right", fontFamily: "'IBM Plex Mono', monospace", fontSize: "12px", color: "#94a3b8" }}>
                    {ch.ctr}%
                  </td>
                  <td style={{ textAlign: "right", fontFamily: "'IBM Plex Mono', monospace", fontSize: "13px", color }}>
                    <strong>{ch.conversions?.toLocaleString()}</strong>
                  </td>
                  <td style={{ textAlign: "right", fontFamily: "'IBM Plex Mono', monospace", fontSize: "12px", color: "#94a3b8" }}>
                    ${(ch.cost / 1000).toFixed(0)}k
                  </td>
                  <td>
                    <CPABar value={ch.cpa} max={maxCPA} />
                  </td>
                  <td>
                    <MiniSparkline data={ch.trend} color={color} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* HIPAA marketing notes */}
      <div style={{ marginTop: "20px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px" }}>
        <div style={{
          padding: "14px 16px", borderRadius: "8px",
          background: "rgba(251,191,36,0.05)", border: "1px solid rgba(251,191,36,0.2)",
        }}>
          <div style={{ display: "flex", gap: "8px", alignItems: "flex-start" }}>
            <AlertTriangle size={13} color="#fbbf24" style={{ marginTop: "2px", flexShrink: 0 }} />
            <div>
              <div style={{ fontSize: "11px", fontWeight: 600, color: "#fbbf24", marginBottom: "4px" }}>Pharma / Medical Device Note</div>
              <div style={{ fontSize: "11px", color: "#94a3b8", lineHeight: 1.6 }}>
                OPDP/DDMAC guidelines apply to all DTC digital content. Fair balance requirements must be met in display and search ads.
                Off-label promotion is prohibited across all channels.
              </div>
            </div>
          </div>
        </div>
        <div style={{
          padding: "14px 16px", borderRadius: "8px",
          background: "rgba(45,212,191,0.04)", border: "1px solid rgba(45,212,191,0.15)",
        }}>
          <div style={{ display: "flex", gap: "8px", alignItems: "flex-start" }}>
            <Lock size={13} color="#2dd4bf" style={{ marginTop: "2px", flexShrink: 0 }} />
            <div>
              <div style={{ fontSize: "11px", fontWeight: 600, color: "#2dd4bf", marginBottom: "4px" }}>HCP Referral Channel</div>
              <div style={{ fontSize: "11px", color: "#94a3b8", lineHeight: 1.6 }}>
                HCP-directed programs tracked via NPI-level aggregation — not patient-level. BAA required with CRM vendors.
                Sunshine Act reporting obligations apply to HCP value transfers.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

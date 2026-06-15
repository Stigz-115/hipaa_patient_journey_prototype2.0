import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, RadarChart, Radar, PolarGrid, PolarAngleAxis, Legend } from "recharts";
import { Lock, Info, ChevronDown, ChevronUp } from "lucide-react";
import { api } from "../lib/api";

const MODEL_COLORS: Record<string, string> = {
  first_touch: "#38bdf8",
  last_touch: "#f472b6",
  linear: "#a78bfa",
  time_decay: "#fb923c",
  data_driven: "#2dd4bf",
};

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
      maxWidth: "200px",
    }}>
      <div style={{ color: "#94a3b8", marginBottom: "6px", wordBreak: "break-word" }}>{label}</div>
      {payload.map((p: any, i: number) => (
        <div key={i} style={{ color: p.color || "#2dd4bf", marginBottom: "2px" }}>
          {p.name}: <strong>{p.value}%</strong>
        </div>
      ))}
    </div>
  );
};

function ModelCard({ model, selected, onClick }: { model: any; selected: boolean; onClick: () => void }) {
  const color = MODEL_COLORS[model.value] || "#2dd4bf";
  return (
    <button
      onClick={onClick}
      style={{
        textAlign: "left", cursor: "pointer", padding: "14px 16px", borderRadius: "10px",
        border: `1px solid ${selected ? color + "60" : "rgba(45,212,191,0.1)"}`,
        background: selected ? `${color}10` : "rgba(7,18,40,0.5)",
        transition: "all 0.2s ease", width: "100%",
        boxShadow: selected ? `0 0 20px ${color}15` : "none",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "4px" }}>
        <div style={{ width: "10px", height: "10px", borderRadius: "50%", background: color, flexShrink: 0 }} />
        <span style={{ fontSize: "13px", fontWeight: 600, color: selected ? color : "#e8f0fe" }}>{model.label}</span>
      </div>
      <div style={{ fontSize: "10px", color: "#4a6080", lineHeight: 1.5, paddingLeft: "18px" }}>
        {model.description?.slice(0, 80)}…
      </div>
    </button>
  );
}

export function Attribution() {
  const [comparison, setComparison] = useState<any>(null);
  const [selectedModel, setSelectedModel] = useState("data_driven");
  const [singleResult, setSingleResult] = useState<any>(null);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    api.compareModels().then(setComparison).catch(() => {});
  }, []);

  useEffect(() => {
    api.attribution(selectedModel).then(setSingleResult).catch(() => {});
  }, [selectedModel]);

  const selectedModelMeta = comparison?.models?.find((m: any) => m.value === selectedModel);

  return (
    <div>
      {/* Header */}
      <div className="animate-in" style={{ marginBottom: "28px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <h1 className="section-header" style={{ marginBottom: "4px" }}>Multi-Touch Attribution</h1>
            <p style={{ fontSize: "13px", color: "#94a3b8", margin: 0 }}>
              Compare 5 MTA models across channels · De-identified journey sequences only · No PHI
            </p>
          </div>
          <div style={{
            display: "flex", alignItems: "center", gap: "6px", padding: "6px 12px", borderRadius: "8px",
            background: "rgba(45,212,191,0.05)", border: "1px solid rgba(45,212,191,0.15)",
            fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", color: "#4a6080",
          }}>
            <Lock size={9} color="#2dd4bf" /> Anonymized journey hashes · No PHI
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "220px 1fr", gap: "20px" }}>
        {/* Model selector */}
        <div className="animate-in animate-in-delay-1">
          <div style={{ fontSize: "10px", fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", color: "#4a6080", marginBottom: "10px", fontFamily: "'IBM Plex Mono', monospace" }}>
            MTA Model
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
            {comparison?.models?.map((m: any) => (
              <ModelCard
                key={m.value}
                model={m}
                selected={selectedModel === m.value}
                onClick={() => setSelectedModel(m.value)}
              />
            ))}
          </div>
        </div>

        {/* Right panel */}
        <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
          {/* Selected model breakdown */}
          {singleResult && (
            <div className="card animate-in animate-in-delay-2" style={{ padding: "24px" }}>
              <div style={{ marginBottom: "20px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <div style={{ fontSize: "14px", fontWeight: 600, color: "#e8f0fe" }}>{singleResult.model_label}</div>
                    <div style={{ fontSize: "11px", color: "#4a6080", marginTop: "2px" }}>{singleResult.description}</div>
                  </div>
                  <div style={{
                    padding: "4px 10px", borderRadius: "6px",
                    background: "rgba(45,212,191,0.08)", border: "1px solid rgba(45,212,191,0.2)",
                    fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", color: "#2dd4bf",
                  }}>
                    Credits sum: {Object.values(singleResult.credits || {}).reduce((a: any, b: any) => a + b, 0).toFixed(2) === "1.00" ? "✓ 1.00" : "~1.00"}
                  </div>
                </div>

                {selectedModelMeta && (
                  <div style={{
                    marginTop: "12px", padding: "10px 14px", borderRadius: "8px",
                    background: "rgba(45,212,191,0.05)", border: "1px solid rgba(45,212,191,0.15)",
                  }}>
                    <div style={{ fontSize: "10px", fontWeight: 600, letterSpacing: "0.05em", textTransform: "uppercase", color: "#2dd4bf", marginBottom: "4px", fontFamily: "'IBM Plex Mono', monospace" }}>
                      Healthcare Marketing Context
                    </div>
                    <div style={{ fontSize: "12px", color: "#94a3b8", lineHeight: 1.6 }}>
                      {selectedModelMeta.healthcare_context}
                    </div>
                  </div>
                )}
              </div>

              {/* Channel bars */}
              <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                {singleResult.rows?.map((row: any) => {
                  const color = CHANNEL_COLORS[row.channel] || "#2dd4bf";
                  return (
                    <div key={row.channel}>
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                          <div style={{ width: "8px", height: "8px", borderRadius: "2px", background: color }} />
                          <span style={{ fontSize: "12px", color: "#94a3b8" }}>{row.channel_label}</span>
                        </div>
                        <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "12px", color }}>{row.pct}%</span>
                      </div>
                      <div className="attr-bar">
                        <div className="attr-bar-fill" style={{ width: `${row.pct}%`, background: `linear-gradient(90deg, ${color}60, ${color})` }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Side-by-side comparison chart */}
          {comparison && (
            <div className="card animate-in animate-in-delay-3" style={{ padding: "24px" }}>
              <div style={{ fontSize: "14px", fontWeight: 600, color: "#e8f0fe", marginBottom: "4px" }}>Model Comparison — All 5 Approaches</div>
              <div style={{ fontSize: "11px", color: "#4a6080", marginBottom: "20px", fontFamily: "'IBM Plex Mono', monospace" }}>
                Channel credit (%) across MTA models · spot where models diverge
              </div>

              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={comparison.matrix} margin={{ top: 5, right: 5, bottom: 5, left: -15 }}>
                  <XAxis dataKey="channel_label" tick={{ fontSize: 9 }} angle={-20} textAnchor="end" height={50} />
                  <YAxis tick={{ fontSize: 10 }} unit="%" />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend iconSize={8} wrapperStyle={{ fontSize: "10px", fontFamily: "'IBM Plex Mono', monospace" }} />
                  {comparison.models.map((m: any) => (
                    <Bar key={m.value} dataKey={m.value} name={m.label} fill={MODEL_COLORS[m.value]} radius={[3, 3, 0, 0]} />
                  ))}
                </BarChart>
              </ResponsiveContainer>

              <div style={{
                marginTop: "16px", padding: "10px 14px", borderRadius: "8px",
                background: "rgba(251,191,36,0.05)", border: "1px solid rgba(251,191,36,0.15)",
                fontSize: "11px", color: "#94a3b8", lineHeight: 1.6,
              }}>
                <strong style={{ color: "#fbbf24" }}>Interpretation note:</strong> Large divergence between First Touch and Last Touch on HCP Referral indicates this channel plays a strong closing role but weak awareness role.
                Data-Driven (Shapley) is recommended for budget allocation decisions due to its marginal contribution approach.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

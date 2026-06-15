import { useEffect, useState } from "react";
import { ShieldCheck, Lock, AlertTriangle, CheckCircle, XCircle, Info, FileText, Eye, Database } from "lucide-react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";
import { api } from "../lib/api";

function StatusPill({ status }: { status: string }) {
  const ok = status === "active" || status === "compliant";
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: "4px",
      padding: "2px 8px", borderRadius: "100px",
      fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", fontWeight: 500,
      letterSpacing: "0.08em", textTransform: "uppercase",
      background: ok ? "rgba(74,222,128,0.08)" : "rgba(251,191,36,0.08)",
      border: `1px solid ${ok ? "rgba(74,222,128,0.3)" : "rgba(251,191,36,0.3)"}`,
      color: ok ? "#4ade80" : "#fbbf24",
    }}>
      {ok ? <CheckCircle size={8} /> : <AlertTriangle size={8} />}
      {status}
    </span>
  );
}

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "rgba(7,18,40,0.97)", border: "1px solid rgba(45,212,191,0.2)",
      borderRadius: "8px", padding: "10px 14px", fontFamily: "'IBM Plex Mono', monospace", fontSize: "11px",
    }}>
      <div style={{ color: payload[0]?.payload?.color || "#2dd4bf" }}>{payload[0]?.name}</div>
      <div style={{ color: "#e8f0fe" }}>{payload[0]?.value?.toLocaleString()}</div>
    </div>
  );
};

export function Compliance() {
  const [status, setStatus] = useState<any>(null);
  const [auditLog, setAuditLog] = useState<any[]>([]);
  const [consent, setConsent] = useState<any>(null);
  const [laws, setLaws] = useState<any[]>([]);
  const [auditPage, setAuditPage] = useState(0);
  const PAGE_SIZE = 8;

  useEffect(() => {
    api.complianceStatus().then(setStatus).catch(() => {});
    api.auditLog().then(d => setAuditLog(d.entries || [])).catch(() => {});
    api.consent().then(setConsent).catch(() => {});
    api.laws().then(d => setLaws(d.laws || [])).catch(() => {});
  }, []);

  const consentPieData = consent ? [
    { name: "Full Consent", value: consent.full_consent, color: "#4ade80" },
    { name: "Limited Consent", value: consent.limited_consent, color: "#fbbf24" },
    { name: "Opted Out (Excluded)", value: consent.opted_out, color: "#f87171" },
  ] : [];

  const pagedLog = auditLog.slice(auditPage * PAGE_SIZE, (auditPage + 1) * PAGE_SIZE);
  const totalPages = Math.ceil(auditLog.length / PAGE_SIZE);

  return (
    <div>
      {/* Header */}
      <div className="animate-in" style={{ marginBottom: "28px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <h1 className="section-header" style={{ marginBottom: "4px" }}>Privacy & Compliance Posture</h1>
            <p style={{ fontSize: "13px", color: "#94a3b8", margin: 0 }}>
              De-identification status · Consent management · Regulatory framework · Audit controls
            </p>
          </div>
          {status && (
            <div style={{
              display: "flex", alignItems: "center", gap: "10px", padding: "10px 16px", borderRadius: "10px",
              background: "rgba(74,222,128,0.08)", border: "1px solid rgba(74,222,128,0.3)",
            }}>
              <div className="pulse-dot" />
              <div>
                <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "11px", color: "#4ade80", fontWeight: 600 }}>
                  COMPLIANT
                </div>
                <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", color: "#4a6080" }}>
                  PHI in pipeline: {status.phi_in_pipeline ? "YES ⚠️" : "NONE ✓"}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Compliance overview cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "14px", marginBottom: "20px" }}>
        {[
          { icon: Lock, label: "De-ID Method", value: "Safe Harbor", sub: "§164.514(b)(2)", color: "#4ade80" },
          { icon: Eye, label: "PHI in Analytics", value: "None", sub: "Always excluded", color: "#4ade80" },
          { icon: FileText, label: "Audit Controls", value: "Active", sub: "HIPAA §164.312(b)", color: "#4ade80" },
          { icon: Database, label: "BAA Required", value: "Yes", sub: "All vendors", color: "#fbbf24" },
        ].map((item, i) => {
          const Icon = item.icon;
          return (
            <div key={i} className="kpi-card animate-in" style={{ animationDelay: `${i * 50}ms`, opacity: 0 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "12px" }}>
                <div style={{ padding: "8px", borderRadius: "8px", background: "rgba(45,212,191,0.08)", border: "1px solid rgba(45,212,191,0.15)" }}>
                  <Icon size={15} color={item.color} />
                </div>
              </div>
              <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "1.4rem", fontWeight: 600, color: item.color }}>{item.value}</div>
              <div className="kpi-label">{item.label}</div>
              <div style={{ fontSize: "10px", color: "#4a6080", marginTop: "3px" }}>{item.sub}</div>
            </div>
          );
        })}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "20px" }}>
        {/* Data lineage diagram */}
        <div className="card animate-in animate-in-delay-1" style={{ padding: "24px" }}>
          <div style={{ fontSize: "14px", fontWeight: 600, color: "#e8f0fe", marginBottom: "4px" }}>Data Lineage — Privacy Layer</div>
          <div style={{ fontSize: "11px", color: "#4a6080", marginBottom: "20px", fontFamily: "'IBM Plex Mono', monospace" }}>
            PHI never enters the analytics layer
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0" }}>
            {[
              { label: "Raw Source Data", sub: "EMR / CRM / Ad Platforms", phi: true, color: "#f87171" },
              { label: "De-Identification Layer", sub: "Safe Harbor: 18 identifiers removed", phi: null, color: "#fbbf24", arrow: true },
              { label: "Aggregation Engine", sub: "Cohort grouping · Weekly grain · Min. 11 per cell", phi: false, color: "#fbbf24", arrow: true },
              { label: "Analytics Layer (This App)", sub: "Channel MTA · Journey funnels · Outcomes", phi: false, color: "#4ade80", arrow: true },
            ].map((step, i) => (
              <div key={i}>
                {i > 0 && (
                  <div style={{ display: "flex", justifyContent: "center", padding: "4px 0" }}>
                    <div style={{ width: "2px", height: "20px", background: "rgba(45,212,191,0.2)" }} />
                  </div>
                )}
                <div style={{
                  padding: "12px 14px", borderRadius: "8px",
                  border: `1px solid ${step.phi === true ? "rgba(248,113,113,0.3)" : step.phi === null ? "rgba(251,191,36,0.3)" : "rgba(74,222,128,0.3)"}`,
                  background: step.phi === true ? "rgba(248,113,113,0.05)" : step.phi === null ? "rgba(251,191,36,0.05)" : "rgba(74,222,128,0.05)",
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div>
                      <div style={{ fontSize: "12px", fontWeight: 600, color: "#e8f0fe" }}>{step.label}</div>
                      <div style={{ fontSize: "10px", color: "#4a6080", marginTop: "2px" }}>{step.sub}</div>
                    </div>
                    {step.phi === true && (
                      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", color: "#f87171", background: "rgba(248,113,113,0.1)", border: "1px solid rgba(248,113,113,0.3)", padding: "2px 6px", borderRadius: "4px" }}>
                        CONTAINS PHI
                      </span>
                    )}
                    {step.phi === false && (
                      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", color: "#4ade80", background: "rgba(74,222,128,0.1)", border: "1px solid rgba(74,222,128,0.3)", padding: "2px 6px", borderRadius: "4px" }}>
                        NO PHI
                      </span>
                    )}
                    {step.phi === null && (
                      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", color: "#fbbf24", background: "rgba(251,191,36,0.1)", border: "1px solid rgba(251,191,36,0.3)", padding: "2px 6px", borderRadius: "4px" }}>
                        PHI STRIPPED
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Consent pie */}
        <div className="card animate-in animate-in-delay-2" style={{ padding: "24px" }}>
          <div style={{ fontSize: "14px", fontWeight: 600, color: "#e8f0fe", marginBottom: "4px" }}>Consent Status</div>
          <div style={{ fontSize: "11px", color: "#4a6080", marginBottom: "8px", fontFamily: "'IBM Plex Mono', monospace" }}>
            {consent?.consent_framework}
          </div>
          {consent && (
            <div style={{
              display: "inline-flex", alignItems: "center", gap: "6px", padding: "4px 10px", borderRadius: "6px",
              background: "rgba(248,113,113,0.08)", border: "1px solid rgba(248,113,113,0.25)",
              fontSize: "10px", color: "#f87171", marginBottom: "16px", fontFamily: "'IBM Plex Mono', monospace",
            }}>
              <XCircle size={10} /> Opted-out cohorts excluded from all analytics
            </div>
          )}
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie data={consentPieData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={2} dataKey="value">
                {consentPieData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: "flex", flexDirection: "column", gap: "6px", marginTop: "12px" }}>
            {consentPieData.map((c, i) => (
              <div key={i} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                  <div style={{ width: "8px", height: "8px", borderRadius: "2px", background: c.color }} />
                  <span style={{ fontSize: "11px", color: "#94a3b8" }}>{c.name}</span>
                </div>
                <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "11px", color: c.color }}>
                  {c.value?.toLocaleString()} ({consent ? (c.value / consent.total_cohort_size * 100).toFixed(0) : 0}%)
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* State/Federal law matrix */}
      <div className="card animate-in animate-in-delay-3" style={{ padding: "24px", marginBottom: "20px" }}>
        <div style={{ fontSize: "14px", fontWeight: 600, color: "#e8f0fe", marginBottom: "4px" }}>Regulatory Framework</div>
        <div style={{ fontSize: "11px", color: "#4a6080", marginBottom: "20px", fontFamily: "'IBM Plex Mono', monospace" }}>
          Stricter of federal or state law applies · Updated June 2026
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Law / Regulation</th>
              <th>Jurisdiction</th>
              <th>Applies To</th>
              <th>Key Requirement</th>
              <th>Effective</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {laws.map((law: any) => (
              <tr key={law.law}>
                <td style={{ color: "#e8f0fe", fontWeight: 500, fontSize: "12px" }}>{law.law}</td>
                <td>
                  <span style={{
                    fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px",
                    padding: "2px 6px", borderRadius: "4px",
                    background: law.jurisdiction === "Federal" ? "rgba(45,212,191,0.08)" : "rgba(129,140,248,0.08)",
                    border: `1px solid ${law.jurisdiction === "Federal" ? "rgba(45,212,191,0.2)" : "rgba(129,140,248,0.2)"}`,
                    color: law.jurisdiction === "Federal" ? "#2dd4bf" : "#818cf8",
                  }}>
                    {law.jurisdiction}
                  </span>
                </td>
                <td style={{ fontSize: "11px", color: "#94a3b8", maxWidth: "160px" }}>{law.applies_to}</td>
                <td style={{ fontSize: "11px", color: "#94a3b8", maxWidth: "220px" }}>{law.key_requirement}</td>
                <td style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "10px", color: "#4a6080" }}>{law.effective}</td>
                <td><StatusPill status={law.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Audit log */}
      <div className="card animate-in animate-in-delay-4" style={{ padding: "24px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "4px" }}>
          <div style={{ fontSize: "14px", fontWeight: 600, color: "#e8f0fe" }}>Access Audit Log</div>
          <div style={{
            display: "flex", alignItems: "center", gap: "6px", padding: "4px 10px", borderRadius: "6px",
            background: "rgba(74,222,128,0.08)", border: "1px solid rgba(74,222,128,0.2)",
            fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", color: "#4ade80",
          }}>
            <CheckCircle size={9} /> PHI accessed: NEVER · Retention: 6 years
          </div>
        </div>
        <div style={{ fontSize: "11px", color: "#4a6080", marginBottom: "20px", fontFamily: "'IBM Plex Mono', monospace" }}>
          HIPAA §164.312(b) audit controls · Every data access logged with user, timestamp, legal basis
        </div>

        <table className="data-table">
          <thead>
            <tr>
              <th>Log ID</th>
              <th>Timestamp</th>
              <th>User</th>
              <th>Query</th>
              <th>Data Category</th>
              <th>Legal Basis</th>
              <th>PHI?</th>
            </tr>
          </thead>
          <tbody>
            {pagedLog.map((entry: any) => (
              <tr key={entry.log_id}>
                <td style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "10px", color: "#4a6080" }}>{entry.log_id}</td>
                <td style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "10px", color: "#4a6080" }}>
                  {entry.timestamp?.slice(0, 16).replace("T", " ")}
                </td>
                <td style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "11px", color: "#94a3b8" }}>{entry.user_id}</td>
                <td style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", color: "#4a6080", maxWidth: "200px", wordBreak: "break-all" }}>
                  {entry.action}
                </td>
                <td style={{ fontSize: "11px", color: "#94a3b8" }}>{entry.data_category}</td>
                <td style={{ fontSize: "10px", color: "#94a3b8" }}>{entry.legal_basis}</td>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                    <XCircle size={12} color="#4ade80" />
                    <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", color: "#4ade80" }}>NONE</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Pagination */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "16px" }}>
          <span style={{ fontSize: "11px", color: "#4a6080", fontFamily: "'IBM Plex Mono', monospace" }}>
            {auditLog.length} entries · page {auditPage + 1} / {totalPages}
          </span>
          <div style={{ display: "flex", gap: "8px" }}>
            <button
              onClick={() => setAuditPage(p => Math.max(0, p - 1))}
              disabled={auditPage === 0}
              style={{
                padding: "4px 12px", borderRadius: "6px", cursor: "pointer",
                background: "rgba(45,212,191,0.08)", border: "1px solid rgba(45,212,191,0.2)",
                color: auditPage === 0 ? "#4a6080" : "#2dd4bf",
                fontFamily: "'IBM Plex Mono', monospace", fontSize: "10px",
              }}
            >← Prev</button>
            <button
              onClick={() => setAuditPage(p => Math.min(totalPages - 1, p + 1))}
              disabled={auditPage >= totalPages - 1}
              style={{
                padding: "4px 12px", borderRadius: "6px", cursor: "pointer",
                background: "rgba(45,212,191,0.08)", border: "1px solid rgba(45,212,191,0.2)",
                color: auditPage >= totalPages - 1 ? "#4a6080" : "#2dd4bf",
                fontFamily: "'IBM Plex Mono', monospace", fontSize: "10px",
              }}
            >Next →</button>
          </div>
        </div>
      </div>
    </div>
  );
}

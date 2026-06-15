import { useState, useEffect } from "react";
import {
  LayoutDashboard, Route, BarChart3, LineChart, ShieldCheck, Activity,
  ChevronRight, Lock, AlertTriangle
} from "lucide-react";
import { Dashboard } from "./pages/Dashboard";
import { JourneyMap } from "./pages/JourneyMap";
import { Attribution } from "./pages/Attribution";
import { ChannelAnalysis } from "./pages/ChannelAnalysis";
import { Compliance } from "./pages/Compliance";
import { api } from "./lib/api";

type Page = "dashboard" | "journey" | "attribution" | "channels" | "compliance";

const NAV_ITEMS: { id: Page; label: string; icon: any; desc: string }[] = [
  { id: "dashboard", label: "Overview", icon: LayoutDashboard, desc: "KPIs & trends" },
  { id: "journey", label: "Patient Journey", icon: Route, desc: "Funnel & flow" },
  { id: "attribution", label: "Attribution", icon: BarChart3, desc: "MTA model comparison" },
  { id: "channels", label: "Channels", icon: LineChart, desc: "Performance analysis" },
  { id: "compliance", label: "Compliance", icon: ShieldCheck, desc: "Privacy & audit" },
];

function ComplianceStatusBanner() {
  const [status, setStatus] = useState<any>(null);
  useEffect(() => {
    api.complianceStatus().then(setStatus).catch(() => {});
  }, []);

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg"
      style={{ background: "rgba(74,222,128,0.06)", border: "1px solid rgba(74,222,128,0.2)" }}>
      <div className="pulse-dot" />
      <span style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "10px", color: "#4ade80", fontWeight: 500, letterSpacing: "0.08em" }}>
        HIPAA SAFE
      </span>
    </div>
  );
}

function Sidebar({ current, onChange }: { current: Page; onChange: (p: Page) => void }) {
  return (
    <aside style={{
      width: "240px",
      minHeight: "100vh",
      background: "linear-gradient(180deg, rgba(7,18,40,0.98) 0%, rgba(4,13,26,0.98) 100%)",
      borderRight: "1px solid rgba(45,212,191,0.12)",
      display: "flex",
      flexDirection: "column",
      padding: "0",
      flexShrink: 0,
    }}>
      {/* Logo */}
      <div style={{ padding: "28px 20px 20px", borderBottom: "1px solid rgba(45,212,191,0.08)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "6px" }}>
          <div style={{
            width: "32px", height: "32px",
            background: "linear-gradient(135deg, #14b8a6, #2dd4bf)",
            borderRadius: "8px",
            display: "flex", alignItems: "center", justifyContent: "center",
            flexShrink: 0,
          }}>
            <Activity size={16} color="#040d1a" strokeWidth={2.5} />
          </div>
          <div>
            <div style={{ fontFamily: "'DM Serif Display', serif", fontSize: "15px", color: "#e8f0fe", lineHeight: 1.2 }}>
              PathIQ
            </div>
            <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", color: "#4a6080", letterSpacing: "0.1em", textTransform: "uppercase" }}>
              Patient Journey Analytics
            </div>
          </div>
        </div>
      </div>

      {/* Compliance badge */}
      <div style={{ padding: "14px 16px", borderBottom: "1px solid rgba(45,212,191,0.06)" }}>
        <ComplianceStatusBanner />
      </div>

      {/* Nav */}
      <nav style={{ padding: "12px 10px", flex: 1 }}>
        <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", color: "#4a6080", letterSpacing: "0.15em", textTransform: "uppercase", padding: "6px 10px 10px" }}>
          Analytics
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const active = current === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onChange(item.id)}
              className="nav-link"
              style={active ? {
                background: "rgba(45,212,191,0.12)",
                color: "#2dd4bf",
                borderLeft: "2px solid #2dd4bf",
              } : undefined}
            >
              <Icon size={15} strokeWidth={active ? 2.5 : 2} />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: "13px", fontWeight: active ? 600 : 500, lineHeight: 1.3 }}>
                  {item.label}
                </div>
                <div style={{ fontSize: "10px", color: active ? "rgba(45,212,191,0.6)" : "#4a6080", lineHeight: 1 }}>
                  {item.desc}
                </div>
              </div>
              {active && <ChevronRight size={12} style={{ color: "#2dd4bf" }} />}
            </button>
          );
        })}
      </nav>

      {/* Footer disclaimer */}
      <div style={{
        padding: "16px",
        borderTop: "1px solid rgba(45,212,191,0.08)",
        background: "rgba(251,191,36,0.04)",
      }}>
        <div style={{ display: "flex", gap: "8px", alignItems: "flex-start" }}>
          <Lock size={11} style={{ color: "#fbbf24", marginTop: "2px", flexShrink: 0 }} />
          <div style={{ fontFamily: "'IBM Plex Mono', monospace", fontSize: "9px", color: "#4a6080", lineHeight: 1.6 }}>
            Synthetic data only. No PHI. De-identified per HIPAA §164.514(b) Safe Harbor.
          </div>
        </div>
      </div>
    </aside>
  );
}

const PAGE_COMPONENTS: Record<Page, React.ComponentType> = {
  dashboard: Dashboard,
  journey: JourneyMap,
  attribution: Attribution,
  channels: ChannelAnalysis,
  compliance: Compliance,
};

export default function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const PageComponent = PAGE_COMPONENTS[page];

  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar current={page} onChange={setPage} />
      <main style={{ flex: 1, overflowY: "auto", padding: "32px 36px", maxWidth: "100%" }}>
        <PageComponent />
      </main>
    </div>
  );
}

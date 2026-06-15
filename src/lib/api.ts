// API client — all requests go to the FastAPI backend via Vite proxy

const BASE = "/api";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json();
}

// ── Journey ──────────────────────────────────────────────────────────────────

export const api = {
  health: () => get<{ ok: boolean }>("/health"),

  // Dashboard
  kpis: () => get<any>("/dashboard/kpis"),

  // Journey
  funnel: (condition?: string, region?: string) => {
    const params = new URLSearchParams();
    if (condition) params.set("condition", condition);
    if (region) params.set("region", region);
    const qs = params.toString();
    return get<any>(`/journey/funnel${qs ? "?" + qs : ""}`);
  },
  sankey: (condition?: string) =>
    get<any>(`/journey/sankey${condition ? "?condition=" + condition : ""}`),
  trend: () => get<any>("/journey/trend"),
  filters: () => get<any>("/journey/filters"),

  // Attribution
  attribution: (model: string) => get<any>(`/attribution/run?model=${model}`),
  compareModels: () => get<any>("/attribution/compare"),
  models: () => get<any>("/attribution/models"),

  // Channel
  channelPerformance: () => get<any>("/channel/performance"),

  // Compliance
  auditLog: () => get<any>("/compliance/audit-log"),
  consent: () => get<any>("/compliance/consent"),
  laws: () => get<any>("/compliance/laws"),
  complianceStatus: () => get<any>("/compliance/status"),
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });
    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}));
      throw new Error(errBody.error || `HTTP error ${res.status}`);
    }
    return (await res.json()) as T;
  } catch (err: any) {
    console.warn(`API call failed for ${endpoint}:`, err.message);
    throw err;
  }
}

export const api = {
  getHealth: () => fetchApi<any>("/api/health"),
  getFleetDevices: () => fetchApi<{ devices: any[]; summary: any }>("/api/fleet/devices"),
  getFleetSummary: () => fetchApi<any>("/api/fleet/summary"),
  getFleetClusters: () => fetchApi<{ devices: any[]; count: number }>("/api/fleet/clusters"),
  getLiveDevice: () => fetchApi<any>("/api/device/live"),
  getLiveProcesses: () => fetchApi<{ processes: any[] }>("/api/device/processes"),
  getRegions: () => fetchApi<Record<string, any>>("/api/regions"),
  getDeviceProfiles: () => fetchApi<Record<string, any>>("/api/device-profiles"),
  estimateDevice: (payload: any) => fetchApi<any>("/api/estimate/device", { method: "POST", body: JSON.stringify(payload) }),
  estimateService: (payload: any) => fetchApi<any>("/api/estimate/service", { method: "POST", body: JSON.stringify(payload) }),
  estimateCloudVM: (payload: any) => fetchApi<any>("/api/estimate/cloud-vm", { method: "POST", body: JSON.stringify(payload) }),
  getAttribution: (items?: any[]) => fetchApi<any>("/api/attribution", { method: "POST", body: JSON.stringify({ items: items || [] }) }),
  getForecast: (payload?: any) => fetchApi<any>("/api/forecast", { method: "POST", body: JSON.stringify(payload || {}) }),
  getAnomalies: () => fetchApi<any>("/api/anomalies"),
  getRecommendations: () => fetchApi<any>("/api/optimize"),
  updateRecommendationStatus: (id: number, status: string) =>
    fetchApi<any>(`/api/recommendations/${id}/status`, { method: "PATCH", body: JSON.stringify({ status }) }),
  simulate: (payload: any) => fetchApi<any>("/api/simulate", { method: "POST", body: JSON.stringify(payload) }),
  getSimulationPresets: () => fetchApi<any>("/api/simulate/presets"),
  getCloudComparison: (params?: any) => fetchApi<any>(`/api/cloud/compare?vcpus=${params?.vcpus || 8}&memory_gb=${params?.memory_gb || 32}`),
  scheduleCloudJob: (payload: any) => fetchApi<any>("/api/cloud/schedule", { method: "POST", body: JSON.stringify(payload) }),
  getReport: (period?: string) => fetchApi<any>("/api/report", { method: "POST", body: JSON.stringify({ period: period || "H1 2026" }) }),
  getTargets: () => fetchApi<any[]>("/api/targets"),
  explainFeature: (item: any) => fetchApi<any>("/api/explain", { method: "POST", body: JSON.stringify(item) }),
  advisorChat: (query: string) => fetchApi<any>("/api/advisor/chat", { method: "POST", body: JSON.stringify({ query }) }),
};


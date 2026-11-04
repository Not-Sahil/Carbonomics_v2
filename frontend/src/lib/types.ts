export interface FleetDevice {
  id: number;
  device_id: string;
  device_name: string;
  device_type: string;
  region: string;
  status: "online" | "offline" | "idle";
  last_seen: string | null;
  cpu_util_pct: number;
  power_watts: number;
  total_daily_kg: number;
  total_kwh_daily: number;
  health_score: number;
  os?: string;
  processor?: string;
  tags?: string[];
  cluster_id?: number;
  cluster_label?: string;
}

export interface FleetSummary {
  total_devices: number;
  online_count: number;
  offline_count: number;
  total_daily_kg: number;
  total_annual_kg: number;
  total_annual_t: number;
  total_kwh_daily: number;
  avg_daily_kg: number;
  by_device_type: Record<string, number>;
  highest: string;
  trees_to_offset: number;
  carbon_efficiency_score: number;
  timestamp?: string;
}

export interface LiveHardwareMetrics {
  cpu_util_pct: number;
  cpu_count_logical: number;
  memory_total_gb: number;
  memory_used_gb: number;
  memory_util_pct: number;
  storage_total_gb: number;
  storage_used_gb: number;
  storage_util_pct: number;
  power_watts?: number;
  total_daily_kg?: number;
  total_kwh_daily?: number;
  uptime_hours?: number;
  battery_pct?: number | null;
  battery_charging?: boolean;
  net_bytes_sent_mb?: number;
  net_bytes_recv_mb?: number;
  os?: string;
  processor?: string;
}

export interface ProcessMetric {
  pid: number;
  name: string;
  cpu_percent: number;
  memory_percent: number;
}

export interface CloudRegionComparison {
  region_key: string;
  name: string;
  country: string;
  emission_factor_kg_kwh: number;
  renewable_pct: number;
  typical_pue: number;
  daily_kwh: number;
  daily_kg_co2: number;
  annual_t_co2: number;
  green_score: number;
  grade: string;
}

export interface OptimizationRec {
  id: string | number;
  category: string;
  title: string;
  description: string;
  affected_entity: string;
  potential_savings_kg: number;
  potential_savings_kwh: number;
  effort: "low" | "medium" | "high";
  priority: "low" | "medium" | "high";
  confidence_pct: number;
  status: string;
  impact?: string;
  steps?: string[];
}

export interface ForecastData {
  actual: Array<{ month: string; value: number; type: string; kwh?: number }>;
  forecast: Array<{ month: string; value: number; lower: number; upper: number; type: string; kwh?: number }>;
  predicted_total_kg: number;
  current_total_kg: number;
  pct_change: number;
  ai_confidence: number;
  trend_direction: string;
  at_risk: boolean;
  scenario: string;
  milestones: Array<{ name: string; month: string; status: string }>;
}

export interface SimulationResult {
  scenario_name: string;
  device_count: number;
  baseline: {
    daily_kwh: number;
    daily_kg: number;
    annual_kg: number;
    annual_t: number;
    region: string;
    region_name: string;
    pue: number;
    uptime_hours: number;
  };
  simulated: {
    daily_kwh: number;
    daily_kg: number;
    annual_kg: number;
    annual_t: number;
    region: string;
    region_name: string;
    pue: number;
    uptime_hours: number;
  };
  savings: {
    daily_kg: number;
    annual_kg: number;
    annual_t: number;
    daily_kwh: number;
    annual_kwh: number;
    pct_reduction: number;
    trees_equivalent: number;
    car_km_daily: number;
    estimated_cost_savings_usd: number;
  };
}

export interface SustainabilityTargetItem {
  id: number;
  title: string;
  target_type: string;
  target_value: number;
  current_value: number;
  unit: string;
  deadline: string;
  status: string;
}

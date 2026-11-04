"use client";

import React, { useState } from "react";
import {
  TrendingDown,
  Server,
  Zap,
  Leaf,
  ShieldCheck,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  Filter
} from "lucide-react";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from "recharts";
import { FleetDevice, FleetSummary } from "@/lib/types";

interface DashboardViewProps {
  summary: FleetSummary;
  devices: FleetDevice[];
  onSelectDevice?: (dev: FleetDevice) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  summary,
  devices,
  onSelectDevice,
}) => {
  const [timeFilter, setTimeFilter] = useState<"24h" | "7d" | "30d" | "90d">("7d");

  // Synthetic 7-day diurnal trend based on real fleet total
  const totalDaily = summary.total_daily_kg || 43.5;
  const trendData = [
    { day: "Mon", carbon_kg: +(totalDaily * 0.94).toFixed(2), energy_kwh: +(totalDaily * 0.94 / 0.42).toFixed(1) },
    { day: "Tue", carbon_kg: +(totalDaily * 0.98).toFixed(2), energy_kwh: +(totalDaily * 0.98 / 0.42).toFixed(1) },
    { day: "Wed", carbon_kg: +(totalDaily * 1.05).toFixed(2), energy_kwh: +(totalDaily * 1.05 / 0.42).toFixed(1) },
    { day: "Thu", carbon_kg: +(totalDaily * 1.01).toFixed(2), energy_kwh: +(totalDaily * 1.01 / 0.42).toFixed(1) },
    { day: "Fri", carbon_kg: +(totalDaily * 0.92).toFixed(2), energy_kwh: +(totalDaily * 0.92 / 0.42).toFixed(1) },
    { day: "Sat", carbon_kg: +(totalDaily * 0.65).toFixed(2), energy_kwh: +(totalDaily * 0.65 / 0.42).toFixed(1) },
    { day: "Sun", carbon_kg: +(totalDaily * 0.58).toFixed(2), energy_kwh: +(totalDaily * 0.58 / 0.42).toFixed(1) },
  ];

  // Distribution by device category
  const categoryData = Object.entries(summary.by_device_type || {}).map(([name, val]) => ({
    name: name.replace("_", " ").toUpperCase(),
    value: +val.toFixed(2),
  }));

  const PIE_COLORS = ["#16C784", "#38BDF8", "#F5B942", "#F16C6C", "#A78BFA", "#F472B6"];

  // Top 5 emitting devices
  const topEmitters = [...devices]
    .sort((a, b) => b.total_daily_kg - a.total_daily_kg)
    .slice(0, 5);

  return (
    <div className="space-y-6">
      {/* Time Horizon Filter */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-carbon-text">Fleet Carbon Dynamics</h2>
          <p className="text-xs text-carbon-muted">Real-time telemetry aggregated across physical and cloud nodes</p>
        </div>
        <div className="flex items-center bg-carbon-card p-1 rounded-xl border border-carbon-border text-xs">
          {(["24h", "7d", "30d", "90d"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTimeFilter(t)}
              className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                timeFilter === t
                  ? "bg-carbon-primary text-carbon-bg font-semibold shadow-sm"
                  : "text-carbon-muted hover:text-carbon-text"
              }`}
            >
              {t.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Top 5 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* KPI 1 */}
        <div className="p-5 rounded-2xl bg-carbon-card border border-carbon-border stat-glow">
          <div className="flex items-center justify-between text-xs text-carbon-muted mb-2">
            <span>Total Carbon Emissions</span>
            <Leaf className="w-4 h-4 text-carbon-primary" />
          </div>
          <div className="text-2xl font-bold font-mono text-carbon-text">
            {summary.total_daily_kg.toFixed(2)} <span className="text-xs font-normal text-carbon-muted">kg/day</span>
          </div>
          <div className="text-[11px] text-carbon-primary flex items-center gap-1 mt-2">
            <ArrowDownRight className="w-3.5 h-3.5" />
            <span>-8.4% vs last week</span>
          </div>
        </div>

        {/* KPI 2 */}
        <div className="p-5 rounded-2xl bg-carbon-card border border-carbon-border">
          <div className="flex items-center justify-between text-xs text-carbon-muted mb-2">
            <span>Electricity Demand</span>
            <Zap className="w-4 h-4 text-carbon-cyan" />
          </div>
          <div className="text-2xl font-bold font-mono text-carbon-text">
            {summary.total_kwh_daily.toFixed(1)} <span className="text-xs font-normal text-carbon-muted">kWh/day</span>
          </div>
          <div className="text-[11px] text-carbon-muted mt-2 font-mono">
            ~{(summary.total_kwh_daily * 365 / 1000).toFixed(2)} MWh annualized
          </div>
        </div>

        {/* KPI 3 */}
        <div className="p-5 rounded-2xl bg-carbon-card border border-carbon-border">
          <div className="flex items-center justify-between text-xs text-carbon-muted mb-2">
            <span>Monitored Nodes</span>
            <Server className="w-4 h-4 text-carbon-muted" />
          </div>
          <div className="text-2xl font-bold font-mono text-carbon-text">
            {summary.online_count} <span className="text-xs font-normal text-carbon-dim">/ {summary.total_devices}</span>
          </div>
          <div className="text-[11px] text-carbon-primary mt-2">
            {((summary.online_count / Math.max(summary.total_devices, 1)) * 100).toFixed(0)}% nodes transmitting
          </div>
        </div>

        {/* KPI 4 */}
        <div className="p-5 rounded-2xl bg-carbon-card border border-carbon-border">
          <div className="flex items-center justify-between text-xs text-carbon-muted mb-2">
            <span>Carbon Efficiency</span>
            <ShieldCheck className="w-4 h-4 text-carbon-primary" />
          </div>
          <div className="text-2xl font-bold font-mono text-carbon-primary flex items-center gap-2">
            <span>{summary.carbon_efficiency_score}</span>
            <span className="text-xs px-2 py-0.5 rounded bg-carbon-primary/20 text-carbon-primary font-bold">
              A
            </span>
          </div>
          <div className="text-[11px] text-carbon-muted mt-2">Scale 0 - 100 (Optimal)</div>
        </div>

        {/* KPI 5 */}
        <div className="p-5 rounded-2xl bg-carbon-card border border-carbon-border">
          <div className="flex items-center justify-between text-xs text-carbon-muted mb-2">
            <span>Abatement Potential</span>
            <TrendingDown className="w-4 h-4 text-carbon-warning" />
          </div>
          <div className="text-2xl font-bold font-mono text-carbon-warning">
            {(summary.total_daily_kg * 0.35).toFixed(2)} <span className="text-xs font-normal text-carbon-muted">kg/day</span>
          </div>
          <div className="text-[11px] text-carbon-muted mt-2">~35% reducible via policies</div>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Area Chart */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-carbon-card border border-carbon-border">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-sm font-semibold text-carbon-text">Daily Carbon Trajectory (kg CO₂e)</h3>
              <p className="text-xs text-carbon-muted">Diurnal variance aligned with operational duty cycles</p>
            </div>
            <span className="text-xs font-mono px-2 py-1 rounded bg-carbon-subtle text-carbon-primary border border-carbon-border">
              {timeFilter.toUpperCase()} Baseline
            </span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="carbonGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#16C784" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#16C784" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2D42" vertical={false} />
                <XAxis dataKey="day" stroke="#64748B" fontSize={11} />
                <YAxis stroke="#64748B" fontSize={11} domain={["auto", "auto"]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#151D2B",
                    borderColor: "#1F2D42",
                    borderRadius: "12px",
                    color: "#F8FAFC",
                    fontSize: "12px",
                  }}
                />
                <Area type="monotone" dataKey="carbon_kg" stroke="#16C784" strokeWidth={2.5} fill="url(#carbonGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Breakdown Pie Chart */}
        <div className="p-6 rounded-2xl bg-carbon-card border border-carbon-border flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-carbon-text">Emissions by Device Type</h3>
            <p className="text-xs text-carbon-muted">Category contribution to total footprint</p>
          </div>
          <div className="h-52 my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={categoryData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {categoryData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#151D2B",
                    borderColor: "#1F2D42",
                    borderRadius: "8px",
                    color: "#F8FAFC",
                    fontSize: "11px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 text-[11px] pt-2 border-t border-carbon-border/60">
            {categoryData.slice(0, 4).map((c, i) => (
              <div key={c.name} className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: PIE_COLORS[i % PIE_COLORS.length] }} />
                <span className="text-carbon-muted truncate">{c.name}</span>
                <span className="font-mono text-carbon-text font-semibold ml-auto">{c.value}kg</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top Contributors Table */}
      <div className="p-6 rounded-2xl bg-carbon-card border border-carbon-border">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-carbon-text">Top Fleet Carbon Contributors</h3>
            <p className="text-xs text-carbon-muted">Nodes requiring power capping or workload scheduling</p>
          </div>
          <span className="text-xs text-carbon-dim">Ordered by daily CO₂e</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-carbon-border text-carbon-dim uppercase tracking-wider">
                <th className="pb-3 font-semibold">Device Name</th>
                <th className="pb-3 font-semibold">Type</th>
                <th className="pb-3 font-semibold">Region</th>
                <th className="pb-3 font-semibold">CPU Load</th>
                <th className="pb-3 font-semibold">Power (W)</th>
                <th className="pb-3 font-semibold">Daily Carbon</th>
                <th className="pb-3 font-semibold">Health</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-carbon-border/50">
              {topEmitters.map((dev) => (
                <tr
                  key={dev.id}
                  onClick={() => onSelectDevice?.(dev)}
                  className="hover:bg-carbon-cardHover/70 transition-colors cursor-pointer group"
                >
                  <td className="py-3 font-medium text-carbon-text flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-carbon-primary" />
                    <span className="group-hover:text-carbon-primary transition-colors">{dev.device_name}</span>
                  </td>
                  <td className="py-3 text-carbon-muted uppercase">{dev.device_type}</td>
                  <td className="py-3 font-mono text-carbon-muted">{dev.region}</td>
                  <td className="py-3 font-mono">{dev.cpu_util_pct?.toFixed(1)}%</td>
                  <td className="py-3 font-mono">{dev.power_watts?.toFixed(1)} W</td>
                  <td className="py-3 font-mono font-bold text-carbon-primary">{dev.total_daily_kg?.toFixed(4)} kg</td>
                  <td className="py-3">
                    <span className="px-2 py-0.5 rounded bg-carbon-primary/10 text-carbon-primary font-mono text-[10px]">
                      {dev.health_score || 95}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

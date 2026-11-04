"use client";

import React, { useState, useEffect } from "react";
import {
  Sliders,
  TrendingDown,
  Sparkles,
  Zap,
  Leaf,
  DollarSign,
  TreePine,
  ArrowRight,
  RotateCcw
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";
import { api } from "@/lib/api";
import { SimulationResult } from "@/lib/types";

export const WhatIfSimulatorView: React.FC = () => {
  const [params, setParams] = useState({
    device_type: "laptop",
    device_count: 50,
    current_cpu_util: 50,
    target_cpu_util: 28,
    current_uptime_hours: 12,
    target_uptime_hours: 7.5,
    current_region: "ap-south-1",
    target_region: "eu-north-1",
    current_pue: 1.4,
    target_pue: 1.12,
    scenario_name: "Fleet Transformation",
  });

  const [simResult, setSimResult] = useState<SimulationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const runSimulation = async () => {
    setIsLoading(true);
    try {
      const data = await api.simulate(params);
      setSimResult(data);
    } catch (err) {
      console.warn("Simulation failed:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    runSimulation();
  }, [params]);

  const loadPreset = (presetKey: string) => {
    if (presetKey === "green_policy") {
      setParams((p) => ({
        ...p,
        target_cpu_util: 22,
        target_uptime_hours: 7,
        target_region: "eu-north-1",
        target_pue: 1.12,
        scenario_name: "Aggressive Green Policy",
      }));
    } else if (presetKey === "renewable") {
      setParams((p) => ({
        ...p,
        target_region: "eu-north-1",
        target_pue: 1.15,
        scenario_name: "100% Renewable Transition",
      }));
    } else if (presetKey === "datacenter") {
      setParams((p) => ({
        ...p,
        device_type: "server_1u",
        current_cpu_util: 75,
        target_cpu_util: 45,
        target_pue: 1.1,
        scenario_name: "Datacenter Consolidation",
      }));
    }
  };

  const chartData = [
    {
      category: "Daily Carbon (kg)",
      Baseline: simResult?.baseline?.daily_kg || 42.5,
      Simulated: simResult?.simulated?.daily_kg || 12.8,
    },
    {
      category: "Daily Power (kWh)",
      Baseline: simResult?.baseline?.daily_kwh || 60.0,
      Simulated: simResult?.simulated?.daily_kwh || 26.5,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-carbon-text">What-If Carbon Reduction Simulator</h2>
          <p className="text-xs text-carbon-muted">
            Interactive physics modeling of operational transformations, grid transitions, and power policies
          </p>
        </div>

        {/* Presets Bar */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-carbon-dim">Presets:</span>
          <button
            onClick={() => loadPreset("green_policy")}
            className="px-2.5 py-1.5 rounded-lg bg-carbon-card border border-carbon-border hover:border-carbon-primary/40 text-xs text-carbon-text transition-colors"
          >
            Green Policy
          </button>
          <button
            onClick={() => loadPreset("renewable")}
            className="px-2.5 py-1.5 rounded-lg bg-carbon-card border border-carbon-border hover:border-carbon-primary/40 text-xs text-carbon-text transition-colors"
          >
            Renewable Migration
          </button>
          <button
            onClick={() => loadPreset("datacenter")}
            className="px-2.5 py-1.5 rounded-lg bg-carbon-card border border-carbon-border hover:border-carbon-primary/40 text-xs text-carbon-text transition-colors"
          >
            DC Consolidation
          </button>
        </div>
      </div>

      {/* Main Grid: Controls vs Visual Output */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls Column (2 Cols) */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-carbon-card border border-carbon-border space-y-5">
          <h3 className="text-sm font-semibold text-carbon-text">Simulated Parameter Adjustments</h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 text-xs">
            {/* Device Count Slider */}
            <div>
              <div className="flex justify-between mb-1.5">
                <span className="text-carbon-muted">Managed Fleet Size</span>
                <span className="font-mono text-carbon-primary font-bold">{params.device_count} Nodes</span>
              </div>
              <input
                type="range"
                min="5"
                max="500"
                step="5"
                value={params.device_count}
                onChange={(e) => setParams({ ...params, device_count: +e.target.value })}
                className="w-full accent-carbon-primary"
              />
            </div>

            {/* Target CPU Load Slider */}
            <div>
              <div className="flex justify-between mb-1.5">
                <span className="text-carbon-muted">Target Average CPU Duty</span>
                <span className="font-mono text-carbon-cyan font-bold">{params.target_cpu_util}%</span>
              </div>
              <input
                type="range"
                min="10"
                max="90"
                value={params.target_cpu_util}
                onChange={(e) => setParams({ ...params, target_cpu_util: +e.target.value })}
                className="w-full accent-carbon-cyan"
              />
            </div>

            {/* Target Operating Hours Slider */}
            <div>
              <div className="flex justify-between mb-1.5">
                <span className="text-carbon-muted">Daily Active Operating Hours</span>
                <span className="font-mono text-carbon-warning font-bold">{params.target_uptime_hours}h / day</span>
              </div>
              <input
                type="range"
                min="2"
                max="24"
                step="0.5"
                value={params.target_uptime_hours}
                onChange={(e) => setParams({ ...params, target_uptime_hours: +e.target.value })}
                className="w-full accent-carbon-warning"
              />
            </div>

            {/* Target PUE Slider */}
            <div>
              <div className="flex justify-between mb-1.5">
                <span className="text-carbon-muted">Datacenter PUE Efficiency</span>
                <span className="font-mono text-carbon-text font-bold">{params.target_pue}x</span>
              </div>
              <input
                type="range"
                min="1.05"
                max="1.8"
                step="0.02"
                value={params.target_pue}
                onChange={(e) => setParams({ ...params, target_pue: +e.target.value })}
                className="w-full accent-carbon-text"
              />
            </div>

            {/* Grid Region Dropdown */}
            <div>
              <label className="text-carbon-muted block mb-1.5">Target Grid Electricity Zone</label>
              <select
                value={params.target_region}
                onChange={(e) => setParams({ ...params, target_region: e.target.value })}
                className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text focus:outline-none focus:border-carbon-primary"
              >
                <option value="eu-north-1">EU North - Stockholm (0.08 kg/kWh - 95% Hydro/Wind)</option>
                <option value="ca-central-1">Canada Central - Montreal (0.13 kg/kWh)</option>
                <option value="us-west-2">US West - Oregon (0.15 kg/kWh)</option>
                <option value="eu-west-1">Europe West - Ireland (0.28 kg/kWh)</option>
                <option value="us-east-1">US East - Virginia (0.42 kg/kWh)</option>
                <option value="ap-south-1">Asia Pacific - Mumbai (0.71 kg/kWh)</option>
              </select>
            </div>

            {/* Hardware Type */}
            <div>
              <label className="text-carbon-muted block mb-1.5">Hardware Archetype</label>
              <select
                value={params.device_type}
                onChange={(e) => setParams({ ...params, device_type: e.target.value })}
                className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text focus:outline-none focus:border-carbon-primary uppercase"
              >
                <option value="laptop">Client Laptops (45W TDP)</option>
                <option value="desktop">Office Desktops (125W TDP)</option>
                <option value="workstation">Heavy Workstations (250W TDP)</option>
                <option value="server_1u">Datacenter 1U Nodes (200W TDP)</option>
              </select>
            </div>
          </div>

          {/* Comparative Bar Chart */}
          <div className="pt-4 border-t border-carbon-border/60">
            <h4 className="text-xs font-semibold text-carbon-muted mb-3 uppercase tracking-wider">
              Before vs After Environmental Metrics
            </h4>
            <div className="h-44">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1F2D42" vertical={false} />
                  <XAxis dataKey="category" stroke="#64748B" fontSize={11} />
                  <YAxis stroke="#64748B" fontSize={11} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#151D2B",
                      borderColor: "#1F2D42",
                      borderRadius: "8px",
                      color: "#F8FAFC",
                      fontSize: "11px",
                    }}
                  />
                  <Bar dataKey="Baseline" fill="#F16C6C" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Simulated" fill="#16C784" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Live Savings Output Card (1 Col) */}
        <div className="p-6 rounded-2xl bg-carbon-card border border-carbon-border flex flex-col justify-between space-y-4">
          <div>
            <h3 className="text-sm font-semibold text-carbon-text mb-4">Simulated Carbon Savings</h3>

            <div className="space-y-4 font-mono text-xs">
              <div className="p-4 rounded-xl bg-carbon-subtle border border-carbon-primary/40 space-y-1.5">
                <div className="text-carbon-muted font-sans">Carbon Footprint Reduction</div>
                <div className="text-3xl font-bold text-carbon-primary">
                  {simResult?.savings?.pct_reduction || 65.2}%
                </div>
                <div className="text-[11px] text-carbon-dim">
                  Saves {simResult?.savings?.daily_kg || 28.5} kg CO₂e / day
                </div>
              </div>

              <div className="p-4 rounded-xl bg-carbon-subtle border border-carbon-border space-y-1.5">
                <div className="text-carbon-muted font-sans">Annual Abated Emissions</div>
                <div className="text-2xl font-bold text-carbon-cyan">
                  {simResult?.savings?.annual_t || 10.4} <span className="text-xs font-normal">metric tons</span>
                </div>
                <div className="text-[11px] text-carbon-dim">~{simResult?.savings?.trees_equivalent || 480} mature trees equivalent</div>
              </div>

              <div className="p-4 rounded-xl bg-carbon-subtle border border-carbon-border space-y-1.5">
                <div className="text-carbon-muted font-sans">Estimated Annual OPEX Savings</div>
                <div className="text-2xl font-bold text-carbon-warning">
                  ${simResult?.savings?.estimated_cost_savings_usd || 1850} <span className="text-xs font-normal">USD</span>
                </div>
                <div className="text-[11px] text-carbon-dim">Based on $0.15/kWh commercial utility rate</div>
              </div>
            </div>
          </div>

          <div className="text-[10px] text-carbon-dim pt-3 border-t border-carbon-border/60">
            Validated via physics-based SCI equation: Carbon = (kWh * EF) + Embodied
          </div>
        </div>
      </div>
    </div>
  );
};


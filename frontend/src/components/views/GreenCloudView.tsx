"use client";

import React, { useState, useEffect } from "react";
import {
  Cloud,
  Globe2,
  Clock,
  Zap,
  Leaf,
  CheckCircle2,
  ArrowRight,
  TrendingDown
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";
import { api } from "@/lib/api";
import { CloudRegionComparison } from "@/lib/types";

export const GreenCloudView: React.FC = () => {
  const [regions, setRegions] = useState<CloudRegionComparison[]>([]);
  const [scheduleResult, setScheduleResult] = useState<any>(null);
  const [jobParams, setJobParams] = useState({
    job_name: "Nightly Analytics Pipeline",
    duration_hours: 4.0,
    vcpus: 16,
    memory_gb: 64.0,
    preferred_region: "ap-south-1",
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadCloudData = async () => {
      try {
        const data = await api.getCloudComparison();
        setRegions(data.regions || []);

        const sched = await api.scheduleCloudJob(jobParams);
        setScheduleResult(sched);
      } catch (err) {
        console.warn("Failed to load cloud intelligence:", err);
      } finally {
        setIsLoading(false);
      }
    };
    loadCloudData();
  }, []);

  const handleSimulateSchedule = async () => {
    try {
      const sched = await api.scheduleCloudJob(jobParams);
      setScheduleResult(sched);
    } catch (err: any) {
      alert(`Scheduling error: ${err.message}`);
    }
  };

  const timelineData = scheduleResult?.hourly_timeline?.map((h: any) => ({
    hour: `${h.hour}:00`,
    carbon_kg: h.job_carbon_kg,
    factor: h.emission_factor,
  })) || [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-carbon-text">Green Cloud Intelligence & Scheduling</h2>
        <p className="text-xs text-carbon-muted">
          Global cloud provider matrix and carbon-aware batch workload scheduling simulator
        </p>
      </div>

      {/* Carbon-Aware Scheduler Simulator Card */}
      <div className="p-6 rounded-2xl bg-carbon-card border border-carbon-border space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-carbon-primary/15 flex items-center justify-center text-carbon-primary">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-carbon-text">Carbon-Aware Job Scheduling Simulator</h3>
              <p className="text-xs text-carbon-muted">
                Aligns computational bursts with peak diurnal solar and wind grid supply to minimize grams CO₂e
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs px-2.5 py-1 rounded-lg bg-carbon-primary/10 text-carbon-primary font-mono font-bold">
              Time-Shift Savings: {scheduleResult?.time_shift_savings_pct || 28.0}%
            </span>
          </div>
        </div>

        {/* Inputs & Hourly Curve */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Inputs */}
          <div className="p-4 rounded-xl bg-carbon-subtle border border-carbon-border space-y-3 text-xs">
            <div>
              <label className="text-carbon-muted block mb-1">Batch Job Name</label>
              <input
                type="text"
                value={jobParams.job_name}
                onChange={(e) => setJobParams({ ...jobParams, job_name: e.target.value })}
                className="w-full bg-carbon-bg border border-carbon-border rounded-lg px-3 py-1.5 text-carbon-text font-mono"
              />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-carbon-muted block mb-1">Duration (Hours)</label>
                <input
                  type="number"
                  value={jobParams.duration_hours}
                  onChange={(e) => setJobParams({ ...jobParams, duration_hours: +e.target.value })}
                  className="w-full bg-carbon-bg border border-carbon-border rounded-lg px-3 py-1.5 text-carbon-text font-mono"
                />
              </div>
              <div>
                <label className="text-carbon-muted block mb-1">vCPUs</label>
                <input
                  type="number"
                  value={jobParams.vcpus}
                  onChange={(e) => setJobParams({ ...jobParams, vcpus: +e.target.value })}
                  className="w-full bg-carbon-bg border border-carbon-border rounded-lg px-3 py-1.5 text-carbon-text font-mono"
                />
              </div>
            </div>
            <div>
              <label className="text-carbon-muted block mb-1">Base Region</label>
              <select
                value={jobParams.preferred_region}
                onChange={(e) => setJobParams({ ...jobParams, preferred_region: e.target.value })}
                className="w-full bg-carbon-bg border border-carbon-border rounded-lg px-3 py-1.5 text-carbon-text"
              >
                <option value="ap-south-1">Asia Pacific (Mumbai - 0.71 kg/kWh)</option>
                <option value="us-east-1">US East (Virginia - 0.42 kg/kWh)</option>
                <option value="eu-west-1">Europe West (Ireland - 0.28 kg/kWh)</option>
              </select>
            </div>
            <button
              onClick={handleSimulateSchedule}
              className="w-full mt-2 py-2 rounded-lg bg-carbon-primary text-carbon-bg font-semibold text-xs hover:bg-carbon-primaryHover transition-colors"
            >
              Simulate 24h Carbon Opportunity
            </button>
          </div>

          {/* Diurnal Carbon Chart */}
          <div className="lg:col-span-2 flex flex-col justify-between">
            <div>
              <div className="flex justify-between text-xs text-carbon-muted mb-2 font-mono">
                <span>Diurnal Grid Intensity Curve (24h)</span>
                <span className="text-carbon-primary font-semibold">
                  Optimal Window: {scheduleResult?.recommended_window?.start_time || "12:00 UTC"}
                </span>
              </div>
              <div className="h-44">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={timelineData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1F2D42" vertical={false} />
                    <XAxis dataKey="hour" stroke="#64748B" fontSize={10} />
                    <YAxis stroke="#64748B" fontSize={10} unit="kg" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#151D2B",
                        borderColor: "#1F2D42",
                        borderRadius: "8px",
                        color: "#F8FAFC",
                        fontSize: "11px",
                      }}
                    />
                    <Area type="monotone" dataKey="carbon_kg" stroke="#16C784" strokeWidth={2} fill="#16C784" fillOpacity={0.15} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="pt-3 border-t border-carbon-border/50 flex items-center justify-between text-xs font-mono">
              <span className="text-carbon-muted">Unoptimized: {scheduleResult?.unoptimized_carbon_kg} kg</span>
              <span className="text-carbon-primary font-bold">Time-Shifted: {scheduleResult?.time_shifted_carbon_kg} kg</span>
              <span className="text-carbon-cyan">Geo-Shift (Stockholm): {scheduleResult?.geo_shift_alternative?.carbon_kg} kg (-{scheduleResult?.geo_shift_alternative?.savings_pct}%)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Cloud Regions Comparison Table */}
      <div className="p-6 rounded-2xl bg-carbon-card border border-carbon-border">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-carbon-text">Global Cloud Carbon Comparison</h3>
            <p className="text-xs text-carbon-muted">Normalized for 8 vCPU, 32GB RAM compute instance (24h continuous)</p>
          </div>
          <span className="text-xs text-carbon-dim">Ordered by carbon cleanliness</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-carbon-border text-carbon-dim uppercase tracking-wider">
                <th className="pb-3 font-semibold">Cloud Region</th>
                <th className="pb-3 font-semibold">Grid Factor (kg/kWh)</th>
                <th className="pb-3 font-semibold">Renewables</th>
                <th className="pb-3 font-semibold">Datacenter PUE</th>
                <th className="pb-3 font-semibold">Daily Energy</th>
                <th className="pb-3 font-semibold">Daily Carbon</th>
                <th className="pb-3 font-semibold">Green Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-carbon-border/40 font-mono">
              {regions.map((reg) => (
                <tr key={reg.region_key} className="hover:bg-carbon-cardHover transition-colors">
                  <td className="py-3 font-sans font-medium text-carbon-text flex items-center gap-2">
                    <Globe2 className="w-3.5 h-3.5 text-carbon-muted" />
                    <span>{reg.name}</span>
                    <span className="text-[10px] text-carbon-dim">({reg.region_key})</span>
                  </td>
                  <td className="py-3 text-carbon-text">{reg.emission_factor_kg_kwh.toFixed(2)}</td>
                  <td className="py-3 text-carbon-primary">{reg.renewable_pct}%</td>
                  <td className="py-3 text-carbon-muted">{reg.typical_pue.toFixed(2)}x</td>
                  <td className="py-3 text-carbon-muted">{reg.daily_kwh.toFixed(2)} kWh</td>
                  <td className="py-3 font-bold text-carbon-primary">{reg.daily_kg_co2.toFixed(3)} kg</td>
                  <td className="py-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      reg.green_score >= 80 ? "bg-carbon-primary/15 text-carbon-primary" : "bg-carbon-warning/15 text-carbon-warning"
                    }`}>
                      {reg.green_score} / 100
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

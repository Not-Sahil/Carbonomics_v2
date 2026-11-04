"use client";

import React, { useState, useEffect } from "react";
import {
  Sparkles,
  TrendingDown,
  CheckCircle2,
  Clock,
  ArrowRight,
  Layers,
  Zap,
  Filter,
  Check,
  X
} from "lucide-react";
import { api } from "@/lib/api";
import { OptimizationRec } from "@/lib/types";

export const OptimizationCenterView: React.FC = () => {
  const [recommendations, setRecommendations] = useState<OptimizationRec[]>([]);
  const [totalSavingsKg, setTotalSavingsKg] = useState(0);
  const [totalSavingsKwh, setTotalSavingsKwh] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  const fetchRecs = async () => {
    setIsLoading(true);
    try {
      const data = await api.getRecommendations();
      setRecommendations(data.recommendations || []);
      setTotalSavingsKg(data.potential_savings_kg || 0);
      setTotalSavingsKwh(data.potential_savings_kwh || 0);
    } catch (err) {
      console.warn("Failed to load optimization recommendations:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRecs();
  }, []);

  const handleStatusChange = (id: string | number, newStatus: string) => {
    setRecommendations((prev) =>
      prev.map((r) => (r.id === id ? { ...r, status: newStatus } : r))
    );
  };

  return (
    <div className="space-y-6">
      {/* View Header & Total Savings Banner */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-carbon-card via-carbon-cardHover to-carbon-card border border-carbon-border flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-carbon-warning animate-pulse" />
            <span className="text-xs font-semibold text-carbon-warning uppercase tracking-wider">
              Optimization Opportunities Identified
            </span>
          </div>
          <h2 className="text-2xl font-bold text-carbon-text">Fleet Carbon Abatement Center</h2>
          <p className="text-xs text-carbon-muted mt-1 max-w-xl">
            Prioritized by environmental impact and implementation complexity. Simulates operational changes before deployment.
          </p>
        </div>

        <div className="flex items-center gap-4 bg-carbon-subtle/70 p-4 rounded-2xl border border-carbon-border">
          <div>
            <div className="text-[11px] text-carbon-muted">Potential Abatement</div>
            <div className="text-2xl font-bold font-mono text-carbon-primary">
              {totalSavingsKg.toFixed(2)} <span className="text-xs font-normal text-carbon-muted">kg/day</span>
            </div>
            <div className="text-[10px] text-carbon-dim">~{(totalSavingsKg * 365 / 1000).toFixed(2)} tons annual reduction</div>
          </div>
          <div className="w-px h-10 bg-carbon-border" />
          <div>
            <div className="text-[11px] text-carbon-muted">Electricity Savings</div>
            <div className="text-2xl font-bold font-mono text-carbon-cyan">
              {totalSavingsKwh.toFixed(1)} <span className="text-xs font-normal text-carbon-muted">kWh/day</span>
            </div>
            <div className="text-[10px] text-carbon-dim font-mono">~${(totalSavingsKwh * 365 * 0.15).toFixed(0)}/yr cost cut</div>
          </div>
        </div>
      </div>

      {/* Recommendations Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {recommendations.map((rec) => (
          <div
            key={rec.id}
            className="p-6 rounded-2xl bg-carbon-card border border-carbon-border flex flex-col justify-between space-y-4 hover:border-carbon-primary/40 transition-all"
          >
            <div>
              {/* Category & Badges */}
              <div className="flex items-center justify-between mb-3 text-xs">
                <span className="px-2.5 py-1 rounded-lg bg-carbon-subtle text-carbon-text border border-carbon-border font-medium">
                  {rec.category}
                </span>

                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                    rec.priority === "high"
                      ? "bg-carbon-danger/15 text-carbon-danger border border-carbon-danger/30"
                      : "bg-carbon-warning/15 text-carbon-warning border border-carbon-warning/30"
                  }`}>
                    {rec.priority} Priority
                  </span>
                  <span className="px-2 py-0.5 rounded bg-carbon-subtle text-carbon-muted text-[10px] font-medium border border-carbon-border">
                    {rec.effort} Effort
                  </span>
                </div>
              </div>

              {/* Title & Description */}
              <h3 className="text-base font-bold text-carbon-text mb-2">{rec.title}</h3>
              <p className="text-xs text-carbon-muted leading-relaxed mb-4">{rec.description}</p>

              {/* Implementation Steps */}
              {rec.steps && rec.steps.length > 0 && (
                <div className="p-3.5 rounded-xl bg-carbon-subtle border border-carbon-border/70 space-y-2 text-xs">
                  <div className="text-[10px] font-semibold text-carbon-dim uppercase tracking-wider">
                    Recommended Implementation Protocol:
                  </div>
                  <ul className="space-y-1.5 text-carbon-text">
                    {rec.steps.map((st, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-carbon-primary flex-shrink-0 mt-0.5" />
                        <span className="text-[11px]">{st}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Bottom Actions & Status */}
            <div className="pt-4 border-t border-carbon-border/60 flex items-center justify-between text-xs">
              <div className="font-mono">
                <span className="text-carbon-muted">Savings: </span>
                <span className="text-carbon-primary font-bold">{rec.potential_savings_kg?.toFixed(2)} kg/day</span>
                <span className="text-carbon-dim"> ({rec.potential_savings_kwh?.toFixed(1)} kWh)</span>
              </div>

              <div className="flex items-center gap-2">
                {rec.status === "completed" ? (
                  <span className="px-3 py-1.5 rounded-lg bg-carbon-primary/20 text-carbon-primary font-semibold flex items-center gap-1.5">
                    <Check className="w-3.5 h-3.5" /> Completed
                  </span>
                ) : rec.status === "accepted" ? (
                  <button
                    onClick={() => handleStatusChange(rec.id, "completed")}
                    className="px-3 py-1.5 rounded-lg bg-carbon-primary text-carbon-bg font-semibold hover:bg-carbon-primaryHover transition-colors flex items-center gap-1.5 shadow-sm"
                  >
                    <span>Mark Applied</span>
                  </button>
                ) : (
                  <button
                    onClick={() => handleStatusChange(rec.id, "accepted")}
                    className="px-3 py-1.5 rounded-lg bg-carbon-primary/15 text-carbon-primary border border-carbon-primary/30 font-semibold hover:bg-carbon-primary/25 transition-colors"
                  >
                    Accept Action
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

"use client";

import React from "react";
import {
  ArrowRight,
  ShieldCheck,
  Cpu,
  BrainCircuit,
  Cloud,
  TrendingDown,
  Sparkles,
  Zap,
  Globe2,
  Server
} from "lucide-react";
import { ViewTab } from "../Sidebar";

interface LandingViewProps {
  onExplore: (tab: ViewTab) => void;
  fleetCount: number;
  fleetDailyKg: number;
}

export const LandingView: React.FC<LandingViewProps> = ({
  onExplore,
  fleetCount,
  fleetDailyKg,
}) => {
  return (
    <div className="space-y-16 py-8 px-2 max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="relative text-center space-y-6 pt-12 pb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-carbon-card border border-carbon-border text-xs text-carbon-muted">
          <span className="w-2 h-2 rounded-full bg-carbon-primary animate-pulse" />
          <span>Carbonomics v3 Enterprise Intelligence Platform</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-carbon-text leading-tight max-w-4xl mx-auto">
          Understand Your Carbon. <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-carbon-primary via-emerald-400 to-carbon-cyan">
            Optimize Your Future.
          </span>
        </h1>

        <p className="text-base md:text-lg text-carbon-muted max-w-2xl mx-auto leading-relaxed">
          An intelligent carbon intelligence platform that monitors digital infrastructure,
          predicts emissions via physics-based SCI models and machine learning, and helps organizations
          build verifiable green computing environments.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <button
            onClick={() => onExplore("dashboard")}
            className="flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-carbon-primary hover:bg-carbon-primaryHover text-carbon-bg font-semibold text-sm shadow-xl shadow-carbon-primary/20 transition-all hover:scale-[1.02]"
          >
            <span>Explore Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => onExplore("simulator")}
            className="flex items-center gap-2.5 px-6 py-3.5 rounded-xl bg-carbon-card hover:bg-carbon-cardHover border border-carbon-border text-carbon-text font-semibold text-sm transition-all"
          >
            <span>Launch What-If Simulator</span>
          </button>
        </div>

        {/* Live Metrics Floating Bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto pt-10">
          <div className="p-4 rounded-xl bg-carbon-card/80 border border-carbon-border text-left">
            <div className="text-xs text-carbon-muted">Active Fleet Nodes</div>
            <div className="text-2xl font-bold font-mono text-carbon-text mt-1">{fleetCount}</div>
            <div className="text-[11px] text-carbon-primary mt-0.5">Real-time telemetry</div>
          </div>
          <div className="p-4 rounded-xl bg-carbon-card/80 border border-carbon-border text-left">
            <div className="text-xs text-carbon-muted">Daily Carbon Run-Rate</div>
            <div className="text-2xl font-bold font-mono text-carbon-primary mt-1">{fleetDailyKg.toFixed(1)} <span className="text-xs font-normal">kg</span></div>
            <div className="text-[11px] text-carbon-muted mt-0.5">GSF-SCI compliant</div>
          </div>
          <div className="p-4 rounded-xl bg-carbon-card/80 border border-carbon-border text-left">
            <div className="text-xs text-carbon-muted">ML Model Accuracy</div>
            <div className="text-2xl font-bold font-mono text-carbon-cyan mt-1">97.8% <span className="text-xs font-normal">R²</span></div>
            <div className="text-[11px] text-carbon-muted mt-0.5">Dual-stage regressor</div>
          </div>
          <div className="p-4 rounded-xl bg-carbon-card/80 border border-carbon-border text-left">
            <div className="text-xs text-carbon-muted">Identified Savings</div>
            <div className="text-2xl font-bold font-mono text-carbon-warning mt-1">42.5%</div>
            <div className="text-[11px] text-carbon-muted mt-0.5">Prioritized actions</div>
          </div>
        </div>
      </div>

      {/* Core Architectural Pillars */}
      <div className="space-y-6">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-carbon-text">Enterprise Capabilities</h2>
          <p className="text-sm text-carbon-muted max-w-xl mx-auto">
            From endpoint hardware telemetry to global datacenter cloud optimization.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <div
            onClick={() => onExplore("live")}
            className="p-6 rounded-2xl bg-carbon-card border border-carbon-border hover:border-carbon-primary/40 transition-all cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-carbon-primary/10 border border-carbon-primary/20 flex items-center justify-center text-carbon-primary mb-4 group-hover:scale-110 transition-transform">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-carbon-text mb-2">Live Hardware Telemetry</h3>
            <p className="text-xs text-carbon-muted leading-relaxed">
              Native cross-platform device agent streaming CPU TDP curves, RAM wattage, disk I/O, GPU utilization, and thermal states every 3 seconds.
            </p>
          </div>

          <div
            onClick={() => onExplore("ai")}
            className="p-6 rounded-2xl bg-carbon-card border border-carbon-border hover:border-carbon-primary/40 transition-all cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-carbon-cyan/10 border border-carbon-cyan/20 flex items-center justify-center text-carbon-cyan mb-4 group-hover:scale-110 transition-transform">
              <BrainCircuit className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-carbon-text mb-2">Machine Learning & SHAP</h3>
            <p className="text-xs text-carbon-muted leading-relaxed">
              GradientBoosting and Random Forest regressors, calibrated Isolation Forest anomaly detection, K-Means device clustering, and explainable AI feature attribution.
            </p>
          </div>

          <div
            onClick={() => onExplore("cloud")}
            className="p-6 rounded-2xl bg-carbon-card border border-carbon-border hover:border-carbon-primary/40 transition-all cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-xl bg-carbon-warning/10 border border-carbon-warning/20 flex items-center justify-center text-carbon-warning mb-4 group-hover:scale-110 transition-transform">
              <Cloud className="w-5 h-5" />
            </div>
            <h3 className="text-base font-semibold text-carbon-text mb-2">Green Cloud Intelligence</h3>
            <p className="text-xs text-carbon-muted leading-relaxed">
              Global emission factor matrix across AWS, GCP, and Azure with a Carbon-Aware Batch Scheduler that time-shifts jobs to align with renewable peaks.
            </p>
          </div>
        </div>
      </div>

      {/* Bottom CTA Banner */}
      <div className="p-8 rounded-3xl bg-gradient-to-r from-carbon-card via-carbon-cardHover to-carbon-card border border-carbon-border flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2">
          <h3 className="text-xl font-bold text-carbon-text">Ready to reduce your digital carbon footprint?</h3>
          <p className="text-xs text-carbon-muted">
            Access real-time fleet analytics, simulate grid migrations, and export GHG protocol reports.
          </p>
        </div>
        <button
          onClick={() => onExplore("dashboard")}
          className="flex items-center gap-2 px-6 py-3 rounded-xl bg-carbon-primary hover:bg-carbon-primaryHover text-carbon-bg font-semibold text-sm transition-all whitespace-nowrap shadow-lg shadow-carbon-primary/20"
        >
          <span>Launch Dashboard</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

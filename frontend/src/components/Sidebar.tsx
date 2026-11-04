"use client";

import React from "react";
import {
  LayoutDashboard,
  Activity,
  Server,
  Calculator,
  BrainCircuit,
  TrendingUp,
  Sparkles,
  Sliders,
  Cloud,
  FileSpreadsheet,
  Settings,
  Leaf,
  Layers
} from "lucide-react";

export type ViewTab =
  | "landing"
  | "dashboard"
  | "live"
  | "fleet"
  | "estimator"
  | "ai"
  | "forecasting"
  | "optimization"
  | "simulator"
  | "cloud"
  | "reports"
  | "settings";

interface SidebarProps {
  activeTab: ViewTab;
  setActiveTab: (tab: ViewTab) => void;
  fleetDailyKg: number;
  onlineCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  fleetDailyKg,
  onlineCount,
}) => {
  const navItems = [
    { id: "dashboard", label: "Executive Overview", icon: LayoutDashboard },
    { id: "live", label: "Live Telemetry", icon: Activity },
    { id: "fleet", label: "Fleet Inventory", icon: Server },
    { id: "estimator", label: "Carbon Estimator", icon: Calculator },
    { id: "ai", label: "AI Insights & SHAP", icon: BrainCircuit },
    { id: "forecasting", label: "Predictive Forecasting", icon: TrendingUp },
    { id: "optimization", label: "Optimization Center", icon: Sparkles },
    { id: "simulator", label: "What-If Simulator", icon: Sliders },
    { id: "cloud", label: "Green Cloud Intel", icon: Cloud },
    { id: "reports", label: "ESG Reports & Scopes", icon: FileSpreadsheet },
    { id: "settings", label: "Platform Settings", icon: Settings },
  ];

  return (
    <aside className="w-64 h-screen bg-carbon-subtle border-r border-carbon-border flex flex-col flex-shrink-0 select-none z-30">
      {/* Brand Header */}
      <div
        onClick={() => setActiveTab("landing")}
        className="p-5 border-b border-carbon-border flex items-center gap-3 cursor-pointer hover:bg-carbon-card/50 transition-colors"
      >
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-carbon-primary to-emerald-600 flex items-center justify-center text-carbon-bg shadow-lg shadow-carbon-primary/20">
          <Leaf className="w-5 h-5 text-carbon-bg" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-base tracking-tight text-carbon-text">CARBONOMICS</span>
            <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-carbon-primary/20 text-carbon-primary border border-carbon-primary/30">
              v3.0
            </span>
          </div>
          <p className="text-xs text-carbon-muted">Carbon Intelligence SaaS</p>
        </div>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-carbon-dim">
          Core Platform
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id as ViewTab)}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? "bg-carbon-primary/15 text-carbon-primary border border-carbon-primary/30 shadow-sm"
                  : "text-carbon-muted hover:text-carbon-text hover:bg-carbon-card/60"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-carbon-primary" : "text-carbon-dim"}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      {/* Fleet Live Status Box */}
      <div className="p-3 m-3 rounded-xl bg-carbon-card border border-carbon-border/80">
        <div className="flex items-center justify-between text-xs text-carbon-muted mb-2">
          <span className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-carbon-primary animate-pulse" />
            Live Fleet Active
          </span>
          <span className="font-mono text-carbon-text">{onlineCount} Nodes</span>
        </div>
        <div className="text-xl font-bold font-mono text-carbon-primary">
          {fleetDailyKg.toFixed(2)} <span className="text-xs font-normal text-carbon-muted">kg CO₂e/day</span>
        </div>
        <div className="text-[11px] text-carbon-dim mt-1">
          ~{(fleetDailyKg * 365 / 1000).toFixed(2)} tons annual run-rate
        </div>
      </div>
    </aside>
  );
};


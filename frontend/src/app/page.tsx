"use client";

import React, { useState, useEffect } from "react";
import { Sidebar, ViewTab } from "@/components/Sidebar";
import { Header } from "@/components/Header";
import { AiAdvisorDrawer } from "@/components/AiAdvisorDrawer";

// Views
import { LandingView } from "@/components/views/LandingView";
import { DashboardView } from "@/components/views/DashboardView";
import { LiveTelemetryView } from "@/components/views/LiveTelemetryView";
import { FleetInventoryView } from "@/components/views/FleetInventoryView";
import { CarbonEstimatorView } from "@/components/views/CarbonEstimatorView";
import { AiInsightsView } from "@/components/views/AiInsightsView";
import { ForecastingView } from "@/components/views/ForecastingView";
import { OptimizationCenterView } from "@/components/views/OptimizationCenterView";
import { WhatIfSimulatorView } from "@/components/views/WhatIfSimulatorView";
import { GreenCloudView } from "@/components/views/GreenCloudView";
import { ReportsView } from "@/components/views/ReportsView";
import { SettingsView } from "@/components/views/SettingsView";

import { api } from "@/lib/api";
import { FleetDevice, FleetSummary } from "@/lib/types";

export default function Home() {
  const [activeTab, setActiveTab] = useState<ViewTab>("landing");
  const [isAdvisorOpen, setIsAdvisorOpen] = useState(false);
  const [devices, setDevices] = useState<FleetDevice[]>([]);
  const [summary, setSummary] = useState<FleetSummary>({
    total_devices: 35,
    online_count: 26,
    offline_count: 9,
    total_daily_kg: 43.36,
    total_annual_kg: 15826.4,
    total_annual_t: 15.83,
    total_kwh_daily: 68.4,
    avg_daily_kg: 1.24,
    by_device_type: { laptop: 5.2, desktop: 8.4, workstation: 14.1, server_1u: 15.6 },
    highest: "Hardware-Node-Server-3",
    trees_to_offset: 726,
    carbon_efficiency_score: 82.5,
  });

  const loadFleetData = async () => {
    try {
      const res = await api.getFleetDevices();
      if (res.devices) setDevices(res.devices);
      if (res.summary && res.summary.total_devices > 0) setSummary(res.summary);
    } catch (err) {
      console.warn("Could not reach backend API, using cached baseline:", err);
    }
  };

  useEffect(() => {
    loadFleetData();
    const interval = setInterval(loadFleetData, 15000);
    return () => clearInterval(interval);
  }, []);

  const titles: Record<ViewTab, { title: string; subtitle: string }> = {
    landing: { title: "Carbonomics v3", subtitle: "Intelligent Carbon Intelligence Platform" },
    dashboard: { title: "Executive Overview", subtitle: "Fleet-wide emissions and energy telemetry" },
    live: { title: "Live Telemetry", subtitle: "Real-time client hardware power monitoring" },
    fleet: { title: "Fleet Inventory", subtitle: "Multi-device registry and node management" },
    estimator: { title: "Carbon Estimator", subtitle: "Physics-based SCI emissions calculator" },
    ai: { title: "AI Insights & SHAP", subtitle: "Machine learning benchmarks and explainability" },
    forecasting: { title: "Predictive Forecasting", subtitle: "Autoregressive time-series trajectory" },
    optimization: { title: "Optimization Center", subtitle: "Prioritized carbon abatement protocols" },
    simulator: { title: "What-If Simulator", subtitle: "Interactive scenario and policy modeling" },
    cloud: { title: "Green Cloud Intel", subtitle: "Cloud regions and carbon-aware batch scheduler" },
    reports: { title: "ESG Reporting & Scopes", subtitle: "GHG protocol accounting and verified exports" },
    settings: { title: "Platform Settings", subtitle: "Organization governance and agent deployment" },
  };

  return (
    <div className="flex h-screen bg-carbon-bg text-carbon-text overflow-hidden font-sans">
      {/* Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        fleetDailyKg={summary.total_daily_kg}
        onlineCount={summary.online_count}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header
          title={titles[activeTab].title}
          subtitle={titles[activeTab].subtitle}
          onOpenAdvisor={() => setIsAdvisorOpen(true)}
          onlineCount={summary.online_count}
        />

        <main className="flex-1 overflow-y-auto p-8">
          {activeTab === "landing" && (
            <LandingView
              onExplore={(tab) => setActiveTab(tab)}
              fleetCount={summary.total_devices}
              fleetDailyKg={summary.total_daily_kg}
            />
          )}
          {activeTab === "dashboard" && <DashboardView summary={summary} devices={devices} />}
          {activeTab === "live" && <LiveTelemetryView />}
          {activeTab === "fleet" && <FleetInventoryView devices={devices} onRefresh={loadFleetData} />}
          {activeTab === "estimator" && <CarbonEstimatorView />}
          {activeTab === "ai" && <AiInsightsView />}
          {activeTab === "forecasting" && <ForecastingView />}
          {activeTab === "optimization" && <OptimizationCenterView />}
          {activeTab === "simulator" && <WhatIfSimulatorView />}
          {activeTab === "cloud" && <GreenCloudView />}
          {activeTab === "reports" && <ReportsView />}
          {activeTab === "settings" && <SettingsView />}
        </main>
      </div>

      {/* AI Carbon Advisor Slide-Over Drawer */}
      <AiAdvisorDrawer isOpen={isAdvisorOpen} onClose={() => setIsAdvisorOpen(false)} />
    </div>
  );
}

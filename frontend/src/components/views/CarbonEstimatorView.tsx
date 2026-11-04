"use client";

import React, { useState } from "react";
import {
  Calculator,
  Server,
  Cloud,
  FileSpreadsheet,
  Zap,
  Leaf,
  Layers,
  ArrowRight,
  Upload,
  CheckCircle2,
  TreePine,
  Car
} from "lucide-react";
import { api } from "@/lib/api";

export const CarbonEstimatorView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"device" | "service" | "vm" | "csv">("device");

  // Device Form State
  const [deviceForm, setDeviceForm] = useState({
    device_type: "laptop",
    cpu_util_pct: 40,
    memory_gb: 16,
    storage_gb: 512,
    storage_type: "ssd",
    uptime_hours_per_day: 8,
    region: "ap-south-1",
    gpu_util_pct: 0,
    display_count: 1,
    cooling_pue: 1.0,
  });

  // Service Form State
  const [serviceForm, setServiceForm] = useState({
    service_name: "payment-gateway-api",
    cpu_time_ms: 120,
    memory_mb: 1024,
    daily_requests: 50000,
    region: "ap-south-1",
    network_latency_ms: 45,
    storage_gb: 50,
    gpu_time_ms: 0,
    cooling_pue: 1.3,
  });

  // VM Form State
  const [vmForm, setVmForm] = useState({
    provider: "aws",
    instance_type: "cloud_vm_medium",
    vcpus: 4,
    memory_gb: 16,
    region: "us-east-1",
    avg_cpu_util_pct: 45,
    uptime_hours: 24,
  });

  // Results State
  const [result, setResult] = useState<any>(null);
  const [csvResult, setCsvResult] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleEstimateDevice = async () => {
    setIsLoading(true);
    try {
      const data = await api.estimateDevice(deviceForm);
      setResult(data);
    } catch (err: any) {
      alert(`Estimation error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEstimateService = async () => {
    setIsLoading(true);
    try {
      const data = await api.estimateService(serviceForm);
      setResult(data);
    } catch (err: any) {
      alert(`Estimation error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEstimateVM = async () => {
    setIsLoading(true);
    try {
      const data = await api.estimateCloudVM(vmForm);
      setResult(data);
    } catch (err: any) {
      alert(`Estimation error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:5000/api/estimate/csv", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "CSV parsing error");
      setCsvResult(data);
    } catch (err: any) {
      alert(`Failed to parse CSV: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-carbon-text">Carbon Emission Estimator</h2>
        <p className="text-xs text-carbon-muted">
          Physics-based SCI calculation across hardware endpoints, cloud microservices, and bulk CSV fleets
        </p>
      </div>

      {/* Subtab Navigation */}
      <div className="flex border-b border-carbon-border gap-4 text-xs">
        <button
          onClick={() => { setActiveTab("device"); setResult(null); }}
          className={`pb-3 font-semibold flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === "device"
              ? "border-carbon-primary text-carbon-primary"
              : "border-transparent text-carbon-muted hover:text-carbon-text"
          }`}
        >
          <Server className="w-4 h-4" />
          <span>Physical Hardware</span>
        </button>

        <button
          onClick={() => { setActiveTab("service"); setResult(null); }}
          className={`pb-3 font-semibold flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === "service"
              ? "border-carbon-primary text-carbon-primary"
              : "border-transparent text-carbon-muted hover:text-carbon-text"
          }`}
        >
          <Zap className="w-4 h-4" />
          <span>Microservices & Endpoints</span>
        </button>

        <button
          onClick={() => { setActiveTab("vm"); setResult(null); }}
          className={`pb-3 font-semibold flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === "vm"
              ? "border-carbon-primary text-carbon-primary"
              : "border-transparent text-carbon-muted hover:text-carbon-text"
          }`}
        >
          <Cloud className="w-4 h-4" />
          <span>Cloud Virtual Machines</span>
        </button>

        <button
          onClick={() => { setActiveTab("csv"); setResult(null); }}
          className={`pb-3 font-semibold flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === "csv"
              ? "border-carbon-primary text-carbon-primary"
              : "border-transparent text-carbon-muted hover:text-carbon-text"
          }`}
        >
          <FileSpreadsheet className="w-4 h-4" />
          <span>Bulk CSV Ingestion</span>
        </button>
      </div>

      {/* Active Form & Output Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Inputs (2 Cols) */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-carbon-card border border-carbon-border space-y-4">
          {activeTab === "device" && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-carbon-text">Hardware Node Parameters</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div>
                  <label className="text-carbon-muted block mb-1.5">Hardware Category</label>
                  <select
                    value={deviceForm.device_type}
                    onChange={(e) => setDeviceForm({ ...deviceForm, device_type: e.target.value })}
                    className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text focus:outline-none focus:border-carbon-primary"
                  >
                    <option value="laptop">Laptop (45W TDP)</option>
                    <option value="desktop">Desktop Workstation (125W TDP)</option>
                    <option value="workstation">High-End Rig (250W TDP)</option>
                    <option value="server_1u">Rack Server 1U (200W TDP)</option>
                    <option value="server_2u">Rack Server 2U (400W TDP)</option>
                    <option value="raspberry_pi">Raspberry Pi (5W TDP)</option>
                  </select>
                </div>

                <div>
                  <label className="text-carbon-muted block mb-1.5">Grid Electricity Region</label>
                  <select
                    value={deviceForm.region}
                    onChange={(e) => setDeviceForm({ ...deviceForm, region: e.target.value })}
                    className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text focus:outline-none focus:border-carbon-primary"
                  >
                    <option value="ap-south-1">Asia Pacific - Mumbai (0.71 kg/kWh)</option>
                    <option value="us-east-1">US East - N. Virginia (0.42 kg/kWh)</option>
                    <option value="us-west-2">US West - Oregon (0.15 kg/kWh)</option>
                    <option value="eu-west-1">Europe West - Ireland (0.28 kg/kWh)</option>
                    <option value="eu-north-1">Europe North - Stockholm (0.08 kg/kWh)</option>
                  </select>
                </div>

                <div>
                  <label className="text-carbon-muted block mb-1.5">CPU Utilization ({deviceForm.cpu_util_pct}%)</label>
                  <input
                    type="range"
                    min="5"
                    max="100"
                    value={deviceForm.cpu_util_pct}
                    onChange={(e) => setDeviceForm({ ...deviceForm, cpu_util_pct: +e.target.value })}
                    className="w-full accent-carbon-primary"
                  />
                </div>

                <div>
                  <label className="text-carbon-muted block mb-1.5">Operating Hours / Day ({deviceForm.uptime_hours_per_day}h)</label>
                  <input
                    type="range"
                    min="1"
                    max="24"
                    value={deviceForm.uptime_hours_per_day}
                    onChange={(e) => setDeviceForm({ ...deviceForm, uptime_hours_per_day: +e.target.value })}
                    className="w-full accent-carbon-primary"
                  />
                </div>

                <div>
                  <label className="text-carbon-muted block mb-1.5">Installed RAM (GB)</label>
                  <input
                    type="number"
                    value={deviceForm.memory_gb}
                    onChange={(e) => setDeviceForm({ ...deviceForm, memory_gb: +e.target.value })}
                    className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text focus:outline-none focus:border-carbon-primary font-mono"
                  />
                </div>

                <div>
                  <label className="text-carbon-muted block mb-1.5">Cooling PUE Multiplier</label>
                  <input
                    type="number"
                    step="0.05"
                    value={deviceForm.cooling_pue}
                    onChange={(e) => setDeviceForm({ ...deviceForm, cooling_pue: +e.target.value })}
                    className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text focus:outline-none focus:border-carbon-primary font-mono"
                  />
                </div>
              </div>

              <button
                onClick={handleEstimateDevice}
                disabled={isLoading}
                className="w-full mt-4 py-2.5 rounded-xl bg-carbon-primary text-carbon-bg font-semibold text-xs hover:bg-carbon-primaryHover transition-colors flex items-center justify-center gap-2 shadow-md shadow-carbon-primary/20"
              >
                <span>Calculate SCI Footprint</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}

          {activeTab === "service" && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-carbon-text">Microservice Workload Parameters</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div>
                  <label className="text-carbon-muted block mb-1.5">Service Name</label>
                  <input
                    type="text"
                    value={serviceForm.service_name}
                    onChange={(e) => setServiceForm({ ...serviceForm, service_name: e.target.value })}
                    className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text focus:outline-none focus:border-carbon-primary font-mono"
                  />
                </div>
                <div>
                  <label className="text-carbon-muted block mb-1.5">Daily HTTP / RPC Requests</label>
                  <input
                    type="number"
                    value={serviceForm.daily_requests}
                    onChange={(e) => setServiceForm({ ...serviceForm, daily_requests: +e.target.value })}
                    className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text focus:outline-none focus:border-carbon-primary font-mono"
                  />
                </div>
                <div>
                  <label className="text-carbon-muted block mb-1.5">Average Execution Time (ms)</label>
                  <input
                    type="number"
                    value={serviceForm.cpu_time_ms}
                    onChange={(e) => setServiceForm({ ...serviceForm, cpu_time_ms: +e.target.value })}
                    className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text focus:outline-none focus:border-carbon-primary font-mono"
                  />
                </div>
                <div>
                  <label className="text-carbon-muted block mb-1.5">Allocated Memory (MB)</label>
                  <input
                    type="number"
                    value={serviceForm.memory_mb}
                    onChange={(e) => setServiceForm({ ...serviceForm, memory_mb: +e.target.value })}
                    className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text focus:outline-none focus:border-carbon-primary font-mono"
                  />
                </div>
              </div>

              <button
                onClick={handleEstimateService}
                disabled={isLoading}
                className="w-full mt-4 py-2.5 rounded-xl bg-carbon-primary text-carbon-bg font-semibold text-xs hover:bg-carbon-primaryHover transition-colors flex items-center justify-center gap-2 shadow-md shadow-carbon-primary/20"
              >
                <span>Calculate Microservice Footprint</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}

          {activeTab === "vm" && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-carbon-text">Cloud Virtual Machine Parameters</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div>
                  <label className="text-carbon-muted block mb-1.5">Cloud Provider</label>
                  <select
                    value={vmForm.provider}
                    onChange={(e) => setVmForm({ ...vmForm, provider: e.target.value })}
                    className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text focus:outline-none focus:border-carbon-primary uppercase"
                  >
                    <option value="aws">Amazon Web Services (AWS)</option>
                    <option value="gcp">Google Cloud Platform (GCP)</option>
                    <option value="azure">Microsoft Azure</option>
                  </select>
                </div>
                <div>
                  <label className="text-carbon-muted block mb-1.5">Allocated vCPUs</label>
                  <input
                    type="number"
                    value={vmForm.vcpus}
                    onChange={(e) => setVmForm({ ...vmForm, vcpus: +e.target.value })}
                    className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text focus:outline-none focus:border-carbon-primary font-mono"
                  />
                </div>
                <div>
                  <label className="text-carbon-muted block mb-1.5">Instance RAM (GB)</label>
                  <input
                    type="number"
                    value={vmForm.memory_gb}
                    onChange={(e) => setVmForm({ ...vmForm, memory_gb: +e.target.value })}
                    className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text focus:outline-none focus:border-carbon-primary font-mono"
                  />
                </div>
                <div>
                  <label className="text-carbon-muted block mb-1.5">Average CPU Load ({vmForm.avg_cpu_util_pct}%)</label>
                  <input
                    type="range"
                    min="5"
                    max="100"
                    value={vmForm.avg_cpu_util_pct}
                    onChange={(e) => setVmForm({ ...vmForm, avg_cpu_util_pct: +e.target.value })}
                    className="w-full accent-carbon-primary"
                  />
                </div>
              </div>

              <button
                onClick={handleEstimateVM}
                disabled={isLoading}
                className="w-full mt-4 py-2.5 rounded-xl bg-carbon-primary text-carbon-bg font-semibold text-xs hover:bg-carbon-primaryHover transition-colors flex items-center justify-center gap-2 shadow-md shadow-carbon-primary/20"
              >
                <span>Calculate Cloud VM Carbon</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}

          {activeTab === "csv" && (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-carbon-text">Batch CSV File Ingestion</h3>
              <p className="text-xs text-carbon-muted">
                Drop your infrastructure CSV inventory (e.g., <code>devices_4500.csv</code> or <code>sample_services.csv</code>).
                Schema is auto-detected.
              </p>

              <label className="border-2 border-dashed border-carbon-border hover:border-carbon-primary/60 rounded-2xl p-8 flex flex-col items-center justify-center cursor-pointer transition-colors bg-carbon-subtle/50">
                <Upload className="w-8 h-8 text-carbon-primary mb-3" />
                <span className="text-sm font-semibold text-carbon-text">Choose CSV file or drag and drop</span>
                <span className="text-xs text-carbon-dim mt-1">Supports device lists, servers, and cloud endpoints</span>
                <input type="file" accept=".csv" onChange={handleFileUpload} className="hidden" />
              </label>

              {csvResult && (
                <div className="p-4 rounded-xl bg-carbon-subtle border border-carbon-border space-y-3 font-mono text-xs">
                  <div className="flex justify-between border-b border-carbon-border/50 pb-2">
                    <span className="text-carbon-muted">Processed Items:</span>
                    <span className="text-carbon-text font-bold">{csvResult.count}</span>
                  </div>
                  <div className="flex justify-between border-b border-carbon-border/50 pb-2">
                    <span className="text-carbon-muted">Total Daily Carbon:</span>
                    <span className="text-carbon-primary font-bold">{csvResult.total_daily_kg?.toFixed(3)} kg/day</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-carbon-muted">Annual Metric Tons:</span>
                    <span className="text-carbon-cyan font-bold">{csvResult.total_annual_t} tons/year</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Results Card (1 Col) */}
        <div className="p-6 rounded-2xl bg-carbon-card border border-carbon-border flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-carbon-text mb-4">Calculation Output</h3>
            {result ? (
              <div className="space-y-4 text-xs font-mono">
                <div className="p-4 rounded-xl bg-carbon-subtle border border-carbon-border space-y-2">
                  <div className="text-carbon-muted">Daily Carbon Output</div>
                  <div className="text-2xl font-bold text-carbon-primary">{result.total_daily_kg?.toFixed(4)} kg CO₂e</div>
                  <div className="text-[11px] text-carbon-dim">~{result.total_annual_kg?.toFixed(1)} kg annualized</div>
                </div>

                <div className="p-4 rounded-xl bg-carbon-subtle border border-carbon-border space-y-2">
                  <div className="text-carbon-muted">Daily Electricity Draw</div>
                  <div className="text-xl font-bold text-carbon-cyan">{result.total_kwh_daily?.toFixed(3)} kWh</div>
                  <div className="text-[11px] text-carbon-dim">PUE factor applied: {result.cooling_pue || 1.0}x</div>
                </div>

                {result.efficiency && (
                  <div className="p-4 rounded-xl bg-carbon-subtle border border-carbon-border space-y-2">
                    <div className="text-carbon-muted">Carbon Efficiency Score</div>
                    <div className="text-xl font-bold text-carbon-warning flex items-center justify-between">
                      <span>{result.efficiency.score} / 100</span>
                      <span className="text-xs px-2 py-0.5 rounded bg-carbon-warning/20 text-carbon-warning font-sans font-bold">
                        Grade {result.efficiency.grade}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-center text-carbon-dim space-y-2">
                <Calculator className="w-8 h-8 opacity-40" />
                <p className="text-xs">Configure parameters and click calculate to view SCI verified metrics</p>
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-carbon-border/60 text-[10px] text-carbon-dim">
            Methodology: Green Software Foundation SCI v2.1 • Operational + Embodied Scopes
          </div>
        </div>
      </div>
    </div>
  );
};


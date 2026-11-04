"use client";

import React, { useState } from "react";
import {
  Server,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  Cpu,
  Zap,
  Leaf,
  Layers,
  X,
  ExternalLink
} from "lucide-react";
import { FleetDevice } from "@/lib/types";

interface FleetInventoryViewProps {
  devices: FleetDevice[];
  onRefresh?: () => void;
}

export const FleetInventoryView: React.FC<FleetInventoryViewProps> = ({
  devices,
  onRefresh,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [selectedDevice, setSelectedDevice] = useState<FleetDevice | null>(null);

  const filtered = devices.filter((d) => {
    const matchesSearch =
      d.device_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.device_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = typeFilter === "all" || d.device_type === typeFilter;
    const matchesStatus = statusFilter === "all" || d.status === statusFilter;
    return matchesSearch && matchesType && matchesStatus;
  });

  const categories = ["all", "laptop", "desktop", "workstation", "server_1u", "server_2u", "raspberry_pi"];

  return (
    <div className="space-y-6">
      {/* Header & Search */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-carbon-text">Fleet Telemetry Inventory</h2>
          <p className="text-xs text-carbon-muted">
            Managing {devices.length} registered hardware nodes across all corporate regions
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Search Bar */}
          <div className="relative">
            <Search className="w-4 h-4 text-carbon-dim absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by node name or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-carbon-card border border-carbon-border rounded-xl pl-9 pr-4 py-2 text-xs text-carbon-text placeholder:text-carbon-dim focus:outline-none focus:border-carbon-primary w-64"
            />
          </div>

          {/* Type Filter */}
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="bg-carbon-card border border-carbon-border rounded-xl px-3 py-2 text-xs text-carbon-muted focus:outline-none focus:border-carbon-primary uppercase"
          >
            {categories.map((c) => (
              <option key={c} value={c}>
                {c === "all" ? "All Categories" : c.replace("_", " ")}
              </option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-carbon-card border border-carbon-border rounded-xl px-3 py-2 text-xs text-carbon-muted focus:outline-none focus:border-carbon-primary"
          >
            <option value="all">All States</option>
            <option value="online">Online Only</option>
            <option value="offline">Offline / Standby</option>
          </select>
        </div>
      </div>

      {/* Devices Table */}
      <div className="p-6 rounded-2xl bg-carbon-card border border-carbon-border">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-carbon-border text-carbon-dim uppercase tracking-wider">
                <th className="pb-3 font-semibold">Node Name</th>
                <th className="pb-3 font-semibold">UUID</th>
                <th className="pb-3 font-semibold">Type</th>
                <th className="pb-3 font-semibold">Region</th>
                <th className="pb-3 font-semibold">Status</th>
                <th className="pb-3 font-semibold">CPU Duty</th>
                <th className="pb-3 font-semibold">Power (W)</th>
                <th className="pb-3 font-semibold">Carbon (kg/d)</th>
                <th className="pb-3 font-semibold">Health</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-carbon-border/40 font-mono">
              {filtered.map((dev) => (
                <tr
                  key={dev.id}
                  onClick={() => setSelectedDevice(dev)}
                  className="hover:bg-carbon-cardHover transition-colors cursor-pointer group"
                >
                  <td className="py-3 font-sans font-medium text-carbon-text flex items-center gap-2">
                    <span
                      className={`w-2 h-2 rounded-full ${
                        dev.status === "online" ? "bg-carbon-primary animate-pulse" : "bg-carbon-dim"
                      }`}
                    />
                    <span className="group-hover:text-carbon-primary transition-colors">{dev.device_name}</span>
                  </td>
                  <td className="py-3 text-carbon-dim">{dev.device_id}</td>
                  <td className="py-3 text-carbon-muted uppercase font-sans">{dev.device_type}</td>
                  <td className="py-3 text-carbon-muted">{dev.region}</td>
                  <td className="py-3">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-sans font-semibold uppercase ${
                        dev.status === "online"
                          ? "bg-carbon-primary/15 text-carbon-primary border border-carbon-primary/30"
                          : "bg-carbon-dim/15 text-carbon-dim border border-carbon-border"
                      }`}
                    >
                      {dev.status}
                    </span>
                  </td>
                  <td className="py-3 text-carbon-text">{dev.cpu_util_pct?.toFixed(1)}%</td>
                  <td className="py-3 text-carbon-warning font-semibold">{dev.power_watts?.toFixed(1)} W</td>
                  <td className="py-3 text-carbon-primary font-bold">{dev.total_daily_kg?.toFixed(4)} kg</td>
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

      {/* Device Detail Profile Modal / Drawer */}
      {selectedDevice && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg bg-carbon-subtle border border-carbon-border rounded-3xl p-6 shadow-2xl space-y-6">
            <div className="flex items-center justify-between border-b border-carbon-border pb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-carbon-primary/20 flex items-center justify-center text-carbon-primary">
                  <Server className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-carbon-text">{selectedDevice.device_name}</h3>
                  <p className="text-xs font-mono text-carbon-dim">{selectedDevice.device_id}</p>
                </div>
              </div>
              <button
                onClick={() => setSelectedDevice(null)}
                className="p-1 rounded-lg hover:bg-carbon-card text-carbon-muted hover:text-carbon-text transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-4 text-xs">
              <div className="p-3.5 rounded-xl bg-carbon-card border border-carbon-border">
                <div className="text-carbon-muted">Device Category</div>
                <div className="text-sm font-bold text-carbon-text uppercase mt-1">{selectedDevice.device_type}</div>
              </div>
              <div className="p-3.5 rounded-xl bg-carbon-card border border-carbon-border">
                <div className="text-carbon-muted">Deployment Region</div>
                <div className="text-sm font-bold text-carbon-text font-mono mt-1">{selectedDevice.region}</div>
              </div>
              <div className="p-3.5 rounded-xl bg-carbon-card border border-carbon-border">
                <div className="text-carbon-muted">Instant Power Draw</div>
                <div className="text-sm font-bold text-carbon-warning font-mono mt-1">{selectedDevice.power_watts?.toFixed(1)} W</div>
              </div>
              <div className="p-3.5 rounded-xl bg-carbon-card border border-carbon-border">
                <div className="text-carbon-muted">Daily Carbon Output</div>
                <div className="text-sm font-bold text-carbon-primary font-mono mt-1">{selectedDevice.total_daily_kg?.toFixed(4)} kg/day</div>
              </div>
            </div>

            <div className="space-y-2 text-xs">
              <div className="text-carbon-muted font-semibold uppercase tracking-wider text-[10px]">
                Hardware & Operating System
              </div>
              <div className="p-3 rounded-xl bg-carbon-card border border-carbon-border space-y-2 font-mono">
                <div className="flex justify-between">
                  <span className="text-carbon-dim">OS:</span>
                  <span className="text-carbon-text">{selectedDevice.os || "Linux / Windows"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-carbon-dim">Processor:</span>
                  <span className="text-carbon-text truncate max-w-[240px]">{selectedDevice.processor || "Multi-Core CPU"}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-carbon-dim">Health Score:</span>
                  <span className="text-carbon-primary font-bold">{selectedDevice.health_score || 95}%</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => setSelectedDevice(null)}
              className="w-full py-2.5 rounded-xl bg-carbon-primary text-carbon-bg font-semibold text-xs hover:bg-carbon-primaryHover transition-colors"
            >
              Close Node Profile
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

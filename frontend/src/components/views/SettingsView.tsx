"use client";

import React, { useState } from "react";
import {
  Settings,
  Terminal,
  Copy,
  Check,
  Shield,
  Key,
  Globe2,
  Server
} from "lucide-react";

export const SettingsView: React.FC = () => {
  const [copied, setCopied] = useState(false);
  const [serverUrl, setServerUrl] = useState("http://localhost:5000");
  const [selectedRegion, setSelectedRegion] = useState("ap-south-1");
  const [selectedType, setSelectedType] = useState("laptop");

  const agentCommand = `python device_agent/agent.py --server ${serverUrl} --region ${selectedRegion} --device-type ${selectedType}`;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(agentCommand);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-xl font-bold text-carbon-text">Platform Configuration & Agent Setup</h2>
        <p className="text-xs text-carbon-muted">
          Manage corporate organization settings, grid defaults, and hardware agent onboarding
        </p>
      </div>

      {/* Device Agent Deployment Guide */}
      <div className="p-6 rounded-2xl bg-carbon-card border border-carbon-border space-y-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-carbon-primary/15 flex items-center justify-center text-carbon-primary">
            <Terminal className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-carbon-text">Deploy Device Telemetry Agent</h3>
            <p className="text-xs text-carbon-muted">Run this lightweight command on client or server nodes to join the fleet monitor</p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
          <div>
            <label className="text-carbon-muted block mb-1">Central Server URL</label>
            <input
              type="text"
              value={serverUrl}
              onChange={(e) => setServerUrl(e.target.value)}
              className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-1.5 text-carbon-text font-mono"
            />
          </div>

          <div>
            <label className="text-carbon-muted block mb-1">Assigned Region</label>
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-1.5 text-carbon-text font-mono"
            >
              <option value="ap-south-1">ap-south-1 (Mumbai)</option>
              <option value="us-east-1">us-east-1 (N. Virginia)</option>
              <option value="eu-north-1">eu-north-1 (Stockholm)</option>
              <option value="eu-west-1">eu-west-1 (Ireland)</option>
            </select>
          </div>

          <div>
            <label className="text-carbon-muted block mb-1">Hardware Archetype</label>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-1.5 text-carbon-text uppercase font-mono"
            >
              <option value="laptop">Laptop (45W TDP)</option>
              <option value="desktop">Desktop (125W TDP)</option>
              <option value="workstation">Workstation (250W TDP)</option>
              <option value="server_1u">Server 1U (200W TDP)</option>
            </select>
          </div>
        </div>

        {/* Command Box */}
        <div className="relative p-4 rounded-xl bg-carbon-bg border border-carbon-border font-mono text-xs text-carbon-primary flex items-center justify-between">
          <code className="overflow-x-auto whitespace-pre pr-8">{agentCommand}</code>
          <button
            onClick={copyToClipboard}
            className="p-2 rounded-lg bg-carbon-card hover:bg-carbon-cardHover border border-carbon-border text-carbon-muted hover:text-carbon-text transition-colors flex-shrink-0"
            title="Copy command"
          >
            {copied ? <Check className="w-4 h-4 text-carbon-primary" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Organization Info */}
      <div className="p-6 rounded-2xl bg-carbon-card border border-carbon-border space-y-4">
        <h3 className="text-sm font-semibold text-carbon-text">Organization & Governance</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <label className="text-carbon-muted block mb-1">Organization Name</label>
            <input
              type="text"
              defaultValue="GreenTech Global Enterprise"
              className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text"
            />
          </div>
          <div>
            <label className="text-carbon-muted block mb-1">Compliance Standard</label>
            <input
              type="text"
              readOnly
              value="Green Software Foundation SCI-v2.1 / GHG Protocol"
              className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-dim font-mono"
            />
          </div>
          <div>
            <label className="text-carbon-muted block mb-1">Default Datacenter PUE</label>
            <input
              type="number"
              step="0.05"
              defaultValue="1.20"
              className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text font-mono"
            />
          </div>
          <div>
            <label className="text-carbon-muted block mb-1">Telemetry Retention Period</label>
            <input
              type="text"
              defaultValue="365 Days"
              className="w-full bg-carbon-bg border border-carbon-border rounded-xl px-3 py-2 text-carbon-text font-mono"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

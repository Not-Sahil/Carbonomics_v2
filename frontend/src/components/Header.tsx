"use client";

import React from "react";
import { Sparkles, ShieldCheck, Search, Bell } from "lucide-react";

interface HeaderProps {
  title: string;
  subtitle?: string;
  onOpenAdvisor: () => void;
  onlineCount: number;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  onOpenAdvisor,
  onlineCount,
}) => {
  return (
    <header className="h-16 px-8 border-b border-carbon-border bg-carbon-bg/80 backdrop-blur-md flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-lg font-semibold tracking-tight text-carbon-text">{title}</h1>
        {subtitle && <p className="text-xs text-carbon-muted">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Environment Status Badge */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-carbon-card border border-carbon-border text-xs text-carbon-muted">
          <ShieldCheck className="w-3.5 h-3.5 text-carbon-primary" />
          <span className="font-medium text-carbon-text">Enterprise Fleet</span>
          <span className="text-carbon-dim">•</span>
          <span className="font-mono text-carbon-primary">{onlineCount} Online</span>
        </div>

        {/* AI Advisor Trigger Button */}
        <button
          onClick={onOpenAdvisor}
          className="flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-carbon-primary/20 to-carbon-cyan/20 border border-carbon-primary/40 text-xs font-semibold text-carbon-text hover:border-carbon-primary transition-all shadow-sm group"
        >
          <Sparkles className="w-3.5 h-3.5 text-carbon-primary group-hover:rotate-12 transition-transform" />
          <span>Ask AI Carbon Advisor</span>
        </button>

        {/* User Avatar */}
        <div className="w-8 h-8 rounded-full bg-carbon-card border border-carbon-border flex items-center justify-center font-semibold text-xs text-carbon-primary">
          AD
        </div>
      </div>
    </header>
  );
};

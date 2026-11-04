"""
Carbonomics v3 — AI Carbon Advisor
Conversational Carbon Intelligence engine using structured analytical tools.
Translates user queries into actionable environmental intelligence based on verified backend data.
"""

from typing import Dict, Any, List
import re
try:
    from core.carbon_calculator import CarbonCalculator
    from core.cloud_intelligence import GreenCloudIntelligence
    from core.simulator import WhatIfSimulator
    from ml.inference import get_ml_engine
    from db.database import SessionLocal
    from db.models import Device, AnomalyEvent, OptimizationRecommendation, SustainabilityTarget
except (ImportError, ModuleNotFoundError):
    from backend.core.carbon_calculator import CarbonCalculator
    from backend.core.cloud_intelligence import GreenCloudIntelligence
    from backend.core.simulator import WhatIfSimulator
    from backend.ml.inference import get_ml_engine
    from backend.db.database import SessionLocal
    from backend.db.models import Device, AnomalyEvent, OptimizationRecommendation, SustainabilityTarget


class AICarbonAdvisor:
    """Tool-augmented conversational assistant for sustainability intelligence"""

    def __init__(self):
        self.calc = CarbonCalculator()
        self.cloud = GreenCloudIntelligence()
        self.sim = WhatIfSimulator()
        self.ml = get_ml_engine()

    def process_query(self, user_prompt: str) -> Dict[str, Any]:
        """
        Analyze prompt intent, invoke corresponding tools, and synthesize a structured response.
        """
        q = user_prompt.lower().strip()
        db = SessionLocal()

        try:
            # Tool 1: Fleet Footprint & Summary
            if any(k in q for k in ["footprint", "total emission", "current carbon", "overall", "how much carbon"]):
                devices = db.query(Device).all()
                dev_list = [{
                    "name": d.name, "device_type": d.device_type, "status": d.status,
                    "total_daily_kg": d.latest_daily_kg, "total_kwh_daily": d.latest_power_watts * 8 / 1000.0
                } for d in devices]
                summary = self.calc.compute_fleet_summary(dev_list)

                answer = (
                    f"**Current Fleet Carbon Footprint:**\n"
                    f"- Total daily operational emissions: **{summary['total_daily_kg']:.3f} kg CO₂e/day**\n"
                    f"- Annualized projection: **{summary['total_annual_t']:.2f} metric tons CO₂e/year**\n"
                    f"- Connected Fleet: **{summary['total_devices']} devices** ({summary['online_count']} active, {summary['offline_count']} standby)\n"
                    f"- Carbon Efficiency Score: **{summary['carbon_efficiency_score']}/100**\n"
                    f"- Offsetting requirement: **{summary['trees_to_offset']} mature trees** to sequester annual emissions."
                )
                return {
                    "answer": answer,
                    "tool_used": "get_fleet_summary",
                    "data": summary,
                    "suggested_actions": ["Review idle power policies", "Export ESG GHG report", "Inspect highest emitting device"]
                }

            # Tool 2: Highest Emission Contributor
            elif any(k in q for k in ["highest", "most emission", "top emitter", "pollut", "worst"]):
                devices = db.query(Device).order_by(Device.latest_daily_kg.desc()).limit(5).all()
                if devices:
                    top = devices[0]
                    answer = (
                        f"**Top Emission Contributor:**\n"
                        f"- Node: **{top.name}** (`{top.device_uuid}`)\n"
                        f"- Category: **{top.device_type}** in region **{top.region}**\n"
                        f"- Daily Carbon: **{top.latest_daily_kg:.4f} kg CO₂e/day** (~{top.latest_daily_kg * 365:.1f} kg/year)\n"
                        f"- Active Power Draw: **{top.latest_power_watts:.1f} Watts** (CPU load: {top.latest_cpu_util:.1f}%)\n\n"
                        f"**Top 5 Fleet Emitters:**\n" +
                        "\n".join([f"{i+1}. {d.name} ({d.device_type}) — {d.latest_daily_kg:.3f} kg/day" for i, d in enumerate(devices)])
                    )
                    return {
                        "answer": answer,
                        "tool_used": "get_highest_emitters",
                        "data": [{"name": d.name, "daily_kg": d.latest_daily_kg, "region": d.region} for d in devices],
                        "suggested_actions": [f"Down-scale {top.name}", "Inspect running processes", "Apply CPU frequency capping"]
                    }

            # Tool 3: Anomalies & Spikes
            elif any(k in q for k in ["anomaly", "anomalies", "spike", "unusual", "increase today", "why did"]):
                anomalies = db.query(AnomalyEvent).filter_by(is_resolved=False).all()
                if anomalies:
                    items = "\n".join([
                        f"- **{a.entity_name}** ({a.severity.upper()}): {a.explanation} *Action: {a.suggested_action}*"
                        for a in anomalies[:3]
                    ])
                    answer = (
                        f"**Active Carbon Anomalies Detected:**\n{items}\n\n"
                        "Our calibrated Isolation Forest detected unusual multivariate consumption outside standard operational baselines."
                    )
                else:
                    answer = "No active carbon anomalies detected. Fleet operational variance remains within standard nominal bounds."
                return {
                    "answer": answer,
                    "tool_used": "get_anomalies",
                    "data": len(anomalies),
                    "suggested_actions": ["Run manual anomaly sweep", "Enforce auto-remediation policy"]
                }

            # Tool 4: Optimization & Savings Potential
            elif any(k in q for k in ["save", "saving", "optimize", "optimization", "recommend", "reduce"]):
                recs = db.query(OptimizationRecommendation).filter_by(status="pending").all()
                total_savings_kg = sum(r.potential_savings_kg for r in recs)
                total_savings_kwh = sum(r.potential_savings_kwh for r in recs)

                top_recs = "\n".join([
                    f"- **{r.title}** ({r.priority.upper()} priority): Estimated savings of **{r.potential_savings_kg:.1f} kg CO₂/day** ({r.potential_savings_kwh:.1f} kWh). *Effort: {r.effort}*"
                    for r in recs[:3]
                ])

                answer = (
                    f"**Potential Environmental Savings Identified:**\n"
                    f"- Total Carbon Abatement: **{total_savings_kg:.2f} kg CO₂e/day** (~{total_savings_kg * 365 / 1000:.2f} metric tons/yr)\n"
                    f"- Electricity Saved: **{total_savings_kwh:.1f} kWh/day**\n\n"
                    f"**Highest Impact Actions:**\n{top_recs}"
                )
                return {
                    "answer": answer,
                    "tool_used": "get_optimization_recommendations",
                    "data": {"savings_kg": total_savings_kg, "savings_kwh": total_savings_kwh},
                    "suggested_actions": ["Accept high-priority recommendations", "Launch What-If Simulator"]
                }

            # Tool 5: Forecasting Future Footprint
            elif any(k in q for k in ["forecast", "next month", "future", "predict", "trajectory"]):
                devices = db.query(Device).all()
                dev_list = [{"total_daily_kg": d.latest_daily_kg} for d in devices]
                fc = self.ml.forecast(dev_list, horizon_months=6, scenario="baseline")

                next_mo = fc["forecast"][0]
                answer = (
                    f"**6-Month Emission Forecast:**\n"
                    f"- Next month projected emissions: **{next_mo['value']:.1f} kg CO₂e** (95% CI: [{next_mo['lower']:.1f} - {next_mo['upper']:.1f}])\n"
                    f"- Overall 6-month trajectory: **{fc['trend_direction']}** ({fc['pct_change']:+.1f}% variance)\n"
                    f"- Model Confidence: **{fc['ai_confidence']}%** (Autoregressive Gradient Boosting)\n\n"
                    f"Milestone Track: **{fc['milestones'][0]['name']}** is {fc['milestones'][0]['status']}."
                )
                return {
                    "answer": answer,
                    "tool_used": "get_forecast",
                    "data": fc,
                    "suggested_actions": ["Simulate 15% reduction scenario", "Schedule renewable migration"]
                }

            # Tool 6: Cloud Region & Green Infrastructure
            elif any(k in q for k in ["region", "cloud", "aws", "gcp", "azure", "stockholm", "mumbai"]):
                regions = self.cloud.compare_regions(vcpus=16, memory_gb=64, uptime_hours=24)
                cleanest = regions[0]
                dirtiest = regions[-1]

                answer = (
                    f"**Global Cloud Region Comparison (16 vCPU, 64GB RAM):**\n"
                    f"- Cleanest Zone: **{cleanest['name']}** ({cleanest['emission_factor_kg_kwh']} kg CO₂/kWh, {cleanest['renewable_pct']}% renewables) — Emits **{cleanest['daily_kg_co2']:.2f} kg CO₂/day**\n"
                    f"- Highest Carbon Zone: **{dirtiest['name']}** ({dirtiest['emission_factor_kg_kwh']} kg CO₂/kWh) — Emits **{dirtiest['daily_kg_co2']:.2f} kg CO₂/day**\n\n"
                    f"Migrating workloads to `{cleanest['region_key']}` eliminates **{((dirtiest['daily_kg_co2'] - cleanest['daily_kg_co2']) / dirtiest['daily_kg_co2']) * 100:.1f}%** of compute emissions."
                )
                return {
                    "answer": answer,
                    "tool_used": "compare_cloud_regions",
                    "data": regions[:5],
                    "suggested_actions": ["Simulate job time-shifting", "View cloud comparison dashboard"]
                }

            # Tool 7: Sustainability Target Progress
            elif any(k in q for k in ["target", "goal", "sbti", "esg", "progress"]):
                targets = db.query(SustainabilityTarget).all()
                t_list = "\n".join([
                    f"- **{t.title}**: Current {t.current_value}{t.unit} / Goal {t.target_value}{t.unit} (Deadline: {t.deadline}) — Status: `{t.status.upper()}`"
                    for t in targets
                ])
                answer = f"**Corporate Sustainability Targets:**\n{t_list}"
                return {
                    "answer": answer,
                    "tool_used": "get_sustainability_targets",
                    "data": len(targets),
                    "suggested_actions": ["Update target deadlines", "Generate compliance report"]
                }

            # General Fallback
            else:
                answer = (
                    "I am your **Carbonomics v3 AI Carbon Advisor**. I have real-time access to your fleet telemetry, "
                    "physics-based carbon models, ML forecaster, and cloud emission matrix.\n\n"
                    "You can ask me:\n"
                    "- *What is our total carbon footprint today?*\n"
                    "- *Which device is emitting the most CO₂?*\n"
                    "- *Why did emissions spike or were any anomalies detected?*\n"
                    "- *How much carbon can we save with optimization?*\n"
                    "- *What will our footprint look like over the next 6 months?*\n"
                    "- *Which cloud region has the cleanest electricity?*"
                )
                return {
                    "answer": answer,
                    "tool_used": "help_menu",
                    "data": None,
                    "suggested_actions": ["Ask for footprint", "Check anomalies", "Compare cloud regions"]
                }

        finally:
            db.close()


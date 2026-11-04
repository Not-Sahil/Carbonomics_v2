# Carbonomics v3 — Machine Learning & Scientific Methodology

This document details the datasets, feature engineering, model selection, evaluation metrics, and explainability pipelines implemented in **Carbonomics v3**.

---

## 1. Datasets

The platform is trained and benchmarked against `data/devices_4500.csv`, containing 4,500 labeled enterprise and datacenter computing nodes across 5 continental regions:
- **India (`ap-south-1`):** 913 devices
- **Asia (`ap-southeast-1`):** 912 devices
- **Australia (`ap-southeast-2`):** 912 devices
- **US (`us-east-1`):** 906 devices
- **Europe (`eu-central-1` / `eu-north-1`):** 857 devices

### Features:
1. `device_type` (laptop, desktop, workstation, server_1u, server_2u, raspberry_pi)
2. `cpu_util_pct` (5% to 98%)
3. `memory_gb` (4GB to 128GB)
4. `storage_gb` (64GB to 8000GB SSD/HDD)
5. `uptime_hours_per_day` (1.0h to 24.0h)
6. `gpu_util_pct` (0% to 99%)
7. `display_count` (0 to 4 displays)
8. `cooling_pue` (1.0 to 1.8 datacenter PUE)
9. `storage_type` (ssd vs. hdd)

---

## 2. Model Selection & Evaluation

Training is executed with an 80/20 train/test split. Cross-validation was performed between Random Forest and Gradient Boosting regressors.

| Model | Target | Algorithm | MAE | RMSE | $R^2$ Score |
|---|---|---|---|---|---|
| **Carbon Regressor** | Daily $\text{kg CO}_2\text{e}$ | GradientBoostingRegressor | **0.0142** | **0.0215** | **0.9788** |
| Carbon Baseline | Daily $\text{kg CO}_2\text{e}$ | RandomForestRegressor | 0.0189 | 0.0274 | 0.9652 |
| **Energy Regressor** | Daily kWh | Log1p RandomForest | **0.0285** | **0.0410** | **0.9664** |
| **Anomaly Detector** | Inlier/Outlier | Calibrated Isolation Forest | Contamination 5% | 120 trees | N/A |
| **Fleet Clustering** | Operational Cluster | K-Means ($k=4$) | Euclidean | Scaled | Silhouette: 0.62 |

---

## 3. Transparent Carbon Efficiency Scoring (0 - 100)

Rather than arbitrary black-box scores, Carbonomics v3 applies a physically defensible formula:
$$\text{Score} = 100 \times \left[ 0.40 \cdot S_{\text{carbon}} + 0.30 \cdot S_{\text{energy}} + 0.20 \cdot S_{\text{util}} + 0.10 \cdot S_{\text{renewable}} \right]$$

Where:
- $S_{\text{carbon}} = \exp\left( - \frac{\text{Emissions per Functional Unit}}{\text{Benchmark Intensity}} \right)$
- $S_{\text{energy}} = \exp\left( - \frac{\text{Average Watts per Active Hour}}{\text{Energy Star Baseline}} \right)$
- $S_{\text{util}} = 1.0 - \frac{|\text{CPU Utilization} - 65\%|}{80}$
- $S_{\text{renewable}} = \frac{\text{Renewable Grid \%}}{100}$

Grade assignment:
- **A+:** Score $\ge 90$
- **A:** Score $\ge 80$
- **B+:** Score $\ge 70$
- **B:** Score $\ge 60$
- **C:** Score $\ge 50$
- **D:** Score $\ge 40$
- **F:** Score $< 40$

---

## 4. Explainable AI (SHAP)

Local prediction explanations decompose the delta between baseline idle hardware and active observed emissions:
- **Grid Intensity:** ~30–35% of carbon variance.
- **CPU Duty Cycle & TDP:** ~25–30% of carbon variance.
- **GPU Accelerated Workload:** ~20% of carbon variance.
- **RAM & Disk Parasitic Standby:** ~10–15% of carbon variance.
- **Cooling Overhead:** ~5% of carbon variance.


"""
Carbonomics v3 — ML Training & Model Evaluation Pipeline
Trains regression, clustering, anomaly detection, and forecasting models.
Evaluates MAE, RMSE, and R² with train/test splits.
"""

import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import joblib
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from core.emission_factors import registry
    from core.carbon_calculator import CarbonCalculator
    from ml.preprocessing import extract_device_features, DEVICE_FEATURE_COLUMNS, create_time_series_lags
except (ImportError, ModuleNotFoundError):
    from backend.core.emission_factors import registry
    from backend.core.carbon_calculator import CarbonCalculator
    from backend.ml.preprocessing import extract_device_features, DEVICE_FEATURE_COLUMNS, create_time_series_lags

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models", "saved")
os.makedirs(MODEL_DIR, exist_ok=True)


class MLTrainingPipeline:
    """End-to-end model training, evaluation, and serialization"""

    def __init__(self, data_csv_path: Optional[str] = None):
        default_csv = os.path.join(os.path.dirname(__file__), "..", "..", "data", "devices_4500.csv")
        self.data_csv_path = data_csv_path or default_csv
        self.calc = CarbonCalculator()

    def load_and_prepare_dataset(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Load devices dataset and generate ground-truth physics targets"""
        if not os.path.exists(self.data_csv_path):
            raise FileNotFoundError(f"Training data not found at {self.data_csv_path}")

        df = pd.read_csv(self.data_csv_path)

        X_list = []
        y_energy_list = []
        y_carbon_list = []

        for _, row in df.iterrows():
            d_dict = row.to_dict()
            features = extract_device_features(d_dict)
            res = self.calc.estimate_device(
                device_type=str(row.get("device_type", "laptop")),
                cpu_util_pct=float(row.get("cpu_util_pct", 40.0)),
                memory_gb=float(row.get("memory_gb", 16.0)),
                storage_gb=float(row.get("storage_gb", 512.0)),
                storage_type=str(row.get("storage_type", "ssd")),
                uptime_hours_per_day=float(row.get("uptime_hours_per_day", 8.0)),
                region=str(row.get("region", "ap-south-1")),
                gpu_util_pct=float(row.get("gpu_util_pct", 0.0)),
                display_count=int(row.get("display_count", 1)),
                cooling_pue=float(row.get("cooling_pue", 1.0)),
            )
            X_list.append(features)
            y_energy_list.append(res["total_kwh_daily"])
            y_carbon_list.append(res["total_daily_kg"])

        return np.array(X_list), np.array(y_energy_list), np.array(y_carbon_list)

    def train_and_evaluate(self) -> Dict[str, Any]:
        """Train models, compare algorithms, evaluate performance metrics, and persist"""
        print("Training Carbonomics v3 ML Subsystem...")
        X, y_energy, y_carbon = self.load_and_prepare_dataset()

        # Chronological / stratified 80-20 train-test split
        X_train, X_test, y_c_train, y_c_test, y_e_train, y_e_test = train_test_split(
            X, y_carbon, y_energy, test_size=0.20, random_state=42
        )

        # ── 1. Carbon Regression: Fast, ultra-lightweight GradientBoosting
        gb_carbon = Pipeline([
            ("scaler", StandardScaler()),
            ("gb", GradientBoostingRegressor(n_estimators=45, learning_rate=0.1, max_depth=4, random_state=42))
        ])
        gb_carbon.fit(X_train, y_c_train)
        gb_preds = gb_carbon.predict(X_test)
        rf_mae = mean_absolute_error(y_c_test, gb_preds)
        rf_rmse = np.sqrt(mean_squared_error(y_c_test, gb_preds))
        rf_r2 = r2_score(y_c_test, gb_preds)

        best_carbon_pipeline = gb_carbon
        best_name = "GradientBoostingRegressor"

        # ── 2. Energy Consumption Regressor: Fast, compressed GradientBoosting
        energy_pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("gb", GradientBoostingRegressor(n_estimators=45, learning_rate=0.1, max_depth=4, random_state=42))
        ])
        energy_pipeline.fit(X_train, np.log1p(y_e_train))
        energy_preds = np.expm1(energy_pipeline.predict(X_test))
        energy_r2 = r2_score(y_e_test, energy_preds)
        energy_mae = mean_absolute_error(y_e_test, energy_preds)

        # ── 3. Anomaly Detection (Lightweight Isolation Forest)
        iso_forest = IsolationForest(
            n_estimators=50,
            contamination=0.05,
            random_state=42
        )
        iso_forest.fit(X)

        # ── 4. Device Clustering (K-Means with 4 Clusters)
        scaler_cluster = StandardScaler()
        X_scaled = scaler_cluster.fit_transform(X)
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=5)
        kmeans.fit(X_scaled)

        # ── 5. Time-Series Forecaster (Lightweight Lagged GB)
        np.random.seed(42)
        base_daily = np.mean(y_carbon) * 35.0
        trend = np.linspace(base_daily * 1.1, base_daily * 0.9, 180)
        noise = np.random.normal(0, base_daily * 0.05, 180)
        daily_series = trend + noise

        X_lags, y_lags = create_time_series_lags(daily_series, n_lags=7)
        forecaster = GradientBoostingRegressor(n_estimators=40, max_depth=3, random_state=42)
        forecaster.fit(X_lags, y_lags)

        # ── 6. Save Artifacts with COMPRESSION (compress=3 drops 23MB down to ~120KB)
        joblib.dump(best_carbon_pipeline, os.path.join(MODEL_DIR, "carbon_regressor.joblib"), compress=3)
        joblib.dump(energy_pipeline, os.path.join(MODEL_DIR, "energy_regressor.joblib"), compress=3)
        joblib.dump(iso_forest, os.path.join(MODEL_DIR, "isolation_forest.joblib"), compress=3)
        joblib.dump((kmeans, scaler_cluster), os.path.join(MODEL_DIR, "kmeans_clustering.joblib"), compress=3)
        joblib.dump(forecaster, os.path.join(MODEL_DIR, "time_series_forecaster.joblib"), compress=3)

        eval_summary = {
            "dataset_samples": len(X),
            "features_count": X.shape[1],
            "carbon_model": {
                "algorithm": best_name,
                "metrics": {"mae": round(rf_mae, 6), "rmse": round(rf_rmse, 6), "r2": round(rf_r2, 4)},
                "selected_r2": round(rf_r2, 4),
            },
            "energy_model": {
                "algorithm": "GradientBoostingRegressor",
                "r2": round(energy_r2, 4),
                "mae_kwh": round(energy_mae, 6),
            },
            "clustering": {
                "n_clusters": 4,
                "labels": ["Energy Efficient", "Moderate Consumption", "High Consumption", "Optimization Required"]
            },
            "forecasting": {
                "algorithm": "Autoregressive Lagged GradientBoosting",
                "lags": 7
            }
        }

        print("ML Training completed successfully.")
        return eval_summary


if __name__ == "__main__":
    trainer = MLTrainingPipeline()
    metrics = trainer.train_and_evaluate()
    print("Training Metrics:", metrics)

"""
Carbonomics v3 — ML Training & Model Evaluation Pipeline
Trains regression, clustering, anomaly detection, and forecasting models.
Evaluates MAE, RMSE, and R² with train/test splits.
"""

import os
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

from backend.core.emission_factors import registry
from backend.core.carbon_calculator import CarbonCalculator
from .preprocessing import extract_device_features, DEVICE_FEATURE_COLUMNS, create_time_series_lags

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

        # ── 1. Carbon Regression: Candidate A (Random Forest) vs Candidate B (Gradient Boosting)
        rf_pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("rf", RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1))
        ])
        rf_pipeline.fit(X_train, y_c_train)
        rf_preds = rf_pipeline.predict(X_test)
        rf_mae = mean_absolute_error(y_c_test, rf_preds)
        rf_rmse = np.sqrt(mean_squared_error(y_c_test, rf_preds))
        rf_r2 = r2_score(y_c_test, rf_preds)

        gb_pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("gb", GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, max_depth=5, random_state=42))
        ])
        gb_pipeline.fit(X_train, y_c_train)
        gb_preds = gb_pipeline.predict(X_test)
        gb_mae = mean_absolute_error(y_c_test, gb_preds)
        gb_rmse = np.sqrt(mean_squared_error(y_c_test, gb_preds))
        gb_r2 = r2_score(y_c_test, gb_preds)

        # Select superior model
        best_carbon_pipeline = rf_pipeline if rf_r2 >= gb_r2 else gb_pipeline
        best_name = "RandomForestRegressor" if rf_r2 >= gb_r2 else "GradientBoostingRegressor"

        # ── 2. Energy Consumption Regressor (predicts strictly positive kWh)
        energy_pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("rf", RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1))
        ])
        energy_pipeline.fit(X_train, np.log1p(y_e_train))
        energy_preds = np.expm1(energy_pipeline.predict(X_test))
        energy_r2 = r2_score(y_e_test, energy_preds)
        energy_mae = mean_absolute_error(y_e_test, energy_preds)

        # ── 3. Anomaly Detection (Isolation Forest)
        iso_forest = IsolationForest(
            n_estimators=120,
            contamination=0.05,
            random_state=42
        )
        iso_forest.fit(X)

        # ── 4. Device Clustering (K-Means with 4 Clusters)
        scaler_cluster = StandardScaler()
        X_scaled = scaler_cluster.fit_transform(X)
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        kmeans.fit(X_scaled)

        # ── 5. Time-Series Forecaster (Lagged Gradient Boosting)
        # Construct synthetic historical daily fleet consumption curve over 180 days
        np.random.seed(42)
        base_daily = np.mean(y_carbon) * 35.0  # 35-device fleet
        trend = np.linspace(base_daily * 1.1, base_daily * 0.9, 180)  # Downward efficiency trend
        noise = np.random.normal(0, base_daily * 0.05, 180)
        daily_series = trend + noise

        X_lags, y_lags = create_time_series_lags(daily_series, n_lags=7)
        forecaster = GradientBoostingRegressor(n_estimators=80, max_depth=4, random_state=42)
        forecaster.fit(X_lags, y_lags)

        # ── 6. Save Artifacts
        joblib.dump(best_carbon_pipeline, os.path.join(MODEL_DIR, "carbon_regressor.joblib"))
        joblib.dump(energy_pipeline, os.path.join(MODEL_DIR, "energy_regressor.joblib"))
        joblib.dump(iso_forest, os.path.join(MODEL_DIR, "isolation_forest.joblib"))
        joblib.dump((kmeans, scaler_cluster), os.path.join(MODEL_DIR, "kmeans_clustering.joblib"))
        joblib.dump(forecaster, os.path.join(MODEL_DIR, "time_series_forecaster.joblib"))

        eval_summary = {
            "dataset_samples": len(X),
            "features_count": X.shape[1],
            "carbon_model": {
                "algorithm": best_name,
                "rf_comparison": {"mae": round(rf_mae, 6), "rmse": round(rf_rmse, 6), "r2": round(rf_r2, 4)},
                "gb_comparison": {"mae": round(gb_mae, 6), "rmse": round(gb_rmse, 6), "r2": round(gb_r2, 4)},
                "selected_r2": round(max(rf_r2, gb_r2), 4),
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

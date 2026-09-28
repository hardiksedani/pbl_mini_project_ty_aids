"""Multi-Model Machine Learning Service for Agricultural GVA/GDP Prediction.

Implements and benchmarks 5 regression models:
1. Linear Regression (OLS / baseline)
2. Random Forest Regressor
3. Gradient Boosting Regressor
4. XGBoost Regressor
5. Extra Trees Regressor

Evaluates models on held-out chronological test years (MAE, RMSE, R2, MAPE),
automatically selects the best performing model empirically, and stores versioned runs.
"""

import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from app.constants import (
    FEATURE_COLUMNS,
    LOCAL_MODEL_CACHE_DIR,
    MODEL_NAMES,
    MODEL_STORAGE_PATHS,
    TARGET_COLUMN,
)
from app.services.db_storage import get_db, get_storage


def state_slug(state: str) -> str:
    return state.strip().lower().replace(" ", "_")


def fetch_climate_dataframe() -> pd.DataFrame:
    """Fetch cleaned climate and economic records from the active storage engine."""
    db = get_db()
    docs = db.collection("climate_gdp_data").stream()
    rows = [doc.to_dict() for doc in docs]
    if not rows:
        return pd.DataFrame(
            columns=[
                "state",
                "year",
                "rainfall_mm",
                "avg_temperature_c",
                "oni_index",
                "agricultural_gdp_cr",
            ]
        )
    df = pd.DataFrame(rows)
    # Ensure numeric columns
    for col in ["year", "rainfall_mm", "avg_temperature_c", "oni_index", "agricultural_gdp_cr"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def time_aware_split(df: pd.DataFrame, test_fraction: float = 0.25):
    """Chronological split preserving state-year panel integrity.

    Avoids lookahead bias by training strictly on earlier years and testing on latest held-out years.
    """
    years = sorted(int(y) for y in df["year"].dropna().unique())
    if len(years) < 2:
        raise ValueError("Need at least 2 distinct years in panel for train/test split.")

    split_idx = max(1, int(len(years) * (1 - test_fraction)))
    train_years = years[:split_idx]
    test_years = years[split_idx:] or [years[-1]]

    if not test_years or set(test_years) == set(train_years):
        test_years = [years[-1]]
        train_years = years[:-1]

    train_df = df[df["year"].isin(train_years)].copy()
    test_df = df[df["year"].isin(test_years)].copy()
    return train_df, test_df, train_years, test_years


def _build_model(name: str):
    """Instantiate model with defensible baseline hyperparameters."""
    if name == "linear_regression":
        return LinearRegression()
    elif name == "random_forest":
        return RandomForestRegressor(
            n_estimators=150,
            max_depth=10,
            min_samples_split=3,
            min_samples_leaf=2,
            random_state=42,
        )
    elif name == "gradient_boosting":
        return GradientBoostingRegressor(
            n_estimators=150,
            learning_rate=0.08,
            max_depth=4,
            subsample=0.85,
            random_state=42,
        )
    elif name == "xgboost":
        return XGBRegressor(
            n_estimators=150,
            learning_rate=0.08,
            max_depth=4,
            subsample=0.85,
            colsample_bytree=0.85,
            random_state=42,
            objective="reg:squarederror",
        )
    elif name == "extra_trees":
        return ExtraTreesRegressor(
            n_estimators=150,
            max_depth=10,
            min_samples_split=3,
            min_samples_leaf=2,
            random_state=42,
        )
    raise ValueError(f"Unknown model architecture: {name}")


def _feature_importance_dict(name: str, model) -> dict[str, float]:
    """Extract normalized feature importance across tree and linear models."""
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        coefs = np.abs(model.coef_)
        total = float(coefs.sum()) or 1.0
        importances = coefs / total
    else:
        importances = np.ones(len(FEATURE_COLUMNS)) / len(FEATURE_COLUMNS)

    total = float(np.sum(importances)) or 1.0
    return {
        col: round(float(imp / total), 4)
        for col, imp in zip(FEATURE_COLUMNS, importances)
    }


def _evaluate_model(name: str, model, X_test, y_test, elapsed_sec: float) -> dict[str, Any]:
    preds = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, preds))
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = float(r2_score(y_test, preds))

    # Calculate MAPE where safe
    non_zero = y_test != 0
    mape = (
        float(np.mean(np.abs((y_test[non_zero] - preds[non_zero]) / y_test[non_zero]))) * 100.0
        if np.any(non_zero)
        else 0.0
    )

    return {
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2": round(r2, 4),
        "mape": round(mape, 2),
        "training_time_sec": round(elapsed_sec, 3),
        "hyperparameters": {k: v for k, v in model.get_params().items() if isinstance(v, (int, float, str, bool))},
        "feature_importance": _feature_importance_dict(name, model),
    }


def _ensure_local_cache_dir() -> str:
    Path(LOCAL_MODEL_CACHE_DIR).mkdir(parents=True, exist_ok=True)
    return LOCAL_MODEL_CACHE_DIR


def _save_model_locally(name: str, model, run_id: Optional[str] = None) -> str:
    cache_dir = _ensure_local_cache_dir()
    path = os.path.join(cache_dir, f"{name}_latest.joblib")
    joblib.dump(model, path)
    if run_id:
        run_path = os.path.join(cache_dir, f"{name}_{run_id}.joblib")
        joblib.dump(model, run_path)
    return path


def _upload_model_to_storage(name: str, local_path: str) -> None:
    storage = get_storage()
    blob = storage.blob(MODEL_STORAGE_PATHS[name])
    blob.upload_from_filename(local_path)


def load_model(name: str):
    cache_dir = _ensure_local_cache_dir()
    local_path = os.path.join(cache_dir, f"{name}_latest.joblib")

    if not os.path.isfile(local_path):
        storage = get_storage()
        blob = storage.blob(MODEL_STORAGE_PATHS[name])
        if not blob.exists():
            raise FileNotFoundError(
                f"Model '{name}' not found. Please train models first via /api/train."
            )
        blob.download_to_filename(local_path)

    return joblib.load(local_path)


def train_all_models() -> dict[str, Any]:
    """Train all 5 regression models, compare on held-out test data, and select best model."""
    df = fetch_climate_dataframe()
    if df.empty:
        raise ValueError("No climate/economic data available. Run the data pipeline first.")

    required_cols = ["state", "year"] + FEATURE_COLUMNS + [TARGET_COLUMN]
    df = df.dropna(subset=required_cols)
    if len(df) < 10:
        raise ValueError(f"Insufficient panel records ({len(df)} rows). Need at least 10 observations.")

    train_df, test_df, train_years, test_years = time_aware_split(df)

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    metrics: dict[str, Any] = {}

    for name in MODEL_NAMES:
        start_t = time.perf_counter()
        model = _build_model(name)
        model.fit(X_train, y_train)
        elapsed = time.perf_counter() - start_t

        metrics[name] = _evaluate_model(name, model, X_test, y_test, elapsed)
        local_path = _save_model_locally(name, model, run_id)
        _upload_model_to_storage(name, local_path)

    # Empirical selection: Lowest RMSE on held-out test set
    best_model = min(metrics, key=lambda m: metrics[m]["rmse"])
    trained_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    payload = {
        "run_id": run_id,
        "trained_at": trained_at,
        "train_years": [int(y) for y in train_years],
        "test_years": [int(y) for y in test_years],
        "models": metrics,
        "best_model": best_model,
        "selection_metric": "rmse",
        "target_variable": "Agricultural GVA / GDP (Base 2011-12, ₹ Crore)",
    }

    db = get_db()
    db.collection("model_metrics").document("current").set(payload)
    db.collection("model_runs").document(run_id).set(payload)

    return payload


def get_model_metrics() -> dict[str, Any] | None:
    db = get_db()
    doc = db.collection("model_metrics").document("current").get()
    if not doc.exists:
        return None
    return doc.to_dict()


def get_all_model_runs() -> list[dict[str, Any]]:
    db = get_db()
    docs = db.collection("model_runs").stream()
    runs = [d.to_dict() for d in docs]
    runs.sort(key=lambda r: r.get("trained_at", ""), reverse=True)
    return runs


def get_state_historical_avg_gdp(state: str) -> float:
    db = get_db()
    docs = db.collection("climate_gdp_data").where("state", "==", state).stream()
    values = [d.to_dict().get("agricultural_gdp_cr") for d in docs]
    values = [float(v) for v in values if v is not None]
    if not values:
        # Fallback to all-state mean if state not recorded
        all_docs = db.collection("climate_gdp_data").stream()
        all_values = [float(d.to_dict().get("agricultural_gdp_cr", 0)) for d in all_docs]
        if all_values:
            return float(np.mean(all_values))
        return 1000.0  # Safe default baseline
    return float(np.mean(values))


def predict_gdp(
    state: str,
    rainfall: float,
    temperature: float,
    oni_index: float,
    model_name: str | None = None,
) -> dict[str, Any]:
    historical_avg = get_state_historical_avg_gdp(state)
    features = pd.DataFrame([[rainfall, temperature, oni_index]], columns=FEATURE_COLUMNS)

    models_to_run = [model_name] if model_name else MODEL_NAMES
    predictions = []

    from app.constants import MODEL_DISPLAY_NAMES

    for name in models_to_run:
        try:
            model = load_model(name)
            predicted = float(model.predict(features)[0])
            abs_change = round(predicted - historical_avg, 2)
            impact_pct = round((abs_change / historical_avg) * 100, 2) if historical_avg > 0 else 0.0
            predictions.append(
                {
                    "model": name,
                    "model_name_display": MODEL_DISPLAY_NAMES.get(name, name),
                    "predicted_gdp_cr": round(predicted, 2),
                    "predicted_impact_pct": impact_pct,
                    "absolute_change_cr": abs_change,
                }
            )
        except Exception:
            continue

    if not predictions:
        raise ValueError("Could not run predictions. Models not yet trained.")

    ensemble = round(
        float(np.mean([p["predicted_gdp_cr"] for p in predictions])), 2
    )
    ensemble_impact = round(
        float(np.mean([p["predicted_impact_pct"] for p in predictions])), 2
    )

    return {
        "state": state,
        "historical_avg_gdp_cr": round(historical_avg, 2),
        "predictions": predictions,
        "ensemble_gdp_cr": ensemble,
        "ensemble_impact_pct": ensemble_impact,
    }


def log_prediction(
    state: str,
    rainfall: float,
    temperature: float,
    oni_index: float,
    predictions: list[dict],
) -> None:
    db = get_db()
    for pred in predictions:
        db.collection("predictions").add(
            {
                "state": state,
                "input_rainfall": rainfall,
                "input_temperature": temperature,
                "input_oni": oni_index,
                "model_used": pred["model"],
                "predicted_gdp_cr": pred["predicted_gdp_cr"],
                "predicted_impact_pct": pred["predicted_impact_pct"],
                "created_at": datetime.now(timezone.utc)
                .isoformat()
                .replace("+00:00", "Z"),
            }
        )

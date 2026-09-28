"""Standalone training script for the Multi-Model Machine Learning System.

Trains all 5 regression models:
1. Linear Regression (OLS / Baseline)
2. Random Forest Regressor
3. Gradient Boosting Regressor
4. XGBoost Regressor
5. Extra Trees Regressor

Applies chronological time-aware split and stores versioned model artifacts.
"""

import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.services.ml import train_all_models

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    logger.info("==================================================")
    logger.info("PHASE 7 - 11: MULTI-MODEL MACHINE LEARNING TRAINING")
    logger.info("==================================================")

    result = train_all_models()

    print("\n" + "=" * 65)
    print("TRAINING & BENCHMARK RESULTS (TEST DATASET)")
    print("=" * 65)
    print(f"Run ID:            {result.get('run_id')}")
    print(f"Train Years:       {result.get('train_years')}")
    print(f"Test Years:        {result.get('test_years')}")
    print("-" * 65)
    print(f"{'Model':<25} | {'MAE (INR Cr)':<14} | {'RMSE (INR Cr)':<14} | {'R2':<8}")
    print("-" * 65)

    for name, m in result["models"].items():
        is_best = " (BEST)" if name == result["best_model"] else ""
        print(f"{name + is_best:<25} | {m['mae']:<12.2f} | {m['rmse']:<12.2f} | {m['r2']:<8.4f}")

    print("=" * 65)
    print(f"\nEmpirically Selected Best Model: {result['best_model'].upper()}")
    print("Selection Rule: Minimum RMSE on held-out test data without prior algorithm assumptions.\n")


if __name__ == "__main__":
    main()

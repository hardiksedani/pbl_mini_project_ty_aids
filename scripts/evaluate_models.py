"""Model evaluation and benchmarking report generator.

Inspects test metrics across:
- Linear Regression
- Random Forest
- Gradient Boosting
- XGBoost
- Extra Trees

Exports evaluation summary report to data/processed/model_evaluation_report.json.
"""

import json
import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.services.ml import get_model_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    metrics = get_model_metrics()
    if not metrics:
        logger.error("No trained models found in database. Run scripts/train_models.py first.")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("EMPIRICAL MODEL EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Evaluation Timestamp: {metrics.get('trained_at')}")
    print(f"Target Variable:      {metrics.get('target_variable')}")
    print(f"Held-out Test Years:  {metrics.get('test_years')}")
    print("-" * 70)
    print(f"{'Model':<22} | {'MAE':<9} | {'RMSE':<9} | {'R2':<8} | {'MAPE %':<8}")
    print("-" * 70)

    for name, m in metrics["models"].items():
        best_flag = " *" if name == metrics.get("best_model") else ""
        mape_str = f"{m.get('mape', 0.0):.1f}%"
        print(f"{name + best_flag:<22} | {m['mae']:<9.2f} | {m['rmse']:<9.2f} | {m['r2']:<8.4f} | {mape_str:<8}")

    print("=" * 70)
    print(f"* Best Performer on Test Data: {metrics.get('best_model')}")

    out_file = BASE_DIR / "data" / "processed" / "model_evaluation_report.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nReport exported to {out_file}\n")


if __name__ == "__main__":
    main()

"""CLI prediction and scenario testing utility.

Usage:
  python scripts/run_prediction.py --state Maharashtra --rainfall 750 --temp 29.5 --oni 1.5
  python scripts/run_prediction.py --state "Punjab" --preset "Strong El Niño"
"""

import argparse
import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "backend"))

from app.models.schemas import ScenarioRequest
from app.services.ml import predict_gdp
from app.services.scenario_service import PRESET_CONFIGS, run_scenario_simulation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="Run El Nino Agricultural GDP Prediction")
    parser.add_argument("--state", type=str, default="Maharashtra", help="Indian State name")
    parser.add_argument("--rainfall", type=float, default=700.0, help="Rainfall in mm")
    parser.add_argument("--temp", type=float, default=29.0, help="Average temperature in deg C")
    parser.add_argument("--oni", type=float, default=1.5, help="Oceanic Nino Index (-2.0 to +3.0)")
    parser.add_argument("--preset", type=str, default=None, help="Preset name e.g. 'Strong El Nino'")
    args = parser.parse_args()

    print("\n" + "=" * 65)
    print(f"PREDICTION RUN FOR: {args.state.upper()}")
    print("=" * 65)

    if args.preset:
        req = ScenarioRequest(
            state=args.state,
            rainfall=args.rainfall,
            temperature=args.temp,
            oni_index=args.oni,
            preset_name=args.preset,
        )
        res = run_scenario_simulation(req)
        print(f"Preset Applied:       {res.preset_name}")
        print(f"Historical Baseline:  INR {res.historical_avg_gdp_cr:,.1f} Crore")
        print("-" * 65)
        print(f"{'Model':<25} | {'Predicted (INR Cr)':<20} | {'Impact %':<10}")
        print("-" * 65)
        for p in res.predictions:
            print(f"{p.model_name_display:<25} | INR {p.predicted_gdp_cr:<15,.1f} | {p.predicted_impact_pct:+.1f}%")
        print("-" * 65)
        print(f"Ensemble Average:     INR {res.ensemble_gdp_cr:,.1f} Crore ({res.ensemble_impact_pct:+.1f}%)")
        print(f"\nInterpretation: {res.interpretation}")
    else:
        res = predict_gdp(args.state, args.rainfall, args.temp, args.oni)
        print(f"Historical Baseline:  INR {res['historical_avg_gdp_cr']:,.1f} Crore")
        print("-" * 65)
        print(f"{'Model':<25} | {'Predicted (INR Cr)':<20} | {'Impact %':<10}")
        print("-" * 65)
        for p in res["predictions"]:
            print(f"{p['model_name_display']:<25} | INR {p['predicted_gdp_cr']:<15,.1f} | {p['predicted_impact_pct']:+.1f}%")
        print("-" * 65)
        print(f"Ensemble Average:     INR {res['ensemble_gdp_cr']:,.1f} Crore")

    print("\nDisclaimer: Analytical estimate based on panel ML. Not an official government forecast.\n")


if __name__ == "__main__":
    main()

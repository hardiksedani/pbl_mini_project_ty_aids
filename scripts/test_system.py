"""End-to-End System Integration Test.

Tests:
1. Processed Panel Data & SQLite Database
2. Multi-Model Machine Learning System (5 models loaded & evaluated)
3. El Niño Scenario Simulation Engine
4. Two-Tier Search & Knowledge Assistant (intent classification & citations)
5. FastAPI REST API endpoints via TestClient
"""

import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR / "backend"))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def run_tests():
    print("\n" + "=" * 70)
    print("RUNNING END-TO-END VERIFICATION SUITE")
    print("=" * 70)

    # 1. Test Dataset
    from app.services.ml import fetch_climate_dataframe
    df = fetch_climate_dataframe()
    assert not df.empty, "Dataset is empty!"
    assert len(df) >= 150, f"Expected at least 150 panel rows, got {len(df)}"
    assert "rainfall_anomaly" in df.columns, "rainfall_anomaly missing from panel features"
    print(f"[PASS] 1. Panel Dataset: {len(df)} rows across {df['state'].nunique()} states loaded successfully.")

    # 2. Test Multi-Model Evaluation
    from app.services.ml import get_model_metrics, load_model
    from app.constants import MODEL_NAMES
    metrics = get_model_metrics()
    assert metrics is not None, "Model metrics not found in database"
    assert len(metrics["models"]) == 5, f"Expected 5 models, found {len(metrics['models'])}"
    assert metrics["best_model"] in MODEL_NAMES, f"Invalid best model: {metrics['best_model']}"
    for name in MODEL_NAMES:
        m = load_model(name)
        assert m is not None, f"Model {name} failed to load"
    print(f"[PASS] 2. ML System: 5 models operational. Empirical Best: {metrics['best_model']} (RMSE: {metrics['models'][metrics['best_model']]['rmse']:.2f})")

    # 3. Test Scenario Engine
    from app.services.scenario_service import run_scenario_simulation
    from app.models.schemas import ScenarioRequest
    sc_req = ScenarioRequest(state="Maharashtra", rainfall=700.0, temperature=29.0, oni_index=1.5, preset_name="Moderate El Niño")
    sc_res = run_scenario_simulation(sc_req)
    assert len(sc_res.predictions) == 5, "Scenario did not produce predictions for all 5 models"
    assert sc_res.historical_avg_gdp_cr > 0, "Scenario baseline must be positive"
    print(f"[PASS] 3. Scenario Engine: Ran simulation for Maharashtra. Baseline: INR {sc_res.historical_avg_gdp_cr:.1f} Cr | Best Model Impact: {sc_res.best_model_result.predicted_impact_pct:+.1f}%")

    # 4. Test Search Assistant
    from app.services.search_service import answer_search_query
    from app.models.schemas import SearchRequest
    search_res = answer_search_query(SearchRequest(query="How does El Nino affect Indian agriculture and monsoon?"))
    assert search_res.intent in ["factual", "historical", "prediction", "scenario", "mixed"], f"Unknown intent: {search_res.intent}"
    assert len(search_res.citations) > 0, "Search result has zero verified citations"
    print(f"[PASS] 4. Search Assistant: Query classified as '{search_res.intent.upper()}' with {len(search_res.citations)} verified citations.")

    # 5. Test FastAPI TestClient
    from fastapi.testclient import TestClient
    from app.main import app
    client = TestClient(app)

    # Health check
    r = client.get("/health")
    assert r.status_code == 200, f"/health failed: {r.text}"
    assert r.json()["status"] in ["ok", "healthy"]
    print("[PASS] 5a. GET /health -> 200 OK")

    # Dashboard Summary
    r = client.get("/api/dashboard/summary")
    assert r.status_code == 200, f"/api/dashboard/summary failed: {r.text}"
    summary = r.json()
    assert summary["states_count"] == 10, f"Expected 10 states, got {summary['states_count']}"
    print(f"[PASS] 5b. GET /api/dashboard/summary -> 200 OK ({summary['records_count']} records, Best Model: {summary['best_model']})")

    # Model comparison
    r = client.get("/api/models/comparison")
    assert r.status_code == 200, f"/api/models/comparison failed: {r.text}"
    comp = r.json()
    assert len(comp["models"]) == 5, "Expected 5 models in comparison endpoint"
    print("[PASS] 5c. GET /api/models/comparison -> 200 OK (5 models)")

    # States list & single state
    r = client.get("/api/states")
    assert r.status_code == 200
    assert len(r.json()["states"]) == 10
    r = client.get("/api/states/Maharashtra/history")
    assert r.status_code == 200
    assert r.json()["state"] == "Maharashtra"
    print("[PASS] 5d. GET /api/states and /api/states/Maharashtra/history -> 200 OK")

    # Scenario endpoint
    # Predict endpoint
    r = client.post("/api/predict", json={"state": "Maharashtra", "rainfall": 750, "temperature": 29.5, "oni_index": 1.5})
    assert r.status_code == 200, f"/api/predict failed: {r.text}"
    print("[PASS] 5e. POST /api/predict -> 200 OK")

    # Scenario endpoint
    r = client.post("/api/scenario", json={"state": "Punjab", "rainfall": 500, "temperature": 30, "oni_index": 1.2})
    assert r.status_code == 200, f"/api/scenario failed: {r.text}"
    print("[PASS] 5f. POST /api/scenario -> 200 OK")

    # Search endpoint
    r = client.post("/api/search", json={"query": "Which state is most vulnerable to El Nino?"})
    assert r.status_code == 200, f"/api/search failed: {r.text}"
    print("[PASS] 5g. POST /api/search -> 200 OK")

    # Export endpoints
    r = client.get("/api/export/panel?format=csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    r = client.get("/api/export/panel?format=json")
    assert r.status_code == 200
    r = client.get("/api/export/metrics?format=json")
    assert r.status_code == 200
    print("[PASS] 5h. GET /api/export/panel and /api/export/metrics -> 200 OK")

    print("=" * 70)
    print("ALL 11 TEST PHASES PASSED WITH ZERO FAILURES!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_tests()

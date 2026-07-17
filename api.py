import os
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from runtime.core.scenario import Scenario
from runtime.core.runner import Runner

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ton frontend Vite
    allow_methods=["*"],
    allow_headers=["*"],
)

SCENARIOS_DIR = "scenarios/"

def get_scenarios(suite_path):
    from pathlib import Path
    from yaml import safe_load
    suite_dir = Path(suite_path)
    scenarios = []
    for path in sorted(suite_dir.glob("*.yaml")):
        with open(path) as f:
            raw = safe_load(f)
        scenarios.append({
            "id": path.stem,
            "name": raw.get("name", path.stem),
            "description": raw.get("description", ""),
            "checks": len(raw.get("verifier", {}).get("checks", [])),
            "path": str(path),
        })
    return scenarios

@app.get("/scenarios")
def scenario_list():
    return get_scenarios(SCENARIOS_DIR)

@app.post("/scenarios/{scenario_id}")
def run_single_scenario(scenario_id):
    """Run a single scenario and return results."""
    from cli import return_json_summary

    scenario_path = os.path.join(SCENARIOS_DIR, f"{scenario_id}.yaml")
    if not os.path.exists(scenario_path):
        raise HTTPException(status_code=404, detail="Scenario does not exist. Go to /scenarios to check the list of existing scenarios")
    
    scenario = Scenario(scenario_path)
    runner = Runner(verifier=scenario.verifier)

    start = time.time()
    result = runner.run(scenario)
    duration = time.time() - start
    
    return return_json_summary(scenario, scenario_id, result, duration)

@app.post("/run-suite")
def run_suite():
    scenarios = get_scenarios(SCENARIOS_DIR)
    results = []
    for s in scenarios:
        result = run_single_scenario(s["id"])
        results.append(result)
    return {"suite": SCENARIOS_DIR, "results": results}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
    return get_scenarios("SCENARIOS_DIR")
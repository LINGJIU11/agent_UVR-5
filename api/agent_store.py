import json
from pathlib import Path

STORE_FILE = Path("agents.json")

def load_agents() -> dict:
    if STORE_FILE.exists():
        return json.loads(STORE_FILE.read_text(encoding="utf-8"))
    return {}

def save_agents(agents: dict):
    STORE_FILE.write_text(json.dumps(agents, ensure_ascii=False, indent=2), encoding="utf-8")
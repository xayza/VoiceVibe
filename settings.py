"""Settings + history + favorites, stored in config.json next to the app."""
import json
from pathlib import Path

CONFIG = Path(__file__).resolve().parent / "config.json"
HISTORY = Path(__file__).resolve().parent / "history.json"

def load_config():
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_config(data):
    old = load_config()
    old.update(data)
    CONFIG.write_text(json.dumps(old, ensure_ascii=False, indent=2), encoding="utf-8")
    return old

def add_history(entry):
    try:
        items = json.loads(HISTORY.read_text(encoding="utf-8"))
    except Exception:
        items = []
    items.insert(0, entry)
    HISTORY.write_text(json.dumps(items[:50], ensure_ascii=False, indent=2), encoding="utf-8")

def load_history():
    try:
        return json.loads(HISTORY.read_text(encoding="utf-8"))
    except Exception:
        return []

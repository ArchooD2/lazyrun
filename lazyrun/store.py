import json
from appdirs import user_config_dir
from pathlib import Path

CONFIG_DIR = Path(user_config_dir("lazyrun"))
CONFIG_FILE = CONFIG_DIR / "config.json"

CURRENT_VERSION = 3

def _migrate(data: dict) -> dict:
    """Upgrade old shortcut formats to latest versioned format."""
    # ensure our meta block exists and has a groups dict
    if "_meta" not in data:
        data["_meta"] = {
            "version": CURRENT_VERSION,
            "groups": {},
        }
    else:
        data["_meta"].setdefault("groups", {})

    # migrate each entry
    for name, entry in list(data.items()):
        if name == "_meta":
            continue
        if isinstance(entry, str):
            # old: bare string → full entry
            data[name] = {
                "cmd": entry,
                "tags": [],
                "groups": [],
                "version-set": CURRENT_VERSION
            }
        elif isinstance(entry, dict):
            entry.setdefault("cmd", "")
            entry.setdefault("tags", [])
            entry.setdefault("groups", [])
            entry["version-set"] = CURRENT_VERSION

    # bump meta version
    data["_meta"]["version"] = CURRENT_VERSION
    return data

def _load() -> dict:
    """Load and migrate configuration, or return empty if missing/corrupt."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        return {}
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        return _migrate(data)
    except json.JSONDecodeError:
        return {}

def _save(data: dict) -> None:
    """Save the configuration to the JSON file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def get_all() -> dict:
    """Get all saved shortcuts (excluding meta)."""
    data = _load()
    return {k: v for k, v in data.items() if k != "_meta"}

def set_shortcut(name: str, cmd: str) -> None:
    """Set or update a shortcut, preserving tags/groups if present."""
    data = _load()
    if name in data and isinstance(data[name], dict):
        data[name]["cmd"] = cmd
    else:
        data[name] = {
            "cmd": cmd,
            "tags": [],
            "groups": [],
            "version-set": CURRENT_VERSION
        }
    _save(data)

def del_shortcut(name: str) -> None:
    """Delete a shortcut command, if it exists."""
    data = _load()
    data.pop(name, None)
    _save(data)
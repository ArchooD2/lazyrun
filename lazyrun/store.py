import json
from appdirs import user_config_dir
from pathlib import Path

CONFIG_DIR  = Path(user_config_dir("lazyrun"))        # e.g. %LOCALAPPDATA%\lazyrun
CONFIG_FILE = CONFIG_DIR / "config.json"             # or "shortcuts.json"

def _load() -> dict:
    """Load the configuration from the JSON file, or return {} if missing/corrupt."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        # corrupted JSON → start fresh
        return {}

def _save(data: dict) -> None:
    """Save the configuration to the JSON file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def get_all() -> dict:
    """Get all saved shortcuts."""
    return _load()

def set_shortcut(name: str, cmd: str) -> None:
    """Set or overwrite a shortcut command."""
    data = _load()
    data[name] = cmd
    _save(data)

def del_shortcut(name: str) -> None:
    """Delete a shortcut command, if it exists."""
    data = _load()
    data.pop(name, None)
    _save(data)

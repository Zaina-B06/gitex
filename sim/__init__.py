"""Synthetic population simulator. Calls the real rebound_engine.Engine; never copies its logic."""

from pathlib import Path

import yaml

SIM_DIR = Path(__file__).resolve().parent


def _merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_config(scenario: str = "baseline") -> dict:
    cfg = yaml.safe_load((SIM_DIR / "config.yaml").read_text(encoding="utf-8"))
    scenarios = yaml.safe_load((SIM_DIR / "scenarios.yaml").read_text(encoding="utf-8"))
    if scenario not in scenarios:
        raise ValueError(f"unknown scenario {scenario!r}; known: {sorted(scenarios)}")
    return _merge(cfg, scenarios[scenario] or {})

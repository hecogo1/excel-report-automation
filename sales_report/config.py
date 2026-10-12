"""Configuration loading."""
from pathlib import Path
import yaml


def load_config(path: str | Path = "config.yaml") -> dict:
    """Read the YAML configuration file and return it as a dict."""
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)

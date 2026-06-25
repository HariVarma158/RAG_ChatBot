from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "config" / "config.yaml") as f:
    APP_CONFIG = yaml.safe_load(f)

with open(BASE_DIR / "config" / "prompts.yaml") as f:
    PROMPTS = yaml.safe_load(f)
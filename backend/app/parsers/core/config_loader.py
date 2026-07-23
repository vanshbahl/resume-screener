import os
import yaml
from functools import lru_cache

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "config")

@lru_cache(maxsize=None)
def load_config(filename: str) -> dict:
    path = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}

def get_parser_config() -> dict:
    return {
        "sections": load_config("section_patterns.yaml").get("sections", {}),
        "skill_categories": load_config("section_patterns.yaml").get("skill_categories", {}),
        "weights": load_config("confidence_weights.yaml").get("field_weights", {}),
        "date_patterns": load_config("date_patterns.yaml").get("date_patterns", {}),
        "skills_kb": load_config("skills_kb.yaml").get("categories", {})
    }

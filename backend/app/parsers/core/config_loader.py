import os
from functools import lru_cache

import yaml

CONFIG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "config",
)


@lru_cache(maxsize=None)
def load_config(filename: str) -> dict:
    path = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}


@lru_cache(maxsize=None)
def load_normalization_configs() -> dict:
    norm_dir = os.path.join(CONFIG_DIR, "normalization")
    norm_configs = {}
    if os.path.exists(norm_dir):
        for filename in os.listdir(norm_dir):
            if filename.endswith(".yaml") or filename.endswith(".yml"):
                base = os.path.splitext(filename)[0]
                norm_configs[base] = load_config(
                    os.path.join("normalization", filename)
                )
    return norm_configs


def get_parser_config() -> dict:
    return {
        "sections": load_config("section_patterns.yaml").get("sections", {}),
        "jd_sections": load_config("section_patterns.yaml").get("jd_sections", {}),
        "skill_categories": load_config("section_patterns.yaml").get(
            "skill_categories", {}
        ),
        "weights": load_config("confidence_weights.yaml").get("field_weights", {}),
        "date_patterns": load_config("date_patterns.yaml").get("date_patterns", {}),
        "skills_kb": load_config("skills_kb.yaml").get("categories", {}),
        "normalization": load_normalization_configs(),
    }

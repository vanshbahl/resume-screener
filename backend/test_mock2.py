import sys, json, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.parsers.core.config_loader import get_parser_config
print("CONFIG SKILLS:")
print(get_parser_config().get("skill_categories"))

import yaml
import re
text = "Frameworks: FastAPI, React, Django"
categories = {
  "languages": "^(languages|programming languages)$",
  "frameworks": "^(frameworks|libraries|frameworks & libraries)$",
  "tools": "^(tools|developer tools|technologies|software)$"
}
parts = text.split(":", 1)
header = parts[0].strip().lower()
current_cat = "skills"
for cat_name, pattern in categories.items():
    if re.match(pattern, header):
        current_cat = cat_name
        break
print(f"Header: {header}, Cat: {current_cat}")

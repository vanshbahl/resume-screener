import re
from typing import Optional

def parse_date(text: str) -> Optional[str]:
    """
    Extracts dates confidently using regex.
    Common formats: Jan 2023, 2022, 2020-2024, Present.
    """
    if not text: return None
    
    text = text.lower().strip()
    
    if text in ["present", "current", "now"]:
        return "Present"
        
    if re.match(r'^(0?[1-9]|1[0-2])/\d{4}$', text):
        return text
        
    if re.match(r'^\d{4}$', text):
        return text
        
    months = r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)'
    if re.match(rf'^{months}[-\s]\d{{4}}$', text):
        return text.title()
        
    return None

import re

def clean_text(text: str) -> str:
    """
    Normalizes whitespace and removes unnecessary formatting.
    """
    if not text:
        return ""
        
    # Replace unicode non-breaking spaces with regular space
    text = text.replace('\xa0', ' ')
    
    # Remove multiple consecutive newlines (more than 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove multiple consecutive spaces
    text = re.sub(r' {2,}', ' ', text)
    
    # Strip leading/trailing whitespace
    return text.strip()

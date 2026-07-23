import re
from typing import Dict, Any

def generate_structured_json(text: str) -> Dict[str, Any]:
    """
    Generates a structured JSON representation from the cleaned resume text.
    In Phase 1, we do not use AI. We use deterministic regex to extract basic entities (email, phone).
    Complex fields remain empty and will not be hallucinated.
    """
    structured_data = {
        "name": "",
        "email": "",
        "phone": "",
        "skills": [],
        "education": [],
        "experience": [],
        "projects": []
    }
    
    if not text:
        return structured_data
        
    # Deterministic Email Extraction
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email_match:
        structured_data["email"] = email_match.group(0)
        
    # Deterministic Phone Extraction (Handles international and standard US formats)
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    if phone_match:
        structured_data["phone"] = phone_match.group(0)
        
    # Note: Extracting Name without an NLP model like spaCy or an LLM is highly error-prone.
    # Following Phase 1 rules, we leave name, skills, education, experience, and projects empty.
    
    return structured_data

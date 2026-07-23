import json
import os

import spacy
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer

from app.services.extraction import extract_text_from_pdf

# Load NLP Models
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    print(
        "Warning: Failed to load spaCy model. Ensure 'python -m spacy download en_core_web_sm' was run."
    )
    nlp = None

print("Loading SentenceTransformer model...")
embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")

# Load Skills Dictionary
SKILLS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "core", "skills_dictionary.json"
)
with open(SKILLS_FILE, "r") as f:
    MASTER_SKILLS = json.load(f)


def clean_text(text: str) -> str:
    """Uses spaCy to clean and normalize text"""
    if not nlp:
        return text.strip()

    doc = nlp(text)
    # Remove extra whitespace and stop words for cleaner processing
    cleaned = " ".join([token.text for token in doc if not token.is_space])
    return cleaned


def extract_skills(text: str) -> list[str]:
    """Uses RapidFuzz to match text against master skills dictionary"""
    found_skills = set()
    text_lower = text.lower()

    # Simple tokenization for fuzzy matching
    words = text_lower.split()

    for skill in MASTER_SKILLS:
        skill_lower = skill.lower()
        # If it's a multi-word skill, check if it's in the text directly
        if " " in skill_lower and skill_lower in text_lower:
            found_skills.add(skill)
            continue

        # For single word skills, do a rapidfuzz match on words
        for word in words:
            if fuzz.ratio(skill_lower, word) > 90:
                found_skills.add(skill)
                break

    return list(found_skills)


def generate_embeddings(text: str) -> list[float]:
    """Generates a dense vector embedding using sentence-transformers"""
    # Truncate text to fit model context window (approx 512 tokens)
    # For a real app, we'd chunk this properly.
    truncated_text = text[:2000]
    embedding = embedder.encode(truncated_text)
    return embedding.tolist()


def process_resume(file_path: str):
    """
    Main pipeline:
    1. Extract Text
    2. Clean
    3. Extract Skills
    4. Generate Embeddings
    """
    raw_text = extract_text_from_pdf(file_path)
    cleaned_text = clean_text(raw_text)
    skills = extract_skills(cleaned_text)
    embedding = generate_embeddings(cleaned_text)

    return {
        "raw_text": raw_text,
        "parsed_metadata": {"skills": skills},
        "embedding": embedding,
    }

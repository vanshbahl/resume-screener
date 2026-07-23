from rapidfuzz import fuzz
import numpy as np

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculates cosine similarity between two dense vectors"""
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0.0
        
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def score_resume(
    job_skills: list[str], 
    resume_skills: list[str], 
    job_embedding: list[float], 
    resume_embedding: list[float]
) -> float:
    """
    Deterministic scoring algorithm.
    Weights:
    - Hard Skills (RapidFuzz match): 60%
    - Soft Skills/Context (Cosine Similarity): 40%
    """
    # 1. Hard Skills Score (0-60 points)
    matched_skills = 0
    for req_skill in job_skills:
        req_lower = req_skill.lower()
        for res_skill in resume_skills:
            if fuzz.ratio(req_lower, res_skill.lower()) > 90:
                matched_skills += 1
                break
                
    skill_score = 0
    if job_skills:
        skill_percentage = matched_skills / len(job_skills)
        skill_score = skill_percentage * 60.0
    else:
        skill_score = 60.0 # Free points if no skills required
        
    # 2. Semantic Similarity Score (0-40 points)
    sim = cosine_similarity(job_embedding, resume_embedding)
    # Cosine similarity is [-1, 1], normalize to [0, 1] roughly.
    sim_normalized = max(0, sim) 
    semantic_score = sim_normalized * 40.0
    
    final_score = skill_score + semantic_score
    return round(final_score, 2)

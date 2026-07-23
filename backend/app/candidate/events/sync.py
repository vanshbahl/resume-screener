import logging
from sqlalchemy.orm import Session
from app.candidate.repositories.candidate import resume_repo, candidate_repo

# We import the Intelligence layers directly
from app.intelligence.feature_vector_service import feature_vector_service
from app.schemas.intelligence import CandidateProfile
from app.search.index.manager import index_manager

logger = logging.getLogger(__name__)

def sync_candidate_intelligence(db: Session, candidate_id: str):
    """
    Called whenever a candidate's metadata changes or a new resume is processed.
    Extracts the structured_data from the active resume, generates the FeatureVector,
    and indexes the candidate into the Search Engine.
    """
    candidate = candidate_repo.get(db, candidate_id)
    if not candidate:
        logger.error(f"Cannot sync intelligence: Candidate {candidate_id} not found.")
        return

    active_resume = resume_repo.get_active_resume(db, candidate_id)
    if not active_resume or not active_resume.parsed_metadata or "structured_data" not in active_resume.parsed_metadata:
        logger.warning(f"Candidate {candidate_id} has no processed active resume to sync.")
        return

    raw_data = active_resume.parsed_metadata["structured_data"]
    raw_text = active_resume.parsed_metadata.get("raw_text", "")
    
    # 1. Generate Feature Vector
    try:
        vector = feature_vector_service.build_candidate_vector(raw_data)
    except Exception as e:
        logger.error(f"Failed to generate feature vector for candidate {candidate_id}: {e}")
        return

    # 2. Build CandidateProfile Context
    # Incorporate manual tags into the candidate's vector profile for searching
    tags = candidate.tags or []
    if tags:
        # We can append tags to 'skills' or 'frameworks' artificially so they are indexed
        vector.skills.extend([tag.replace("tag_", "") for tag in tags])
        
    profile = CandidateProfile(
        candidate_id=candidate.id,
        raw_data=raw_data,
        vector=vector
    )
    
    # 3. Push to Search Index
    try:
        search_index = index_manager.get_index("candidate")
        search_index.index_document(candidate.id, vector)
        logger.info(f"Successfully synced Candidate {candidate_id} to Search Engine.")
    except Exception as e:
        logger.error(f"Failed to index candidate {candidate_id}: {e}")


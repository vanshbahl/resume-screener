import logging
from sqlalchemy.orm import Session
from app.job.repositories.job import job_description_repo, job_repo

# We import the Intelligence layers directly
from app.intelligence.feature_vector_service import feature_vector_service
from app.schemas.intelligence import JobProfile
from app.search.index.manager import index_manager

logger = logging.getLogger(__name__)

def sync_job_intelligence(db: Session, job_id: str):
    """
    Called whenever a job's metadata changes or a new JobDescription is processed.
    Extracts the structured_data from the active JD, generates the FeatureVector,
    and indexes the Job into the Search Engine.
    """
    job = job_repo.get(db, job_id)
    if not job:
        logger.error(f"Cannot sync intelligence: Job {job_id} not found.")
        return

    active_jd = job_description_repo.get_active_description(db, job_id)
    if not active_jd or not active_jd.parsed_metadata or "structured_data" not in active_jd.parsed_metadata:
        logger.warning(f"Job {job_id} has no processed active JD to sync. Will sync base metadata only.")
        raw_data = {}
    else:
        raw_data = active_jd.parsed_metadata["structured_data"]
    
    # 1. Generate Feature Vector
    try:
        vector = feature_vector_service.build_job_vector(raw_data)
    except Exception as e:
        logger.error(f"Failed to generate feature vector for job {job_id}: {e}")
        return

    # 2. Build JobProfile Context
    # Incorporate manual tags into the job's vector profile for searching
    tags = job.tags or []
    if tags:
        # We can append tags to 'skills' or 'frameworks' artificially so they are indexed
        vector.skills.extend([tag.replace("tag_", "") for tag in tags])
        
    profile = JobProfile(
        job_id=job.id,
        raw_data=raw_data,
        required_vector=vector,
        preferred_vector=vector # In the future, parse preferred vs required
    )
    
    # 3. Push to Search Index
    try:
        search_index = index_manager.get_index("job")
        search_index.index_document(job.id, vector)
        logger.info(f"Successfully synced Job {job_id} to Search Engine.")
    except Exception as e:
        logger.error(f"Failed to index job {job_id}: {e}")

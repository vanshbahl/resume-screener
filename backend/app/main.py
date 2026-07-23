from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.models.domain import Job, Resume, ResumeEmbedding, ResumeStatus
from app.schemas.domain import JobCreate, JobResponse, ResumeResponse
from app.services.pipeline import process_resume, generate_embeddings
from app.services.scoring import score_resume

# In a real app we'd use Alembic. For V1 MVP local dev without Alembic ready, we can uncomment this:
# Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

@app.post("/jobs/", response_model=JobResponse)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = Job(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

@app.get("/jobs/", response_model=list[JobResponse])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    jobs = db.query(Job).offset(skip).limit(limit).all()
    return jobs

def process_resume_background(resume_id: int, file_path: str, job_id: int):
    # This runs outside the HTTP request. Must create its own DB session.
    db = next(get_db())
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not resume or not job:
            return
            
        # 1. Run AI Pipeline
        result = process_resume(file_path)
        
        resume.raw_text = result["raw_text"]
        resume.parsed_metadata = result["parsed_metadata"]
        
        # 2. Generate Job Embedding (Caching this would be better in prod)
        job_embedding = generate_embeddings(job.description or job.title)
        
        # 3. Save Vector
        db_embedding = ResumeEmbedding(
            resume_id=resume.id,
            chunk_text=result["raw_text"][:2000],
            embedding=result["embedding"]
        )
        db.add(db_embedding)
        
        # 4. Score against job
        score = score_resume(
            job_skills=job.required_skills,
            resume_skills=result["parsed_metadata"]["skills"],
            job_embedding=job_embedding,
            resume_embedding=result["embedding"]
        )
        
        resume.final_score = score
        resume.status = ResumeStatus.PROCESSED
        
        db.commit()
    except Exception as e:
        print(f"Error processing resume {resume_id}: {e}")
        db.rollback()
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            resume.status = ResumeStatus.ERROR
            db.commit()
    finally:
        db.close()

@app.post("/jobs/{job_id}/resumes/", response_model=ResumeResponse)
async def upload_resume(
    job_id: int, 
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    db_resume = Resume(job_id=job_id, filename=file.filename)
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    
    background_tasks.add_task(process_resume_background, db_resume.id, file_path, job_id)
    
    return db_resume

@app.get("/jobs/{job_id}/rankings/", response_model=list[ResumeResponse])
def get_rankings(job_id: int, db: Session = Depends(get_db)):
    """Returns resumes for a job, ordered by highest score"""
    resumes = db.query(Resume).filter(
        Resume.job_id == job_id,
        Resume.status == ResumeStatus.PROCESSED
    ).order_by(Resume.final_score.desc()).all()
    
    return resumes

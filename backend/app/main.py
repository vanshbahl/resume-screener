from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import uuid

from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.models.domain import Job, Resume, ResumeEmbedding, ResumeStatus
from app.schemas.domain import JobCreate, JobUpdate, JobResponse, ResumeResponse
from app.parsers.pdf_parser import extract_text_from_pdf
from app.parsers.text_cleaner import clean_text
from app.parsers.json_generator import generate_structured_json

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

@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.put("/jobs/{job_id}", response_model=JobResponse)
def update_job(job_id: int, job_update: JobUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    update_data = job_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(job, key, value)
        
    db.commit()
    db.refresh(job)
    return job

@app.delete("/jobs/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    return None

def process_resume_background(resume_id: int, file_path: str, job_id: int):
    # This runs outside the HTTP request. Must create its own DB session.
    db = next(get_db())
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not resume or not job:
            return
            
        # Milestone 3: Extract and Clean Text (No AI yet)
        raw_pdf_text = extract_text_from_pdf(file_path)
        clean_pdf_text = clean_text(raw_pdf_text)
        
        # Milestone 4: Generate Structured JSON
        structured_data = generate_structured_json(clean_pdf_text)
        
        # Milestone 5: Persist everything (Text, JSON, Metadata)
        # We merge the structured_data into the existing metadata created during upload
        existing_metadata = resume.parsed_metadata or {}
        existing_metadata["structured_data"] = structured_data
        
        resume.raw_text = clean_pdf_text
        resume.parsed_metadata = existing_metadata
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

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = ["application/pdf"]

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
        
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
        
    file_bytes = await file.read()
    file_size = len(file_bytes)
    
    if file_size == 0:
        raise HTTPException(status_code=400, detail="File is empty.")
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the 10MB limit.")
        
    unique_filename = f"{uuid.uuid4().hex}.pdf"
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(file_bytes)
        
    initial_metadata = {
        "original_filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": file_size
    }
        
    db_resume = Resume(
        job_id=job_id, 
        filename=unique_filename,
        parsed_metadata=initial_metadata
    )
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

@app.get("/resumes/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """Retrieves full details of a specific resume."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

@app.get("/resumes/{resume_id}/parsed")
def get_parsed_resume(resume_id: int, db: Session = Depends(get_db)):
    """Retrieves only the structured JSON representation of the resume."""
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    if not resume.parsed_metadata or "structured_data" not in resume.parsed_metadata:
        raise HTTPException(status_code=404, detail="Structured data not available for this resume yet.")
        
    return resume.parsed_metadata["structured_data"]

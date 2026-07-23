import os
import uuid
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.models.domain import Job, Resume, ResumeStatus
from app.schemas.domain import JobCreate, JobUpdate, JobResponse, ResumeResponse
from app.parsers.core.document import ResumeDocument
from app.parsers.pipeline import ParserPipeline
from app.parsers.stages.extraction import PDFExtractionStage
from app.parsers.stages.cleaning import TextCleaningStage
from app.parsers.stages.section_detection import SectionDetectionStage
from app.parsers.stages.entity_extraction import EntityExtractionStage
from app.parsers.stages.normalization import NormalizationStage
from app.parsers.stages.validation import ValidationStage

def get_default_pipeline() -> ParserPipeline:
    return ParserPipeline([
        PDFExtractionStage(),
        TextCleaningStage(),
        SectionDetectionStage(),
        EntityExtractionStage(),
        NormalizationStage(),
        ValidationStage()
    ])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up... Creating database tables if they do not exist.")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
    yield
    logger.info("Shutting down...")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Centralized Exception Handlers
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error occurred: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred while processing the request."},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred."},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

@app.post("/jobs/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    db_job = Job(**job.model_dump())
    db.add(db_job)
    try:
        db.commit()
        db.refresh(db_job)
        return db_job
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(status_code=500, detail="Failed to create job.")

@app.get("/jobs/", response_model=list[JobResponse])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Job).offset(skip).limit(limit).all()

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
        
    try:
        db.commit()
        db.refresh(job)
        return job
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to update job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update job.")

@app.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    try:
        db.delete(job)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Failed to delete job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete job.")
    return None

def process_resume_background(resume_id: int, file_path: str, job_id: int):
    # This runs outside the HTTP request. Must create its own DB session.
    db = next(get_db())
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        job = db.query(Job).filter(Job.id == job_id).first()
        
        if not resume or not job:
            logger.warning(f"Background task aborted: Resume {resume_id} or Job {job_id} not found.")
            return
            
        # Phase 1D: Execute OOP Pipeline
        document = ResumeDocument(file_path=file_path, resume_id=resume_id, job_id=resume.job_id)
        pipeline = get_default_pipeline()
        
        try:
            document = pipeline.run(document)
            structured_data = document.final_json
            clean_pdf_text = "\n".join([line["text"] for line in document.cleaned_lines])
            raw_pdf_text = "\n".join([line["text"] for line in document.raw_lines])
        except Exception as e:
            logger.error(f"Pipeline error for Resume {resume_id}: {e}")
            structured_data = {"error": str(e)}
            clean_pdf_text = ""
            raw_pdf_text = ""
        
        # Milestone 5: Persist everything (Text, JSON, Metadata)
        import copy
        new_metadata = copy.deepcopy(resume.parsed_metadata) if resume.parsed_metadata else {}
        new_metadata["structured_data"] = structured_data
        
        resume.raw_text = clean_pdf_text
        resume.parsed_metadata = new_metadata
        resume.status = ResumeStatus.PROCESSED
        
        db.commit()
        logger.info(f"Resume {resume_id} processed successfully.")
    except Exception as e:
        logger.error(f"Error processing resume {resume_id}: {e}")
        db.rollback()
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            resume.status = ResumeStatus.ERROR
            db.commit()
    finally:
        db.close()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = ["application/pdf"]

@app.post("/jobs/{job_id}/resumes/", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
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
    
    try:
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
        
    except Exception as e:
        logger.error(f"Failed to upload resume: {e}")
        db.rollback()
        # Clean up file if DB fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="Failed to process file upload.")

@app.get("/jobs/{job_id}/rankings/", response_model=list[ResumeResponse])
def get_rankings(job_id: int, db: Session = Depends(get_db)):
    """Returns resumes for a job, ordered by highest score"""
    # Note: AI scoring is disabled in Phase 1, so final_score will be NULL.
    resumes = db.query(Resume).filter(
        Resume.job_id == job_id,
        Resume.status == ResumeStatus.PROCESSED
    ).order_by(Resume.final_score.desc().nulls_last()).all()
    
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

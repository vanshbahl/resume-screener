from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

class SourceInfo(BaseModel):
    page: int
    section: str
    line: int

class ExtractedField(BaseModel):
    value: Any
    confidence: float = 0.0
    source: Optional[SourceInfo] = None

class PersonalInfo(BaseModel):
    name: Optional[ExtractedField] = None
    email: Optional[ExtractedField] = None
    phone: Optional[ExtractedField] = None
    linkedin: Optional[ExtractedField] = None
    github: Optional[ExtractedField] = None
    portfolio: Optional[ExtractedField] = None
    location: Optional[ExtractedField] = None

class ExperienceEntry(BaseModel):
    company: Optional[ExtractedField] = None
    title: Optional[ExtractedField] = None
    start_date: Optional[ExtractedField] = None
    end_date: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    confidence: float = 0.0

class EducationEntry(BaseModel):
    institution: Optional[ExtractedField] = None
    degree: Optional[ExtractedField] = None
    field_of_study: Optional[ExtractedField] = None
    start_date: Optional[ExtractedField] = None
    end_date: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    confidence: float = 0.0

class ProjectEntry(BaseModel):
    name: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    link: Optional[ExtractedField] = None
    confidence: float = 0.0

class CertificationEntry(BaseModel):
    name: Optional[ExtractedField] = None
    issuer: Optional[ExtractedField] = None
    date: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    confidence: float = 0.0

class AchievementEntry(BaseModel):
    description: ExtractedField
    confidence: float = 0.0

class Metadata(BaseModel):
    parser_version: str = "1.2.0"
    schema_version: str = "1.0.0"
    parsed_at: str
    processing_time_ms: int = 0
    page_count: int = 0
    word_count: int = 0
    sections_detected: List[str] = Field(default_factory=list)
    entities_detected: int = 0
    parsing_confidence: float = 0.0
    resume_id: Optional[int] = None
    job_id: Optional[int] = None

class ParsedResumeSchema(BaseModel):
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    summary: Optional[ExtractedField] = None
    skills: List[ExtractedField] = Field(default_factory=list)
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    certifications: List[CertificationEntry] = Field(default_factory=list)
    achievements: List[AchievementEntry] = Field(default_factory=list)
    languages: List[ExtractedField] = Field(default_factory=list)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Metadata

def validate_and_score(parsed_dict: dict) -> dict:
    schema = ParsedResumeSchema(**parsed_dict)
    
    total_confidence = 0.0
    total_fields = 0
    entities_detected = 0
    
    def add_score(field: Optional[ExtractedField], weight=1.0):
        nonlocal total_confidence, total_fields, entities_detected
        total_fields += weight
        if field and field.value:
            total_confidence += (field.confidence * weight)
            entities_detected += 1

    add_score(schema.personal_info.name)
    add_score(schema.personal_info.email)
    add_score(schema.personal_info.phone)
    
    if schema.skills:
        skill_conf = sum(s.confidence for s in schema.skills) / len(schema.skills)
        total_confidence += skill_conf
        entities_detected += len(schema.skills)
    total_fields += 1
    
    if schema.experience:
        exp_conf = sum(e.confidence for e in schema.experience) / len(schema.experience)
        total_confidence += exp_conf
        entities_detected += len(schema.experience)
    total_fields += 1
        
    if schema.education:
        edu_conf = sum(e.confidence for e in schema.education) / len(schema.education)
        total_confidence += edu_conf
        entities_detected += len(schema.education)
    total_fields += 1
        
    schema.metadata.parsing_confidence = round(total_confidence / total_fields, 2) if total_fields else 0.0
    schema.metadata.entities_detected = entities_detected
    return schema.model_dump()

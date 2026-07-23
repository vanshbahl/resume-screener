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
    origin_model: str = "deterministic"

class PersonalInfo(BaseModel):
    name: Optional[ExtractedField] = None
    email: Optional[ExtractedField] = None
    phone: Optional[ExtractedField] = None
    linkedin: Optional[ExtractedField] = None
    github: Optional[ExtractedField] = None
    portfolio: Optional[ExtractedField] = None
    website: Optional[ExtractedField] = None
    location: Optional[ExtractedField] = None

class ExperienceEntry(BaseModel):
    company: Optional[ExtractedField] = None
    title: Optional[ExtractedField] = None
    location: Optional[ExtractedField] = None
    employment_type: Optional[ExtractedField] = None
    start_date: Optional[ExtractedField] = None
    end_date: Optional[ExtractedField] = None
    duration: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    skills_used: List[ExtractedField] = Field(default_factory=list)
    responsibilities: List[ExtractedField] = Field(default_factory=list)
    confidence: float = 0.0

class EducationEntry(BaseModel):
    institution: Optional[ExtractedField] = None
    degree: Optional[ExtractedField] = None
    field_of_study: Optional[ExtractedField] = None
    cgpa: Optional[ExtractedField] = None
    percentage: Optional[ExtractedField] = None
    start_date: Optional[ExtractedField] = None
    end_date: Optional[ExtractedField] = None
    graduation_year: Optional[ExtractedField] = None
    expected_graduation: Optional[ExtractedField] = None
    current_semester: Optional[ExtractedField] = None
    location: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    confidence: float = 0.0

class ProjectEntry(BaseModel):
    name: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    technologies: List[ExtractedField] = Field(default_factory=list)
    link: Optional[ExtractedField] = None
    duration: Optional[ExtractedField] = None
    role: Optional[ExtractedField] = None
    awards: List[ExtractedField] = Field(default_factory=list)
    confidence: float = 0.0

class CertificationEntry(BaseModel):
    name: Optional[ExtractedField] = None
    issuer: Optional[ExtractedField] = None
    date: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    confidence: float = 0.0

class AchievementEntry(BaseModel):
    competition: Optional[ExtractedField] = None
    award: Optional[ExtractedField] = None
    rank: Optional[ExtractedField] = None
    position: Optional[ExtractedField] = None
    organizer: Optional[ExtractedField] = None
    year: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    confidence: float = 0.0

class SpokenLanguageEntry(BaseModel):
    name: ExtractedField
    fluency: Optional[ExtractedField] = None
    confidence: float = 0.0

class Metadata(BaseModel):
    parser_version: str = "1.2.0"
    schema_version: str = "1.0.0"
    parsed_at: str
    processing_time_ms: int = 0
    ai_inference_time_ms: int = 0
    page_count: int = 0
    word_count: int = 0
    sections_detected: List[str] = Field(default_factory=list)
    entities_detected: int = 0
    entities_added_by_ai: int = 0
    entities_modified_by_ai: int = 0
    parsing_confidence: float = 0.0
    model_versions: Dict[str, str] = Field(default_factory=dict)
    resume_id: Optional[int] = None
    job_id: Optional[int] = None

class ParsedResumeSchema(BaseModel):
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    summary: Optional[ExtractedField] = None
    skills: List[ExtractedField] = Field(default_factory=list)
    languages: List[ExtractedField] = Field(default_factory=list)
    spoken_languages: List[SpokenLanguageEntry] = Field(default_factory=list)
    frameworks: List[ExtractedField] = Field(default_factory=list)
    tools: List[ExtractedField] = Field(default_factory=list)
    concepts: List[ExtractedField] = Field(default_factory=list)
    soft_skills: List[ExtractedField] = Field(default_factory=list)
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    certifications: List[CertificationEntry] = Field(default_factory=list)
    achievements: List[AchievementEntry] = Field(default_factory=list)
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
            
    # Core fields are heavily weighted
    add_score(schema.personal_info.name, weight=2.0)
    add_score(schema.personal_info.email, weight=2.0)
    add_score(schema.personal_info.phone, weight=1.5)
    
    # Penalize if name or email is missing
    penalty = 0.0
    if not schema.personal_info.name or not schema.personal_info.name.value:
        penalty += 0.2
    if not schema.personal_info.email or not schema.personal_info.email.value:
        penalty += 0.1
    
    if schema.skills or schema.languages or schema.frameworks or schema.tools or schema.concepts or schema.soft_skills:
        all_skills = schema.skills + schema.languages + schema.frameworks + schema.tools + schema.concepts + schema.soft_skills
        skill_conf = sum(s.confidence for s in all_skills) / len(all_skills)
        total_confidence += skill_conf
        entities_detected += len(all_skills)
    total_fields += 1
    
    if schema.experience:
        exp_conf = sum(e.confidence for e in schema.experience) / len(schema.experience)
        total_confidence += exp_conf
        entities_detected += len(schema.experience)
        # Check if experience descriptions are missing
        for exp in schema.experience:
            if not exp.description or not exp.description.value:
                penalty += 0.05
    total_fields += 1
        
    if schema.education:
        edu_conf = sum(e.confidence for e in schema.education) / len(schema.education)
        total_confidence += edu_conf
        entities_detected += len(schema.education)
    total_fields += 1
        
    base_confidence = total_confidence / total_fields if total_fields else 0.0
    final_confidence = max(0.0, base_confidence - penalty)
    
    schema.metadata.parsing_confidence = round(final_confidence, 2)
    schema.metadata.entities_detected = entities_detected
    return schema.model_dump()

import pytest
from app.schemas.intelligence import FeatureVector
from app.intelligence.feature_vector_service import FeatureVectorService

def test_resume_to_vector():
    service = FeatureVectorService()
    
    raw_resume = {
        "skills": [{"value": "py"}, {"value": "java"}],
        "frameworks": [{"value": "react.js"}],
        "experience": [
            {"duration_months": 12},
            {"duration_months": 24}
        ],
        "education": [
            {"degree": "Bachelor of Science in Computer Science"}
        ]
    }
    
    vector = service.convert_resume_to_vector(raw_resume)
    
    # Check ontology normalization
    assert "Python" in vector.skills
    assert "Java" in vector.skills
    assert "React" in vector.frameworks
    
    # Check experience mapping (36 months = 3.0 years)
    assert vector.years_experience == 3.0
    
    # Check education mapping
    assert vector.education_level == "bachelors"
    
def test_job_to_vectors():
    service = FeatureVectorService()
    
    raw_jd = {
        "required_skills": [{"value": "Python"}],
        "preferred_skills": [{"value": "AWS"}],
        "experience_requirements": 5.0
    }
    
    req, pref = service.convert_job_to_vectors(raw_jd)
    
    assert "Python" in req.skills
    assert "AWS" in pref.skills
    assert req.years_experience == 5.0

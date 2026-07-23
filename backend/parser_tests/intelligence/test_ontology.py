import pytest
from app.intelligence.ontology_service import OntologyService

def test_ontology_loads_and_merges():
    # We scaffolded the config files in config/ontology/
    service = OntologyService("config/ontology")
    
    # Test canonical resolution
    assert service.get_canonical_name("py") == "Python"
    assert service.get_canonical_name("react.js") == "React"
    assert service.get_canonical_name("unknown_skill") == "Unknown_Skill"
    
    # Test family resolution
    assert service.get_semantic_family("Python") == "Backend"
    assert service.get_semantic_family("React") == "Frontend"
    
    # Test prerequisites
    assert "JavaScript" in service.get_prerequisites("React")
    
    # Test siblings
    related = service.get_related("Python")
    assert "Java" in related

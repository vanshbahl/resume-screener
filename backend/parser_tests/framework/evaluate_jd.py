import os
import json
import time
import sys
from typing import Dict, Any, Tuple

# Adjust path so we can import app modules from backend root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.parsers.core.document import JobDocument
from app.main import get_default_pipeline
from parser_tests.framework.metrics import calculate_field_match, calculate_list_metrics, evaluate_complex_list

def load_expected_jd_output(jd_filename: str, expected_dir: str = "parser_tests/datasets/expected_jd_outputs") -> Dict[str, Any]:
    base_name = os.path.splitext(jd_filename)[0]
    expected_path = os.path.join(expected_dir, f"{base_name}.json")
    if not os.path.exists(expected_path):
        return None
    with open(expected_path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_value(field: Any) -> Any:
    if isinstance(field, dict) and "value" in field:
        return field["value"]
    return field

def evaluate_single_jd(txt_path: str, expected_data: Dict[str, Any]) -> Dict[str, Any]:
    """Runs parser on a single JD and compares with expected data."""
    start_time = time.time()
    
    # Run pipeline
    doc = JobDocument(file_path=txt_path)
    pipeline = get_default_pipeline()
    doc = pipeline.run(doc)
    actual_data = doc.final_json
    
    end_time = time.time()
    parsing_time = end_time - start_time
    
    metrics = {
        "parsing_time_sec": round(parsing_time, 2),
        "confidence": doc.metadata.get("parsing_confidence", 0.0),
        "entities_detected": doc.metadata.get("entities_detected", 0),
        "sections": {},
        "overall_accuracy": 0.0
    }
    
    if not expected_data:
        return {"error": "Missing expected data", "actual_data": actual_data, "metrics": metrics}

    total_matched = 0
    total_fields = 0
    
    # 1. Scalar fields
    scalar_keys = ["salary", "employment_type", "location", "experience_requirements"]
    for key in scalar_keys:
        exp_val = extract_value(expected_data.get(key))
        act_val = extract_value(actual_data.get(key))
        is_match = calculate_field_match(exp_val, act_val)
        
        metrics["sections"][key] = {"accuracy": 1.0 if is_match else 0.0}
        total_fields += 1
        if is_match:
            total_matched += 1
            
    # 2. Job Metadata
    exp_jm = expected_data.get("job_metadata", {})
    act_jm = actual_data.get("job_metadata", {})
    jm_metrics = {}
    for key in ["title", "company"]:
        exp_val = extract_value(exp_jm.get(key))
        act_val = extract_value(act_jm.get(key))
        is_match = calculate_field_match(exp_val, act_val)
        jm_metrics[key] = is_match
        
        total_fields += 1
        if is_match:
            total_matched += 1
            
    metrics["sections"]["job_metadata"] = {
        "accuracy": sum(jm_metrics.values()) / len(jm_metrics) if jm_metrics else 0.0,
        "fields": jm_metrics
    }
            
    # 3. Simple Lists
    list_keys = ["education_requirements", "visa_requirements", "required_skills", "preferred_skills", "technologies", "tools", "frameworks", "concepts", "languages"]
    for l_key in list_keys:
        exp_list = expected_data.get(l_key, [])
        act_list = actual_data.get(l_key, [])
        l_metrics = calculate_list_metrics(exp_list, act_list)
        metrics["sections"][l_key] = l_metrics
        
        # Consider F1 score for accuracy contribution
        total_fields += 1
        total_matched += l_metrics["f1"]
        
    metrics["overall_accuracy"] = round(total_matched / total_fields, 4) if total_fields > 0 else 0.0
    
    return {
        "metrics": metrics,
        "actual_data": actual_data
    }

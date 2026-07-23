from typing import Any, Dict, List
from rapidfuzz import fuzz

def normalize_string(s: Any) -> str:
    if s is None:
        return ""
    return str(s).lower().strip()

def calculate_field_match(expected: Any, actual: Any, fuzzy_threshold: float = 90.0) -> bool:
    """Compare a single expected value against the actual value."""
    if expected is None and actual is None:
        return True
    if expected is None and actual is not None:
        return False
    if expected is not None and actual is None:
        return False
        
    str_exp = normalize_string(expected)
    str_act = normalize_string(actual)
    
    if str_exp == str_act:
        return True
        
    score = fuzz.ratio(str_exp, str_act)
    return score >= fuzzy_threshold

def extract_value(field: Any) -> Any:
    """Extracts the 'value' from a parsed field dictionary, or returns the raw value."""
    if isinstance(field, dict) and "value" in field:
        return field["value"]
    return field

def calculate_list_metrics(expected_list: List[Any], actual_list: List[Any], fuzzy_threshold: float = 90.0) -> Dict[str, Any]:
    """Calculate Precision, Recall, F1 for lists of strings/objects."""
    exp_vals = [extract_value(x) for x in expected_list]
    act_vals = [extract_value(x) for x in actual_list]
    
    if not exp_vals and not act_vals:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "tp": 0, "fp": 0, "fn": 0}
        
    tp, fp, fn = 0, 0, 0
    matched_actuals = set()
    
    for exp in exp_vals:
        match_found = False
        for i, act in enumerate(act_vals):
            if i not in matched_actuals and calculate_field_match(exp, act, fuzzy_threshold):
                tp += 1
                matched_actuals.add(i)
                match_found = True
                break
        if not match_found:
            fn += 1
            
    fp = len(act_vals) - len(matched_actuals)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn
    }

def evaluate_complex_list(expected_items: List[Dict], actual_items: List[Dict], match_keys: List[str]) -> Dict[str, Any]:
    """Evaluate complex lists like Experience, Projects, Education."""
    if not expected_items and not actual_items:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "accuracy": 1.0, "details": [], "item_count_diff": 0}
        
    tp_items = 0
    total_fields = 0
    matched_fields = 0
    matched_actual_indices = set()
    details = []

    for exp_item in expected_items:
        best_match_idx = -1
        best_match_score = -1
        
        for i, act_item in enumerate(actual_items):
            if i in matched_actual_indices:
                continue
            
            score = 0
            for key in match_keys:
                exp_val = extract_value(exp_item.get(key))
                act_val = extract_value(act_item.get(key))
                if calculate_field_match(exp_val, act_val, fuzzy_threshold=80.0):
                    score += 1
            
            if score > best_match_score:
                best_match_score = score
                best_match_idx = i
                
        if best_match_idx != -1 and best_match_score > 0:
            matched_actual_indices.add(best_match_idx)
            act_item = actual_items[best_match_idx]
            tp_items += 1
            
            item_details = {}
            for k, exp_raw in exp_item.items():
                total_fields += 1
                act_raw = act_item.get(k)
                
                exp_val = extract_value(exp_raw)
                act_val = extract_value(act_raw)
                
                if isinstance(exp_val, list):
                    list_metrics = calculate_list_metrics(exp_val, act_val or [])
                    item_details[k] = {"type": "list", "metrics": list_metrics}
                    if list_metrics["f1"] >= 0.5:
                        matched_fields += 1
                else:
                    is_match = calculate_field_match(exp_val, act_val)
                    item_details[k] = {"type": "scalar", "match": is_match, "expected": exp_val, "actual": act_val}
                    if is_match:
                        matched_fields += 1
            details.append({"expected": exp_item, "actual": act_item, "field_matches": item_details, "matched": True})
        else:
            details.append({"expected": exp_item, "actual": None, "field_matches": {}, "matched": False})
            for k, exp_val in exp_item.items():
                total_fields += 1
                
    fp_items = len(actual_items) - len(matched_actual_indices)
    
    precision = tp_items / (tp_items + fp_items) if (tp_items + fp_items) > 0 else 0.0
    recall = tp_items / len(expected_items) if expected_items else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = matched_fields / total_fields if total_fields > 0 else 0.0
    
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "accuracy": round(accuracy, 4),
        "details": details,
        "item_count_diff": len(actual_items) - len(expected_items)
    }

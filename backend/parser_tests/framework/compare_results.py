import os
import sys
import json
from typing import Dict, Any

def load_results(run_id: str, results_dir: str = "parser_tests/results/benchmark_results"):
    path = os.path.join(results_dir, run_id, "results.json")
    if not os.path.exists(path):
        print(f"Error: Could not find results.json for run {run_id}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def compare_runs(old_run: str, new_run: str):
    old_data = load_results(old_run)
    new_data = load_results(new_run)
    
    old_sum = old_data.get("summary", {})
    new_sum = new_data.get("summary", {})
    
    print(f"=== Parser Evaluation Comparison ===")
    print(f"Old Run: {old_run}")
    print(f"New Run: {new_run}\n")
    
    o_acc = old_sum.get("overall_accuracy", 0.0)
    n_acc = new_sum.get("overall_accuracy", 0.0)
    diff = n_acc - o_acc
    
    icon = "✅" if diff > 0 else ("❌" if diff < 0 else "➖")
    print(f"Overall Accuracy: {o_acc*100:.2f}% -> {n_acc*100:.2f}% ({diff*100:+.2f}%) {icon}")
    
    o_time = old_sum.get("avg_parsing_time_sec", 0.0)
    n_time = new_sum.get("avg_parsing_time_sec", 0.0)
    t_diff = n_time - o_time
    print(f"Avg Parsing Time: {o_time:.2f}s -> {n_time:.2f}s ({t_diff:+.2f}s)")
    print("\n--- Field-Level Regressions / Improvements ---")
    
    old_resumes = old_data.get("resumes", {})
    new_resumes = new_data.get("resumes", {})
    
    for r_name in new_resumes:
        if r_name not in old_resumes:
            continue
            
        old_m = old_resumes[r_name].get("metrics", {}).get("sections", {})
        new_m = new_resumes[r_name].get("metrics", {}).get("sections", {})
        
        has_changes = False
        report = []
        
        # Check personal info
        o_pi = old_m.get("personal_info", {}).get("fields", {})
        n_pi = new_m.get("personal_info", {}).get("fields", {})
        
        for k in n_pi:
            if k in o_pi and o_pi[k] != n_pi[k]:
                has_changes = True
                status = "Fixed ↗️" if n_pi[k] else "Regressed ↘️"
                report.append(f"    - PI `{k}`: {status}")
                
        # Check complex sections
        for comp in ["experience", "projects", "education"]:
            o_acc = old_m.get(comp, {}).get("accuracy", 0.0)
            n_acc = new_m.get(comp, {}).get("accuracy", 0.0)
            if abs(o_acc - n_acc) > 0.01:
                has_changes = True
                report.append(f"    - {comp.title()} Accuracy: {o_acc*100:.1f}% -> {n_acc*100:.1f}%")
                
        if has_changes:
            print(f"\n📄 {r_name}:")
            print("\n".join(report))
            
    if diff < 0:
        print("\n❌ REGRESSION DETECTED: Overall accuracy dropped.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python compare_results.py <old_run_id> <new_run_id>")
        sys.exit(1)
        
    compare_runs(sys.argv[1], sys.argv[2])

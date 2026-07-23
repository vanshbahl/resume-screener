import os
import sys
import glob
import json
from datetime import datetime

# Adjust path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parser_tests.evaluate_resume import load_expected_output, evaluate_single_resume
from parser_tests.report_generator import generate_reports

def run_benchmarks():
    print("Starting Parser Evaluation & Regression Framework...")
    sample_dir = "parser_tests/sample_resumes"
    if not os.path.exists(sample_dir):
        print(f"Error: Directory {sample_dir} not found.")
        sys.exit(1)
        
    pdf_files = glob.glob(os.path.join(sample_dir, "*.pdf"))
    if not pdf_files:
        print("No resumes found in sample_resumes/. Add some PDFs to test.")
        sys.exit(0)
        
    run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results = {
        "summary": {},
        "resumes": {},
        "warnings": []
    }
    
    total_time = 0.0
    total_acc = 0.0
    processed_count = 0
    
    for pdf in pdf_files:
        basename = os.path.basename(pdf)
        print(f"\nEvaluating {basename}...")
        
        expected = load_expected_output(basename)
        if not expected:
            print(f"  ⚠️ Skipping validation for {basename}: No expected output found in expected_outputs/")
            continue
            
        eval_result = evaluate_single_resume(pdf, expected)
        if "error" in eval_result:
            print(f"  ❌ Error: {eval_result['error']}")
            continue
            
        metrics = eval_result["metrics"]
        results["resumes"][basename] = eval_result
        
        acc = metrics.get("overall_accuracy", 0.0)
        t = metrics.get("parsing_time_sec", 0.0)
        print(f"  ✅ Done. Accuracy: {acc*100:.1f}%, Time: {t}s")
        
        total_time += t
        total_acc += acc
        processed_count += 1

    if processed_count == 0:
        print("\nNo resumes were evaluated.")
        sys.exit(0)
        
    avg_acc = total_acc / processed_count
    results["summary"] = {
        "total_resumes": processed_count,
        "overall_accuracy": round(avg_acc, 4),
        "total_parsing_time_sec": round(total_time, 2),
        "avg_parsing_time_sec": round(total_time / processed_count, 2)
    }
    
    # Generate reports
    print("\nGenerating reports...")
    out_dir = generate_reports(run_id, results)
    print(f"Reports saved to {out_dir}")
    
    # Store regression check logic here later
    # For now, it just calculates and saves
    
    print("\n=== Benchmark Complete ===")
    print(f"Overall Accuracy: {avg_acc*100:.2f}%")

if __name__ == "__main__":
    run_benchmarks()

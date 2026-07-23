import os
import json
import csv
from datetime import datetime
from typing import Dict, Any, List
import matplotlib.pyplot as plt

def ensure_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_reports(run_id: str, results: Dict[str, Any], output_dir: str = "parser_tests/benchmark_results"):
    """Generate comprehensive reports for a benchmark run."""
    run_dir = os.path.join(output_dir, run_id)
    ensure_dir(run_dir)
    
    # 1. Save detailed JSON
    with open(os.path.join(run_dir, "results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    # Extract overall metrics
    overall_accuracy = results.get("summary", {}).get("overall_accuracy", 0.0)
    resume_metrics = results.get("resumes", {})
    
    # 2. Generate Markdown Summary
    generate_markdown_summary(run_id, results, run_dir)
    
    # 3. Generate CSV accuracy table
    generate_accuracy_csv(resume_metrics, run_dir)
    
    # 4. Generate Visuals (Charts)
    generate_charts(resume_metrics, run_dir)
    
    return run_dir

def generate_markdown_summary(run_id: str, results: Dict[str, Any], run_dir: str):
    summary = results.get("summary", {})
    resumes = results.get("resumes", {})
    
    lines = [
        f"# Benchmark Report: {run_id}",
        "",
        f"**Overall Accuracy**: {summary.get('overall_accuracy', 0.0) * 100:.1f}%",
        f"**Total Resumes Processed**: {summary.get('total_resumes', 0)}",
        f"**Average Parsing Time**: {summary.get('avg_parsing_time_sec', 0.0):.2f} sec",
        ""
    ]
    
    # Add Warnings
    warnings = results.get("warnings", [])
    if warnings:
        lines.append("## Warnings / Regressions")
        for w in warnings:
            lines.append(f"- ⚠️ {w}")
        lines.append("")
        
    for r_name, r_data in resumes.items():
        metrics = r_data.get("metrics", {})
        sections = metrics.get("sections", {})
        
        lines.append(f"## Resume: `{r_name}`")
        lines.append(f"**Accuracy**: {metrics.get('overall_accuracy', 0.0) * 100:.1f}%  ")
        lines.append(f"**Confidence**: {metrics.get('confidence', 0.0):.2f}  ")
        lines.append("")
        
        # Breakdown
        lines.append("| Section | Score / Accuracy |")
        lines.append("|---|---|")
        
        if "personal_info" in sections:
            pi_acc = sections["personal_info"].get("accuracy", 0.0)
            lines.append(f"| Personal Info | {pi_acc * 100:.1f}% |")
            
        for comp_key in ["education", "experience", "projects"]:
            if comp_key in sections:
                c_acc = sections[comp_key].get("accuracy", 0.0)
                diff = sections[comp_key].get("item_count_diff", 0)
                diff_str = f" (Count mismatch: {diff})" if diff != 0 else ""
                lines.append(f"| {comp_key.title()} | {c_acc * 100:.1f}%{diff_str} |")
                
        for list_key in ["skills", "languages", "tools"]:
            if list_key in sections:
                l_f1 = sections[list_key].get("f1", 0.0)
                lines.append(f"| {list_key.title()} | F1: {l_f1:.2f} |")
                
        lines.append("")
        
    with open(os.path.join(run_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def generate_accuracy_csv(resume_metrics: Dict[str, Any], run_dir: str):
    headers = ["Resume", "Overall Accuracy", "Parsing Time", "PI Accuracy", "Experience Acc", "Projects Acc", "Education Acc", "Skills F1"]
    rows = []
    
    for r_name, r_data in resume_metrics.items():
        m = r_data.get("metrics", {})
        s = m.get("sections", {})
        
        row = [
            r_name,
            f"{m.get('overall_accuracy', 0.0):.4f}",
            f"{m.get('parsing_time_sec', 0.0):.2f}",
            f"{s.get('personal_info', {}).get('accuracy', 0.0):.4f}",
            f"{s.get('experience', {}).get('accuracy', 0.0):.4f}",
            f"{s.get('projects', {}).get('accuracy', 0.0):.4f}",
            f"{s.get('education', {}).get('accuracy', 0.0):.4f}",
            f"{s.get('skills', {}).get('f1', 0.0):.4f}"
        ]
        rows.append(row)
        
    with open(os.path.join(run_dir, "accuracy_table.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

def generate_charts(resume_metrics: Dict[str, Any], run_dir: str):
    if not resume_metrics: return
    
    names = list(resume_metrics.keys())
    accuracies = [m["metrics"].get("overall_accuracy", 0.0) * 100 for m in resume_metrics.values()]
    times = [m["metrics"].get("parsing_time_sec", 0.0) for m in resume_metrics.values()]
    
    # 1. Accuracy Bar Chart
    plt.figure(figsize=(10, 6))
    plt.bar(names, accuracies, color='skyblue')
    plt.title('Overall Accuracy per Resume')
    plt.ylabel('Accuracy (%)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(run_dir, "accuracy_chart.png"))
    plt.close()
    
    # 2. Parsing Time Chart
    plt.figure(figsize=(10, 6))
    plt.plot(names, times, marker='o', color='coral')
    plt.title('Parsing Time per Resume')
    plt.ylabel('Time (seconds)')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(run_dir, "parsing_time_chart.png"))
    plt.close()

# Parser Evaluation & Regression Framework

This directory contains the automated evaluation and regression testing framework for the AI Resume Screening parser. 
It ensures that any modifications to the deterministic or AI-based extraction logic do not inadvertently degrade extraction quality.

## Folder Structure

- `sample_resumes/`: Place raw PDF resumes here for testing. The framework supports unlimited resumes.
- `expected_outputs/`: Store the manually verified, perfectly correct JSON output for each resume here. The filename must match the PDF filename (e.g., `dummy_resume.json` for `dummy_resume.pdf`).
- `benchmark_results/`: Stores timestamped directories of historical benchmark runs.
- `metrics.py`: Contains the logic for calculating precision, recall, F1 score, and field-level accuracy.
- `evaluate_resume.py`: Handles parsing a single resume and generating metrics.
- `report_generator.py`: Generates Markdown summaries, CSVs, and charts.
- `benchmark_runner.py`: The main entry point to run the entire suite.
- `compare_results.py`: Tool to compare two historical runs.

## Usage

### 1. Run Benchmarks
To run the full suite across all resumes in `sample_resumes/`:
```bash
python parser_tests/benchmark_runner.py
```
This will:
- Process every PDF in `sample_resumes/`.
- Compare the output to the ground truth in `expected_outputs/`.
- Calculate accuracy and F1 metrics.
- Generate a timestamped folder under `benchmark_results/` with charts, CSVs, JSON dumps, and a Markdown summary.

### 2. Compare Parser Versions
To compare the current parser performance against a previous benchmark run:
```bash
python parser_tests/compare_results.py <old_timestamp> <new_timestamp>
```
Example:
```bash
python parser_tests/compare_results.py 2026-07-23_12-00-00 2026-07-23_12-15-00
```
This highlights improvements and flags any regressions.

## Regression Rules

A parser update **MUST fail validation** if:
1. Overall accuracy decreases.
2. Any critical field (email, phone, experience, projects, education) drops below its previous accuracy score.

## Adding New Resumes

1. Copy the new resume PDF into `parser_tests/sample_resumes/`.
2. Create the exact expected JSON output and place it in `parser_tests/expected_outputs/` with a matching base name.
3. Run the benchmark to verify it parses correctly.

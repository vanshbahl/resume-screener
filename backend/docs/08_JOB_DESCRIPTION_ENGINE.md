# Job Description Intelligence Engine

## Architecture Overview

The Job Description (JD) Intelligence Engine is an extension of the primary Document Processing Pipeline. Instead of forking the architecture, we utilize the existing abstract pipeline stages and adapt their behavior dynamically at runtime based on the document type being processed.

The core abstraction that enables this is the `BaseDocument` interface and its two subclasses:
- `ResumeDocument`
- `JobDocument`

By leveraging `JobDocument`, the JD Intelligence Engine securely routes processing through the same 9 pipeline stages:

1. **Extraction (PDF/Text)**: Extracts raw text. For JDs, text files (`.txt`) are natively supported alongside PDFs.
2. **Cleaning**: Sanitizes raw text into clean, structured lines.
3. **Section Detection**: Identifies job-specific sections (`requirements`, `responsibilities`, `benefits`, etc.) using regex heuristics defined in `config/section_patterns.yaml`.
4. **Deterministic Entity Extraction**: Uses `JDExtractor` to parse salary, employment type, location, and other metadata. Leverages the `SkillsExtractor` to deterministically parse required tools and frameworks.
5. **spaCy NER**: Performs generalized Named Entity Recognition (e.g., ORG extraction for company names).
6. **HuggingFace NER**: Uses BERT-based transformers to perform specialized token classification.
7. **Entity Fusion**: Merges extraction sources. For JDs, it prioritizes extracting the hiring company's name.
8. **Normalization**: Deduplicates and sanitizes parsed values.
9. **Validation**: Validates the payload against `ParsedJobSchema` to enforce structural integrity.

## Document Types & Base Interfaces

```python
class BaseDocument(ABC):
    # Common attributes: file_path, raw_lines, cleaned_lines, extracted_entities...

class JobDocument(BaseDocument):
    def __init__(self, file_path: str, job_id: int = None):
        super().__init__(file_path, job_id=job_id)
        self.job_id = job_id
        self.parsed_job = None
```

In any parser stage, you can branch logic seamlessly:
```python
if isinstance(document, JobDocument):
    self._extract_jd(document, context)
else:
    self._extract_resume(document, context)
```

## Configuration

The parser behavior is entirely configuration-driven to prevent embedding business logic inside the pipeline:

- `jd_patterns.yaml`: Regex definitions for capturing attributes like salary, employment type, and years of experience requirements.
- `section_patterns.yaml`: Contains the `jd_sections` configuration mapping headers to semantic sections.
- `synonyms.yaml`: Contains normalization mappings for job-specific fields, such as consolidating "remote", "wfh", and "work from home" under a single canonical term.

## Evaluation Framework

The JD parsing logic is fully integrated into the existing Benchmark Regression Testing framework. Sample JDs and expected output JSONs are processed identically to Resumes.

To run benchmarks on both Resumes and JDs:
```bash
python parser_tests/framework/benchmark_runner.py
```

This enforces the invariant that any modifications to deterministic extraction, AI-based inference, or pipeline structures must objectively improve or preserve extraction accuracy across both Document Types.

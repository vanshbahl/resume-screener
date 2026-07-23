# Intelligent Entity Fusion & Canonical Normalization

## Architecture

The post-extraction pipeline transforms raw entity outputs from Deterministic Regex, spaCy, and Hugging Face pipelines into a clean, highly structured, and provenance-aware dataset. 

It is divided into three primary stages:
1. **Entity Fusion Stage**: Consolidates independent multi-source extraction into single entities with aggregated confidence.
2. **Normalization Stage**: Applies a config-driven rule engine to collapse synonymous variants into canonical strings without losing the original data lineage.
3. **Validation Stage**: Assesses structural completeness and scores parser quality across multiple dimensions.

---

## 1. The EntityEvidence Model

Rather than bloating the root JSON fields, every extracted field contains an optional `evidence` object that traces its origins.

```json
{
  "value": "React",
  "confidence": 0.96,
  "evidence": {
    "detectors": ["deterministic", "huggingface"],
    "sources": ["skills_section", "projects"],
    "confidence_breakdown": {
      "deterministic": 0.8,
      "huggingface": 0.8
    },
    "original_values": ["ReactJS", "React.js"],
    "normalized_from": "ReactJS",
    "merge_reason": "AI fallback confirmed by HF"
  }
}
```

---

## 2. Confidence Engine (Weighted Consensus)

Confidence is NOT simply additive. We use an **Asymptotic Consensus Formula** ($1 - \prod(1 - w_i)$). 
This guarantees that as more independent detectors (Deterministic, spaCy, HF) agree on an entity, the confidence approaches `1.0` but never exceeds it. 

*Example*:
- Deterministic Extraction (Base 0.8)
- HF Extraction (Base 0.6)
- **Final Confidence**: `1 - ((1 - 0.8) * (1 - 0.6))` = **0.92**

---

## 3. Entity Fusion & Conflict Resolution

The deterministic pipeline takes strict priority. 
AI extractions (spaCy/HF) enrich the data but ONLY overwrite a deterministic string if:
1. The AI model returns a high-confidence prediction (>0.85).
2. The AI prediction is a superset of the deterministic string (e.g. `Tech Innovations Inc.` > `Tech`).
Every merge decision generates an explainable `merge_reason` appended to the `evidence`.

**Structured Object Deduplication**:
Complex entities like Experience and Projects are NOT merged purely via text distance algorithms (like RapidFuzz), as this can accidentally merge distinct jobs at the same company. We utilize a **Weighted Structural Comparison**:
- **Experience**: 40% Company Match, 30% Title Match, 30% Date Match. >85% overall similarity triggers a deduplication.

---

## 4. Configuration-Driven Normalization

All mappings have been removed from Python code and exist in `config/normalization/`.
- **Pipeline Execution**: Trim Whitespace -> Canonical Mapping -> Semantic Deduplication.
- **Entity Lineage**: When `React.js` is mapped to `React`, the string `React.js` is preserved inside `evidence.original_values`. This prevents permanent data loss if a YAML config is misconfigured.

---

## 5. Parser Metadata Scores

The Validation stage never deletes invalid data, but rather calculates holistic quality scores that populate the root `metadata` dictionary:
- **Parser Confidence**: The aggregated confidence of all extracted fields.
- **Extraction Coverage**: % of expected sections (Email, Name, Phone, Skills, Experience, Education) detected.
- **Normalization Coverage**: % of extracted fields successfully mapped to a dictionary canonical term.
- **Entity Quality Score**: Metric scaling upward if entities contain multi-detector consensus.
- **Validation Score**: Starts at 100, penalized by generated `ParserWarning` violations.

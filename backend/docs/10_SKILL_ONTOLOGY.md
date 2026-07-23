# Skill Ontology Engine

## Overview

Flat string matching is insufficient for accurate resume parsing and matching. The Skill Ontology Engine resolves this by mapping parsed entities into a strict hierarchy of domains, families, and aliases.

## Architecture

To ensure modularity and scalability without relying on a database in the early stages, the ontology is split across multiple YAML files:
- `config/ontology/languages.yaml`
- `config/ontology/frameworks.yaml`
- `config/ontology/databases.yaml`
- `config/ontology/cloud.yaml`
- `config/ontology/tools.yaml`

The `OntologyService` is a singleton instantiated at runtime. It automatically iterates through the `config/ontology/` directory, merging every YAML into a single in-memory graph. 

## Node Structure

Each canonical node in the ontology can define:
- `aliases`: Alternate names or abbreviations (e.g., `py` for `Python`).
- `family`: The semantic group (e.g., `Backend`, `Frontend`, `DevOps`).
- `prerequisites`: Foundational skills (e.g., `JavaScript` is a prerequisite for `React`).

## Usage

When a raw resume says "I know JS and AWS", the `FeatureVectorService` queries the ontology:
```python
ontology_service.get_canonical_name("JS") # Returns "JavaScript"
```
During matching, if the job requires "GCP" but the candidate only has "AWS", the matching service can lookup:
```python
ontology_service.get_semantic_family("GCP") == ontology_service.get_semantic_family("AWS") # Both return "Cloud"
```
This enables deterministic semantic matching without unpredictable LLM hallucinations.

# Matching Engine

## Overview

The Matching Engine compares standardized `FeatureVector` representations of candidates and jobs to produce deterministic, explainable `MatchResult` objects. The engine heavily relies on the `OntologyService` to resolve aliases, map parent/child skill relations, and compute semantic distance.

## Architecture

1. **Feature Vector Normalization**: 
   - Before matching, a `CandidateProfile` and `JobProfile` are passed through the `FeatureVectorService`. 
   - This converts nested extracted entities into a flat, standardized `FeatureVector` (`skills`, `frameworks`, `years_experience`).

2. **Matching Strategy**:
   - The `MatchingService` performs exact intersection matching first.
   - For missing skills, it queries the `OntologyService` to search for **Semantic/Partial Matches** (e.g., candidate has `React` instead of `Vue`, which belong to the same Frontend framework family).

3. **Separation of Scoring**:
   - The `MatchingService` only produces `Explanation` evidence of what matched and what didn't. 
   - The actual conversion of this evidence into a 0-100 score is delegated to the `ScoringService`, ensuring the matching heuristic is not tightly coupled with weighted importance calculations.

## Configuration

Weights for the `ScoringService` are defined in `config/matching_weights.yaml`:
```yaml
weights:
  technical_skills: 0.30
  experience: 0.25
  projects: 0.15
  education: 0.10
  soft_skills: 0.10
```

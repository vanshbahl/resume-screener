# Candidate Intelligence Engine

## Overview

The Candidate Intelligence Engine is responsible for deriving advanced recruiter-friendly heuristics and generating automated gap analyses. It operates entirely on `FeatureVector` representations.

## Core Modules

### 1. InsightService
The `InsightService` generates qualitative insights into a candidate's background without comparing them to a specific job. 
Insights include:
- **Skill Breadth**: If a candidate lists an abnormally high number of distinct tools/languages.
- **Deep Technology Focus**: If a candidate restricts their tools entirely to one ontology family.
- **Leadership Potential**: Computed via heuristics linking years of experience with specific soft skill keyword occurrences.

### 2. GapAnalysisService
The `GapAnalysisService` compares a candidate's vector directly with a job's vector and highlights exactly what is missing. It isolates:
- Missing Critical Skills
- Missing Preferred Skills
- Experience Gaps (in years)
- Education Gaps

### 3. RecommendationService
A deterministic gap closure engine. Instead of simply reporting that a candidate is missing "AWS", the `RecommendationService` consumes the `GapAnalysis` output and generates an actionable `Recommendation`. 
- Every recommendation is completely rule-based and avoids generative hallucinations.
- E.g., `Action: Learn and build a project using AWS. Estimated Score Improvement: 5.0 points.`

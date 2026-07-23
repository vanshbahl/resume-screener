# Explainable Ranking Engine

## Overview

The Ranking Engine is a generic sorting service that orchestrates the `ScoringService` across multiple targets and orders them. It is designed generically to support future extensions beyond just Candidate-to-Job matching.

## Architecture

The `RankingService` exposes two primary methods:
- `rank_candidates_for_job()`: Takes a `JobProfile` and a list of `ScoreResult` payloads.
- `rank_generic()`: Takes an arbitrary list of `target_id` and `score` pairs.

## Explainability

Explainability is a first-class citizen across the intelligence suite. No ranking decision is a black box. 
Every `ScoreResult` and `MatchResult` generates an array of `Explanation` objects. 

The `RankingService` bubbles up these explanations into the `RankingResult`:
```json
{
  "ranking_context": "Candidates for Job J-101",
  "rankings": [
    {
      "target_id": "Cand-55",
      "score": 92.5,
      "reason": "Rank 1 with score 92.5%. Exceptional alignment."
    }
  ]
}
```
Downstream UI/UX can expand on this by fetching the underlying `Explanations` attached to the `ScoreResult` for `Cand-55` to see exactly which weights influenced the 92.5% score.

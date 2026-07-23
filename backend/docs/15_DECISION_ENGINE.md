# Decision Engine

## Overview

The Decision Engine is responsible for making the final call on a candidate-to-job match. It synthesizes `ScoreResult` and `RiskReport` objects to generate a definitive `DecisionResult`.

## Architecture

### RiskAnalysisService
Before a decision is made, the `RiskAnalysisService` scans the profile for heuristic red flags governed by `config/recommendation/risk_rules.yaml`.
- **Job Hopping**: Detected via high volume of distinct skills mapped to extremely low tenure.
- **Overqualification**: Detected when candidate YOE heavily exceeds job requirements.
- **Skill Mismatch**: Detected when the candidate fails to meet a minimum threshold (e.g., 30%) of the core required skills.

These risks generate a `RiskReport` containing specific `RiskItems` with assigned severities (`low`, `medium`, `high`, `critical`).

### DecisionEngine
The `DecisionEngine` pulls configuration from `config/recommendation/decision_thresholds.yaml`.
It applies hard adjustments (e.g., subtracting 15 points for a "high" risk report, or outright rejecting "critical" risks). 
Based on the final adjusted score, it deterministically outputs:
- **Strong Hire**
- **Hire**
- **Consider**
- **Needs Review**
- **Reject**

Because the engine requires `Explanation` objects, every decision output inherently documents exactly which factors led to the rejection or hire.

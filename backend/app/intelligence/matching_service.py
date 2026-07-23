from typing import List, Set
from app.schemas.intelligence import FeatureVector, MatchResult, Explanation
from app.intelligence.ontology_service import ontology_service

class MatchingService:
    def __init__(self):
        self.ontology = ontology_service

    def _compare_lists(self, candidate_items: List[str], required_items: List[str], category_name: str) -> Explanation:
        """Finds direct, partial, and missing matches for a given list of strings."""
        cand_set = set(candidate_items)
        req_set = set(required_items)
        
        exact_matches = req_set.intersection(cand_set)
        missing = req_set.difference(cand_set)
        
        # Ontology matching (e.g. they don't have "React" but they have "Next.js")
        partial_matches = set()
        still_missing = set()
        
        for req in missing:
            resolved = False
            # Check if candidate has a related skill in the same family
            req_family = self.ontology.get_semantic_family(req)
            if req_family:
                for cand in cand_set:
                    if self.ontology.get_semantic_family(cand) == req_family:
                        partial_matches.add(f"{req} (Matched via {cand} in family {req_family})")
                        resolved = True
                        break
            
            if not resolved:
                still_missing.add(req)
                
        reason = f"Matched {len(exact_matches)} exactly, {len(partial_matches)} partially."
        if still_missing:
            reason += f" Missing {len(still_missing)}."
            
        return Explanation(
            category=category_name,
            matched_entities=list(exact_matches) + list(partial_matches),
            missing_entities=list(still_missing),
            weighted_contribution=0.0, # Handled by ScoringService later
            confidence=1.0 if not partial_matches else 0.8,
            reason=reason,
            evidence=f"Candidate has {len(cand_set)} total {category_name}, job requires {len(req_set)}."
        )

    def match(self, candidate_id: str, job_id: str, candidate_vec: FeatureVector, req_vec: FeatureVector, pref_vec: FeatureVector = None) -> MatchResult:
        """Compares Candidate against Job and produces a deterministic MatchResult."""
        
        explanations = []
        
        # 1. Compare core lists
        for category in ["skills", "frameworks", "tools", "concepts", "languages", "databases", "cloud", "soft_skills"]:
            cand_items = getattr(candidate_vec, category, [])
            req_items = getattr(req_vec, category, [])
            if req_items:
                exp = self._compare_lists(cand_items, req_items, category)
                explanations.append(exp)
                
        # 2. Compare Experience
        exp_reason = "Exceeds required experience."
        if candidate_vec.years_experience < req_vec.years_experience:
            exp_reason = f"Shortfall of {req_vec.years_experience - candidate_vec.years_experience} years."
            
        explanations.append(Explanation(
            category="experience",
            matched_entities=[str(candidate_vec.years_experience)],
            missing_entities=[] if candidate_vec.years_experience >= req_vec.years_experience else [str(req_vec.years_experience)],
            reason=exp_reason,
            evidence=f"Candidate has {candidate_vec.years_experience} YOE. Required: {req_vec.years_experience} YOE."
        ))
        
        # Assemble missing feature vector
        missing_req = FeatureVector()
        matched_feat = FeatureVector()
        
        for exp in explanations:
            if hasattr(missing_req, exp.category):
                setattr(missing_req, exp.category, exp.missing_entities)
            if hasattr(matched_feat, exp.category):
                setattr(matched_feat, exp.category, exp.matched_entities)

        return MatchResult(
            candidate_id=candidate_id,
            job_id=job_id,
            matched_features=matched_feat,
            missing_features_required=missing_req,
            missing_features_preferred=FeatureVector(), # Omitted for brevity
            explanations=explanations
        )

# Singleton instance
matching_service = MatchingService()

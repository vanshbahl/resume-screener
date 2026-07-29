export type PipelineStage =
  | 'idle'
  | 'uploading'
  | 'ingestion'
  | 'parsing'
  | 'profiling'
  | 'scoring'
  | 'complete'
  | 'failed';

export interface ScoreTraceItem {
  rule_id: string;
  category: string;
  delta_type: 'bonus' | 'deduction';
  points: number;
  reason: string;
}

export interface SectionScore {
  category: string;
  raw_score: number;
  weight: number;
  weighted_score: number;
  traces: ScoreTraceItem[];
}

export interface ResumeScore {
  candidate_id: string;
  resume_id: string;
  overall_score: number;
  section_scores: Record<string, SectionScore>;
  strengths: string[];
  weaknesses: string[];
  traces: ScoreTraceItem[];
  confidence: number;
  scoring_version: string;
  generated_at: string;
  metadata?: Record<string, unknown>;
}

export interface ProjectDetail {
  name: string;
  complexity: string;
  technical_depth: string;
  business_impact?: string;
  scale: string;
  modernity: string;
  tech_stack_maturity: string;
}

export interface ExperienceSummary {
  total_years_experience: number;
  relevant_years_experience: number;
  growth_trajectory: string;
  responsibility_level: string;
  leadership_evidence: string[];
  technical_progression: string;
}

export interface EducationSummary {
  highest_qualification: string;
  education_stream: string;
  graduation_status: string;
  institutions: string[];
}

export interface DetectedGap {
  gap_type: string;
  severity: 'warning' | 'info' | 'critical';
  description: string;
}

export interface CandidateProfile {
  candidate_id: string;
  resume_id: string;
  primary_domain: string;
  secondary_domains: string[];
  career_stage: string;
  education_stream: string;
  current_experience_level: string;
  target_roles: string[];
  industry: string;
  seniority: string;
  technical_specialization: string;
  normalized_skills: string[];
  normalized_technologies: string[];
  normalized_companies: string[];
  normalized_institutions: string[];
  normalized_certifications: string[];
  projects: ProjectDetail[];
  experience_summary: ExperienceSummary;
  education_summary: EducationSummary;
  strengths: string[];
  weaknesses: string[];
  detected_gaps: DetectedGap[];
  engine_version: string;
  created_at: string;
}

export interface CandidateResumeDetail {
  id: string;
  candidate_id: string;
  is_active: boolean;
  filename: string;
  parsed_metadata: Record<string, unknown> | null;
  resume_analysis: Record<string, unknown> | null;
  candidate_profile: CandidateProfile | null;
  resume_score: ResumeScore | null;
  parser_version?: string;
  file_hash?: string;
  created_at: string;
}

export interface CandidateResponse {
  id: string;
  status: string;
  tags: string[];
  custom_fields: Record<string, unknown>;
  audit_data: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

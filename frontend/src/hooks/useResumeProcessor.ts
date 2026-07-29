import { useCallback, useRef, useState } from 'react';
import { createCandidate, getResumeDetail, uploadResume } from '../lib/api';
import type { CandidateResumeDetail, PipelineStage } from '../types/resume';

export function useResumeProcessor() {
  const [stage, setStage] = useState<PipelineStage>('idle');
  const [error, setError] = useState<string | null>(null);
  const [candidateId, setCandidateId] = useState<string | null>(null);
  const [resumeId, setResumeId] = useState<string | null>(null);
  const [detail, setDetail] = useState<CandidateResumeDetail | null>(null);
  const [devMode, setDevMode] = useState<boolean>(true); // Default developer mode ON for validation suite

  const pollingRef = useRef<number | null>(null);

  const stopPolling = () => {
    if (pollingRef.current !== null) {
      window.clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  };

  const reset = useCallback(() => {
    stopPolling();
    setStage('idle');
    setError(null);
    setCandidateId(null);
    setResumeId(null);
    setDetail(null);
  }, []);

  const toggleDevMode = useCallback(() => {
    setDevMode((prev) => !prev);
  }, []);

  const downloadDebugBundle = useCallback(() => {
    if (!detail) return;
    const bundle = {
      bundle_info: {
        exported_at: new Date().toISOString(),
        candidate_id: detail.candidate_id,
        resume_id: detail.id,
        filename: detail.filename,
        file_hash: detail.file_hash,
        parser_version: detail.parser_version,
      },
      parsed_metadata: detail.parsed_metadata,
      resume_analysis: detail.resume_analysis,
      candidate_profile: detail.candidate_profile,
      resume_score: detail.resume_score,
    };

    const jsonStr = JSON.stringify(bundle, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `resume_debug_bundle_${detail.id.slice(0, 8)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [detail]);

  const processFile = useCallback(async (file: File) => {
    stopPolling();
    setError(null);
    setDetail(null);

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setStage('failed');
      setError('Unsupported File Format. Please upload a valid PDF document (%PDF magic header required).');
      return;
    }

    try {
      // 1. Uploading
      setStage('uploading');
      const candidate = await createCandidate();
      setCandidateId(candidate.id);

      // 2. Ingestion
      setStage('ingestion');
      const resume = await uploadResume(candidate.id, file);
      setResumeId(resume.id);

      // 3. Polling loop across parsing, profiling, and scoring stages
      setStage('parsing');
      let attempts = 0;
      const maxAttempts = 60; // 30 seconds total (500ms intervals)

      pollingRef.current = window.setInterval(async () => {
        attempts += 1;
        try {
          const current = await getResumeDetail(candidate.id, resume.id);
          setDetail(current);

          if (current.parsed_metadata && !current.candidate_profile) {
            setStage('profiling');
          } else if (current.candidate_profile && !current.resume_score) {
            setStage('scoring');
          } else if (current.resume_score) {
            setStage('complete');
            stopPolling();
          }

          if (attempts >= maxAttempts && !current.resume_score) {
            stopPolling();
            setStage('failed');
            setError('Pipeline processing timed out after 30 seconds. Check backend logs for background task details.');
          }
        } catch (err: unknown) {
          const msg = err instanceof Error ? err.message : 'Error checking processing status.';
          stopPolling();
          setStage('failed');
          setError(msg);
        }
      }, 500);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload failed.';
      setStage('failed');
      setError(msg);
    }
  }, []);

  return {
    stage,
    error,
    candidateId,
    resumeId,
    detail,
    devMode,
    processFile,
    reset,
    toggleDevMode,
    downloadDebugBundle,
  };
}

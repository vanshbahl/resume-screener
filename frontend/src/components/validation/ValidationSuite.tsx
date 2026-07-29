import { useRef, useState } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Code2,
  Copy,
  Cpu,
  Download,
  FileText,
  Layers,
  Loader2,
  RefreshCw,
  Sliders,
  Sparkles,
  Terminal,
  Upload,
} from 'lucide-react';
import { useResumeProcessor } from '../../hooks/useResumeProcessor';
import type { PipelineStage, ScoreTraceItem } from '../../types/resume';

export function ValidationSuite() {
  const {
    stage,
    error,
    detail,
    devMode,
    processFile,
    reset,
    toggleDevMode,
    downloadDebugBundle,
  } = useResumeProcessor();

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const [activeTraceCategory, setActiveTraceCategory] = useState<string>('all');
  const [expandedJson, setExpandedJson] = useState<Record<string, boolean>>({
    score: true,
    profile: false,
    analysis: false,
    metadata: false,
  });

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  const toggleJsonPanel = (panel: string) => {
    setExpandedJson((prev) => ({ ...prev, [panel]: !prev[panel] }));
  };

  const score = detail?.resume_score;
  const profile = detail?.candidate_profile;
  const analysis = detail?.resume_analysis;
  const metadata = detail?.parsed_metadata;

  // Filter traces
  const traces: ScoreTraceItem[] = score?.traces || [];
  const filteredTraces =
    activeTraceCategory === 'all'
      ? traces
      : traces.filter((t) => t.category === activeTraceCategory);

  const getScoreColor = (num: number) => {
    if (num >= 80) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    if (num >= 60) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
  };

  const getStageStep = (s: PipelineStage): number => {
    switch (s) {
      case 'uploading':
      case 'ingestion':
        return 1;
      case 'parsing':
        return 2;
      case 'profiling':
        return 3;
      case 'scoring':
        return 4;
      case 'complete':
        return 5;
      default:
        return 0;
    }
  };

  const currentStep = getStageStep(stage);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans pb-16">
      {/* Top Header & Developer Control Bar */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-30 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Terminal className="w-6 h-6 text-emerald-400" />
            <div>
              <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
                Pipeline Validation Suite
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  Phases 1–3 Complete
                </span>
              </h1>
              <p className="text-xs text-slate-400">
                End-to-end integration tester for PDF Ingestion → Parsing → CandidateProfile → Deterministic ResumeScore
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Developer Mode Toggle */}
            <button
              onClick={toggleDevMode}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                devMode
                  ? 'bg-purple-500/10 border-purple-500/30 text-purple-300 shadow-sm shadow-purple-500/10'
                  : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-slate-200'
              }`}
            >
              <Sliders className="w-3.5 h-3.5" />
              Developer Mode: <span className="font-bold">{devMode ? 'ON' : 'OFF'}</span>
            </button>

            {/* Debug Bundle Export Button */}
            {detail && (
              <button
                onClick={downloadDebugBundle}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/20 transition-all"
                title="Download formatted JSON bundle containing Metadata, Analysis, Profile, and Score"
              >
                <Download className="w-3.5 h-3.5" />
                Download Debug Bundle
              </button>
            )}

            {stage !== 'idle' && (
              <button
                onClick={reset}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 transition-all"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Upload New
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 pt-8 space-y-8">
        {/* Upload Zone (Visible when idle or failed) */}
        {(stage === 'idle' || stage === 'failed') && (
          <section className="space-y-6">
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setIsDragOver(true);
              }}
              onDragLeave={() => setIsDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all ${
                isDragOver
                  ? 'border-emerald-400 bg-emerald-500/5 scale-[1.01]'
                  : 'border-slate-800 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-900/60'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={handleFileChange}
              />
              <div className="w-16 h-16 mx-auto rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-4">
                <Upload className="w-8 h-8 text-emerald-400" />
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">
                Upload Resume PDF to Validate Pipeline
              </h2>
              <p className="text-sm text-slate-400 max-w-md mx-auto mb-4">
                Drag and drop a PDF file here, or click to browse. The backend will parse the PDF, extract entities, build a CandidateProfile, and compute a 0–100 ResumeScore.
              </p>
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-mono bg-slate-800 text-slate-400 border border-slate-700">
                <FileText className="w-3.5 h-3.5 text-emerald-400" />
                Accepts PDF Documents (%PDF magic header validated)
              </div>
            </div>

            {/* Error Banner */}
            {stage === 'failed' && error && (
              <div className="p-4 rounded-xl border border-rose-500/30 bg-rose-500/10 text-rose-300 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
                <div className="flex-1 text-sm">
                  <h3 className="font-semibold text-rose-200 mb-1">Validation Failure</h3>
                  <p>{error}</p>
                </div>
                <button
                  onClick={reset}
                  className="px-3 py-1 rounded bg-rose-500/20 border border-rose-500/40 text-xs font-medium text-rose-200 hover:bg-rose-500/30 transition-all"
                >
                  Retry Upload
                </button>
              </div>
            )}
          </section>
        )}

        {/* Processing State & Pipeline Stage Timeline */}
        {stage !== 'idle' && stage !== 'failed' && (
          <section className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {stage === 'complete' ? (
                  <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                ) : (
                  <Loader2 className="w-6 h-6 text-emerald-400 animate-spin" />
                )}
                <div>
                  <h3 className="font-semibold text-white">
                    {stage === 'complete' ? 'Pipeline Processing Complete' : 'Processing Resume Pipeline...'}
                  </h3>
                  <p className="text-xs text-slate-400">
                    File: <span className="font-mono text-slate-200">{detail?.filename || 'Uploaded Resume'}</span>
                  </p>
                </div>
              </div>

              {devMode && detail?.parser_version && (
                <div className="flex items-center gap-3 text-xs font-mono text-slate-400 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800">
                  <span>Parser: <strong className="text-emerald-400">{detail.parser_version}</strong></span>
                  <span>Profile: <strong className="text-purple-400">2.0.0</strong></span>
                  <span>Scoring: <strong className="text-amber-400">{score?.scoring_version || '3.0.0'}</strong></span>
                </div>
              )}
            </div>

            {/* Timeline Progress Bar */}
            <div className="grid grid-cols-4 gap-3 pt-2">
              {[
                { step: 1, label: '1. PDF Ingestion', desc: 'Pre-persistence validation & deduplication' },
                { step: 2, label: '2. Parser Pipeline', desc: 'NLP, spaCy, HuggingFace NER, Fusion' },
                { step: 3, label: '3. Candidate Profile', desc: 'Entity normalizers & AI evaluator' },
                { step: 4, label: '4. Deterministic Score', desc: 'Rule evaluator & weight aggregation' },
              ].map((s) => {
                const isCurrent = currentStep === s.step;
                const isPassed = currentStep > s.step || currentStep === 5;
                return (
                  <div
                    key={s.step}
                    className={`p-3.5 rounded-xl border transition-all ${
                      isPassed
                        ? 'border-emerald-500/30 bg-emerald-500/5 text-emerald-300'
                        : isCurrent
                        ? 'border-emerald-400 bg-emerald-500/10 text-white animate-pulse'
                        : 'border-slate-800/60 bg-slate-950/40 text-slate-500'
                    }`}
                  >
                    <div className="flex items-center gap-2 font-medium text-xs mb-1">
                      {isPassed ? (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      ) : isCurrent ? (
                        <Loader2 className="w-3.5 h-3.5 text-emerald-400 animate-spin shrink-0" />
                      ) : (
                        <div className="w-3.5 h-3.5 rounded-full border border-slate-700 shrink-0" />
                      )}
                      <span>{s.label}</span>
                    </div>
                    <p className="text-[11px] leading-tight text-slate-400">{s.desc}</p>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* Results Dashboard (Visible when processing is complete or partial data exists) */}
        {score && (
          <section className="space-y-8 animate-in fade-in duration-300">
            {/* 1. Score Overview & Section Score Cards */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Overall Score Badge */}
              <div className={`p-8 rounded-2xl border flex flex-col items-center justify-center text-center ${getScoreColor(score.overall_score)}`}>
                <Sparkles className="w-8 h-8 mb-3 opacity-80" />
                <div className="text-xs uppercase font-bold tracking-wider mb-1 opacity-80">Overall Resume Score</div>
                <div className="text-6xl font-black tracking-tight my-1 font-mono">
                  {score.overall_score}
                  <span className="text-2xl font-normal text-slate-400">/100</span>
                </div>
                <div className="text-xs font-medium px-3 py-1 rounded-full mt-2 bg-slate-950/40 border border-current">
                  Deterministic Score • Confidence: {(score.confidence * 100).toFixed(0)}%
                </div>
              </div>

              {/* Section Score Cards Grid */}
              <div className="lg:col-span-2 grid grid-cols-2 sm:grid-cols-3 gap-3">
                {Object.entries(score.section_scores || {}).map(([key, sec]) => (
                  <div key={key} className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 flex flex-col justify-between">
                    <div className="text-xs font-medium text-slate-400 capitalize mb-2">
                      {key.replace('_', ' ')}
                    </div>
                    <div>
                      <div className="text-2xl font-bold font-mono text-white">
                        {sec.raw_score}
                        <span className="text-xs text-slate-500">/100</span>
                      </div>
                      <div className="text-[11px] text-emerald-400 font-mono mt-0.5">
                        Weighted: +{sec.weighted_score} pts ({(sec.weight * 100).toFixed(0)}%)
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* 2. Strengths & Weaknesses Chips */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40">
                <h3 className="text-sm font-bold text-emerald-400 mb-3 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" /> Detected Strengths ({score.strengths.length})
                </h3>
                <div className="space-y-2">
                  {score.strengths.map((st, i) => (
                    <div key={i} className="text-xs p-2.5 rounded-lg border border-emerald-500/20 bg-emerald-500/5 text-emerald-200">
                      • {st}
                    </div>
                  ))}
                  {score.strengths.length === 0 && <div className="text-xs text-slate-500 italic">No specific strengths flagged.</div>}
                </div>
              </div>

              <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40">
                <h3 className="text-sm font-bold text-rose-400 mb-3 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" /> Areas for Improvement ({score.weaknesses.length})
                </h3>
                <div className="space-y-2">
                  {score.weaknesses.map((wk, i) => (
                    <div key={i} className="text-xs p-2.5 rounded-lg border border-rose-500/20 bg-rose-500/5 text-rose-200">
                      • {wk}
                    </div>
                  ))}
                  {score.weaknesses.length === 0 && <div className="text-xs text-slate-500 italic">No critical weaknesses detected.</div>}
                </div>
              </div>
            </div>

            {/* 3. DEVELOPER MODE: Rule Trace Inspector */}
            {devMode && (
              <div className="p-6 rounded-2xl border border-purple-500/30 bg-slate-900/60 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Code2 className="w-5 h-5 text-purple-400" />
                    <h3 className="font-bold text-white text-sm">Rule Trace Inspector</h3>
                    <span className="text-xs font-mono px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/20">
                      {traces.length} Rules Triggered
                    </span>
                  </div>

                  {/* Category Filter Tabs */}
                  <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
                    {['all', 'contact_structure', 'education', 'experience', 'projects', 'skills', 'writing_quality'].map((cat) => (
                      <button
                        key={cat}
                        onClick={() => setActiveTraceCategory(cat)}
                        className={`px-2.5 py-1 rounded font-medium capitalize transition-all ${
                          activeTraceCategory === cat
                            ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                            : 'text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        {cat === 'all' ? 'All Rules' : cat.replace('_', ' ')}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Traces List */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                  {filteredTraces.map((t, idx) => (
                    <div
                      key={idx}
                      className={`p-3 rounded-xl border font-mono text-xs flex items-start justify-between gap-3 ${
                        t.delta_type === 'bonus'
                          ? 'border-emerald-500/20 bg-emerald-500/5 text-slate-200'
                          : 'border-rose-500/20 bg-rose-500/5 text-slate-200'
                      }`}
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                            t.delta_type === 'bonus' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                          }`}>
                            {t.rule_id}
                          </span>
                          <span className="text-[10px] text-slate-400 capitalize">{t.category.replace('_', ' ')}</span>
                        </div>
                        <p className="font-sans text-xs text-slate-300 leading-snug">{t.reason}</p>
                      </div>
                      <span className={`font-bold text-sm shrink-0 ${t.delta_type === 'bonus' ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {t.points > 0 ? `+${t.points}` : t.points}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 4. DEVELOPER MODE: Candidate Profile Inspector */}
            {devMode && profile && (
              <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-6">
                <div className="flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-emerald-400" />
                  <h3 className="font-bold text-white text-sm">Candidate Profile Understanding</h3>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-500 block mb-1">Primary Domain</span>
                    <strong className="text-emerald-400 text-sm">{profile.primary_domain}</strong>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-500 block mb-1">Career Stage</span>
                    <strong className="text-white text-sm">{profile.career_stage} ({profile.seniority})</strong>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-500 block mb-1">Total YoE</span>
                    <strong className="text-white text-sm">{profile.experience_summary?.total_years_experience || 0} Years</strong>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-slate-500 block mb-1">Highest Degree</span>
                    <strong className="text-white text-sm capitalize">{profile.education_summary?.highest_qualification || 'N/A'}</strong>
                  </div>
                </div>

                {/* Normalized Entities Tags */}
                <div className="space-y-3 pt-2">
                  <div>
                    <span className="text-xs text-slate-400 block mb-1.5 font-medium">Normalized Skills ({profile.normalized_skills?.length || 0}):</span>
                    <div className="flex flex-wrap gap-1.5">
                      {profile.normalized_skills?.map((sk, i) => (
                        <span key={i} className="text-xs px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
                          {sk}
                        </span>
                      ))}
                    </div>
                  </div>

                  {profile.projects?.length > 0 && (
                    <div>
                      <span className="text-xs text-slate-400 block mb-1.5 font-medium">Evaluated Projects:</span>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {profile.projects.map((p, i) => (
                          <div key={i} className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-1">
                            <div className="flex items-center justify-between font-bold text-slate-200">
                              <span>{p.name}</span>
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">{p.complexity}</span>
                            </div>
                            <p className="text-slate-400 text-[11px]">{p.technical_depth}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* 5. DEVELOPER MODE: Raw Collapsible JSON Viewers */}
            {devMode && (
              <div className="space-y-3">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <Layers className="w-4 h-4 text-purple-400" /> Collapsible Raw Pipeline JSON
                </h3>

                {[
                  { key: 'score', label: 'Resume Score JSON', data: score },
                  { key: 'profile', label: 'Candidate Profile JSON', data: profile },
                  { key: 'analysis', label: 'Resume Analysis JSON', data: analysis },
                  { key: 'metadata', label: 'Parsed Metadata JSON', data: metadata },
                ].map(({ key, label, data }) => (
                  <div key={key} className="border border-slate-800 rounded-xl bg-slate-900/60 overflow-hidden">
                    <button
                      onClick={() => toggleJsonPanel(key)}
                      className="w-full px-4 py-3 flex items-center justify-between text-xs font-medium text-slate-300 hover:bg-slate-800/50 transition-all"
                    >
                      <div className="flex items-center gap-2 font-mono">
                        {expandedJson[key] ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                        <span>{label}</span>
                      </div>
                      {data && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            copyToClipboard(JSON.stringify(data, null, 2), key);
                          }}
                          className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 hover:text-white transition-all"
                        >
                          <Copy className="w-3 h-3" />
                          {copiedKey === key ? 'Copied!' : 'Copy'}
                        </button>
                      )}
                    </button>

                    {expandedJson[key] && data && (
                      <pre className="p-4 bg-slate-950 text-emerald-400 font-mono text-[11px] overflow-x-auto border-t border-slate-800 max-h-96 leading-relaxed">
                        {JSON.stringify(data, null, 2)}
                      </pre>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>
        )}
      </main>
    </div>
  );
}

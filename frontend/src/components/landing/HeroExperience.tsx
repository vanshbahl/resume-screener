import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { BrainCircuit, Cpu, GitMerge, FileText, CheckCircle2, ChevronRight } from "lucide-react";

const STAGES = [
  "Raw Document",
  "Text Extraction",
  "Entity Recognition",
  "Knowledge Graph",
  "Intelligence Dashboard",
  "Resume Score",
  "Actionable Insights"
];

export function HeroExperience() {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStageIndex((prev) => (prev + 1) % STAGES.length);
    }, 3500); // 3.5s per stage
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="relative min-h-[100svh] w-full flex flex-col items-center justify-center pt-24 pb-12 overflow-hidden bg-slate-50">
      {/* Subtle Noise Background */}
      <div className="absolute inset-0 bg-noise pointer-events-none z-0 mix-blend-multiply opacity-50" />
      
      {/* Decorative gradient blur */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] bg-indigo-500/5 blur-[120px] rounded-full pointer-events-none z-0" />

      {/* Hero Content */}
      <div className="relative z-10 text-center max-w-4xl mx-auto px-6 mb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
        >
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-700 text-sm font-medium mb-6">
            <BrainCircuit size={16} />
            AI-Powered Analysis
          </span>
          <h1 className="text-5xl md:text-7xl font-semibold tracking-tighter text-slate-900 leading-[1.1] mb-6">
            Know what recruiters see <br />
            <span className="text-slate-400">before they ever see you.</span>
          </h1>
          <p className="text-lg md:text-xl text-slate-600 font-medium max-w-2xl mx-auto leading-relaxed">
            Transform your ordinary resume into structured intelligence. 
            Understand your strengths, benchmark your experience, and optimize for the exact role you want.
          </p>
        </motion.div>
      </div>

      {/* The Transformation Stage */}
      <div className="relative z-10 w-full max-w-5xl h-[500px] mx-auto px-6">
        <div className="w-full h-full relative flex items-center justify-center">
          <AnimatePresence mode="wait">
            <StageVisual key={stageIndex} index={stageIndex} />
          </AnimatePresence>
        </div>

        {/* Stage Indicator */}
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 flex items-center gap-2 text-sm font-medium text-slate-400">
          <AnimatePresence mode="popLayout">
            <motion.span
              key={stageIndex}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-slate-900"
            >
              {STAGES[stageIndex]}
            </motion.span>
          </AnimatePresence>
          <span className="opacity-50">processing...</span>
        </div>
      </div>
    </section>
  );
}

function StageVisual({ index }: { index: number }) {
  switch (index) {
    case 0:
      return <RawDocumentStage />;
    case 1:
      return <TextExtractionStage />;
    case 2:
      return <EntityRecognitionStage />;
    case 3:
      return <KnowledgeGraphStage />;
    case 4:
      return <DashboardStage />;
    case 5:
      return <ScoreStage />;
    case 6:
      return <InsightsStage />;
    default:
      return null;
  }
}

// STAGE 0: Raw Document (Chaotic, unstructured lines of text)
function RawDocumentStage() {
  return (
    <motion.div
      className="paper-card w-[340px] h-[480px] p-8 flex flex-col gap-4 relative"
      initial={{ scale: 0.95, opacity: 0, rotateY: -10 }}
      animate={{ scale: 1, opacity: 1, rotateY: 0 }}
      exit={{ scale: 1.05, opacity: 0, filter: "blur(10px)" }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="w-1/2 h-6 bg-slate-200 rounded-md mb-4" />
      <div className="w-1/3 h-4 bg-slate-200 rounded-md mb-8" />
      
      {[...Array(6)].map((_, i) => (
        <div key={i} className="space-y-2 mb-4">
          <div className="w-3/4 h-3 bg-slate-100 rounded-sm" />
          <div className="w-full h-3 bg-slate-100 rounded-sm" />
          <div className="w-5/6 h-3 bg-slate-100 rounded-sm" />
        </div>
      ))}
      <FileText className="absolute bottom-6 right-6 text-slate-200" size={48} />
    </motion.div>
  );
}

// STAGE 1: Text Extraction (Lines break apart and float)
function TextExtractionStage() {
  return (
    <motion.div
      className="relative w-full h-full flex items-center justify-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 1.1 }}
    >
      {[...Array(12)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute h-3 bg-slate-200 rounded-sm"
          style={{ width: 100 + Math.random() * 150 }}
          initial={{ 
            x: (Math.random() - 0.5) * 100, 
            y: (Math.random() - 0.5) * 100,
            rotate: (Math.random() - 0.5) * 20
          }}
          animate={{ 
            x: (Math.random() - 0.5) * 400, 
            y: (Math.random() - 0.5) * 300,
            rotate: (Math.random() - 0.5) * 40
          }}
          transition={{ duration: 3, ease: "linear" }}
        />
      ))}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="w-16 h-16 rounded-full border-2 border-dashed border-indigo-300 animate-spin-slow flex items-center justify-center">
          <Cpu className="text-indigo-500 animate-pulse" />
        </div>
      </div>
    </motion.div>
  );
}

// STAGE 2: Entity Recognition (Lines turn into tagged chips)
function EntityRecognitionStage() {
  const entities = [
    { label: "React", type: "skill", x: -120, y: -80 },
    { label: "Senior Engineer", type: "title", x: 100, y: -100 },
    { label: "5 Years", type: "duration", x: -80, y: 60 },
    { label: "Python", type: "skill", x: 120, y: 80 },
    { label: "Google", type: "company", x: 0, y: -30 },
    { label: "B.S. Computer Science", type: "education", x: 20, y: 120 },
  ];

  return (
    <motion.div
      className="relative w-full h-full flex items-center justify-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {entities.map((e, i) => (
        <motion.div
          key={i}
          className="absolute px-4 py-2 bg-white border border-slate-200 rounded-full shadow-sm text-sm font-medium text-slate-700"
          initial={{ x: 0, y: 0, scale: 0 }}
          animate={{ x: e.x, y: e.y, scale: 1 }}
          transition={{ duration: 0.8, delay: i * 0.1, type: "spring", bounce: 0.4 }}
        >
          {e.label}
          <span className="ml-2 text-[10px] uppercase tracking-wider text-indigo-500">{e.type}</span>
        </motion.div>
      ))}
    </motion.div>
  );
}

// STAGE 3: Knowledge Graph (Chips connect)
function KnowledgeGraphStage() {
  return (
    <motion.div
      className="relative w-full h-full flex items-center justify-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, filter: "blur(10px)" }}
    >
      <svg className="absolute inset-0 w-full h-full pointer-events-none stroke-indigo-200" strokeWidth="1.5" fill="none">
        <motion.path
          d="M 400 200 Q 500 100 600 200 T 500 350 Z"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2 }}
        />
        <motion.path
          d="M 500 250 L 400 200 L 600 200 L 500 250 L 500 350 L 400 200"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 2, delay: 0.5 }}
        />
      </svg>
      <div className="absolute top-[200px] left-[400px] w-4 h-4 rounded-full bg-indigo-500 shadow-[0_0_15px_rgba(79,70,229,0.5)]" />
      <div className="absolute top-[200px] left-[600px] w-4 h-4 rounded-full bg-indigo-500 shadow-[0_0_15px_rgba(79,70,229,0.5)]" />
      <div className="absolute top-[350px] left-[500px] w-4 h-4 rounded-full bg-indigo-500 shadow-[0_0_15px_rgba(79,70,229,0.5)]" />
      <div className="absolute top-[250px] left-[500px] w-6 h-6 rounded-full bg-slate-900 flex items-center justify-center z-10">
        <GitMerge size={12} className="text-white" />
      </div>
    </motion.div>
  );
}

// STAGE 4: Intelligence Dashboard (Nodes snap into a structured grid)
function DashboardStage() {
  return (
    <motion.div
      className="paper-card w-[600px] h-[350px] p-6 flex flex-col gap-6"
      initial={{ scale: 0.9, opacity: 0, y: 20 }}
      animate={{ scale: 1, opacity: 1, y: 0 }}
      exit={{ scale: 0.95, opacity: 0 }}
      transition={{ duration: 0.8, type: "spring" }}
    >
      <div className="flex items-center gap-4 border-b border-slate-100 pb-4">
        <div className="w-12 h-12 rounded-full bg-slate-100" />
        <div className="space-y-2">
          <div className="w-32 h-4 bg-slate-800 rounded-sm" />
          <div className="w-24 h-3 bg-slate-200 rounded-sm" />
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4 flex-1">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="bg-slate-50 rounded-xl p-4 flex flex-col justify-between border border-slate-100">
            <div className="w-16 h-3 bg-slate-200 rounded-sm" />
            <div className="w-full h-8 bg-indigo-50 rounded-md" />
          </div>
        ))}
      </div>
    </motion.div>
  );
}

// STAGE 5: Resume Score (Large number counts up)
function ScoreStage() {
  const [score, setScore] = useState(0);

  useEffect(() => {
    let current = 0;
    const target = 92;
    const interval = setInterval(() => {
      if (current < target) {
        current += 2;
        setScore(current);
      } else {
        clearInterval(interval);
      }
    }, 30);
    return () => clearInterval(interval);
  }, []);

  return (
    <motion.div
      className="relative flex flex-col items-center justify-center gap-4"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 1.1 }}
    >
      <svg className="absolute w-[300px] h-[300px] -rotate-90">
        <circle cx="150" cy="150" r="140" fill="none" stroke="#f1f5f9" strokeWidth="8" />
        <motion.circle 
          cx="150" cy="150" r="140" fill="none" stroke="#4f46e5" strokeWidth="8" 
          strokeDasharray="879.6" 
          initial={{ strokeDashoffset: 879.6 }}
          animate={{ strokeDashoffset: 879.6 * (1 - score / 100) }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          strokeLinecap="round"
        />
      </svg>
      <div className="text-center z-10">
        <div className="text-8xl font-serif text-slate-900 tracking-tighter">{score}</div>
        <div className="text-sm font-medium text-slate-500 uppercase tracking-widest mt-2">Resume Score</div>
      </div>
    </motion.div>
  );
}

// STAGE 6: Actionable Insights (Recommendations appear)
function InsightsStage() {
  return (
    <motion.div
      className="paper-card w-[500px] p-6 space-y-4"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
    >
      <div className="flex items-center gap-2 mb-6">
        <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse" />
        <span className="text-sm font-semibold text-slate-900">AI Recommendations</span>
      </div>
      {[
        "Quantify your impact at Google with metrics.",
        "Add Docker and Kubernetes to match target JD.",
        "Reorder skills section to prioritize Python/React."
      ].map((insight, i) => (
        <motion.div 
          key={i}
          className="flex items-start gap-3 p-4 rounded-xl bg-slate-50 border border-slate-100"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.3 + 0.2 }}
        >
          <CheckCircle2 className="text-indigo-500 mt-0.5 shrink-0" size={18} />
          <p className="text-sm text-slate-700 font-medium">{insight}</p>
          <ChevronRight className="ml-auto text-slate-300" size={16} />
        </motion.div>
      ))}
    </motion.div>
  );
}

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { CheckCircle2, ChevronRight, Loader2 } from "lucide-react";
import { cn } from "../../lib/utils";

const DEMO_STEPS = [
  "Uploading Resume.pdf...",
  "Parsing layout and geometry...",
  "Extracting Skills & Entities...",
  "Understanding Experience timeline...",
  "Building Semantic Knowledge Graph...",
  "Calculating Industry Score...",
  "Generating actionable recommendations..."
];

export function InteractiveDemo() {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStep((prev) => (prev < DEMO_STEPS.length - 1 ? prev + 1 : 0));
    }, 2000);
    return () => clearInterval(timer);
  }, []);

  return (
    <section id="demo" className="py-32 bg-white relative">
      <div className="max-w-5xl mx-auto px-6">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          
          {/* Demo Terminal/Dashboard */}
          <motion.div
            className="paper-card overflow-hidden bg-slate-900 border-slate-800"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 1 }}
          >
            {/* Terminal Header */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-800 bg-slate-950">
              <div className="w-3 h-3 rounded-full bg-red-500/80" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
              <div className="w-3 h-3 rounded-full bg-green-500/80" />
              <span className="ml-2 text-xs font-mono text-slate-500">pipeline.sh</span>
            </div>

            {/* Terminal Body */}
            <div className="p-6 font-mono text-sm h-[320px] flex flex-col justify-end">
              <div className="space-y-3 w-full">
                {DEMO_STEPS.map((step, idx) => {
                  const isPast = idx < currentStep;
                  const isFuture = idx > currentStep;

                  if (isFuture) return null;

                  return (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      className={cn(
                        "flex items-center gap-3",
                        isPast ? "text-slate-400" : "text-indigo-400"
                      )}
                    >
                      {isPast ? (
                        <CheckCircle2 size={14} className="text-emerald-500" />
                      ) : (
                        <Loader2 size={14} className="animate-spin" />
                      )}
                      <span>{step}</span>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          </motion.div>

          {/* Description */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 1 }}
          >
            <h2 className="text-4xl font-serif text-slate-900 mb-6">Real-time Analysis</h2>
            <p className="text-lg text-slate-600 font-medium mb-8 leading-relaxed">
              Experience the power of our deterministic pipeline. We don't just read words—we understand the semantic relationships between your skills, roles, and achievements.
            </p>
            
            <AnimatePresence mode="popLayout">
              {currentStep === DEMO_STEPS.length - 1 && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="paper-card p-6 bg-indigo-50/50 border-indigo-100"
                >
                  <div className="text-5xl font-serif text-indigo-600 mb-2">91</div>
                  <div className="text-sm font-semibold text-slate-900 uppercase tracking-widest mb-4">Top 8% of Candidates</div>
                  <button className="flex items-center gap-2 text-sm font-medium text-indigo-600 hover:text-indigo-700 transition-colors">
                    View Full Report <ChevronRight size={16} />
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>

        </div>
      </div>
    </section>
  );
}

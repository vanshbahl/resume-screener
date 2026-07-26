import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

export function WhyItMatters() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"]
  });

  const y = useTransform(scrollYProgress, [0, 1], [100, -100]);
  const opacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 1, 1, 0]);

  return (
    <section ref={containerRef} id="why-it-matters" className="py-40 bg-slate-900 text-white overflow-hidden relative">
      <div className="absolute inset-0 bg-noise mix-blend-overlay opacity-20 pointer-events-none" />
      
      <div className="max-w-5xl mx-auto px-6 relative z-10 flex flex-col items-center justify-center text-center">
        <motion.div style={{ y, opacity }}>
          <h2 className="text-5xl md:text-7xl font-serif mb-8 leading-[1.1]">
            Stop guessing. <br />
            <span className="text-indigo-400 font-sans tracking-tight">Start knowing.</span>
          </h2>
          <p className="text-xl md:text-2xl text-slate-400 max-w-3xl mx-auto font-light leading-relaxed">
            Your career is too important to leave to chance. By understanding exactly how an AI parser scores your resume, you gain the ultimate advantage in your job search.
          </p>
        </motion.div>
      </div>
    </section>
  );
}

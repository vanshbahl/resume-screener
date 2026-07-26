import { motion, useScroll, useMotionValueEvent } from "framer-motion";
import { useState } from "react";
import { FileSearch } from "lucide-react";
import { cn } from "../../lib/utils";

export function Navigation() {
  const { scrollY } = useScroll();
  const [scrolled, setScrolled] = useState(false);

  useMotionValueEvent(scrollY, "change", (latest) => {
    setScrolled(latest > 50);
  });

  return (
    <motion.header
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      className={cn(
        "fixed top-0 left-0 right-0 z-50 flex justify-center py-6 px-6 transition-all duration-500",
        scrolled ? "py-4" : "py-8"
      )}
    >
      <div
        className={cn(
          "flex items-center justify-between w-full max-w-6xl transition-all duration-500 rounded-full px-6 py-3",
          scrolled ? "bg-white/70 backdrop-blur-md shadow-sm border border-slate-200/50" : "bg-transparent"
        )}
      >
        {/* Logo */}
        <div className="flex items-center gap-2 cursor-pointer group">
          <div className="bg-indigo-600 p-2 rounded-xl text-white group-hover:scale-105 transition-transform duration-300">
            <FileSearch size={18} strokeWidth={2.5} />
          </div>
          <span className="font-semibold text-lg tracking-tight text-slate-900">
            Resume Intelligence
          </span>
        </div>

        {/* Links */}
        <nav className="hidden md:flex items-center gap-8">
          <a href="#how-it-works" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">
            How it Works
          </a>
          <a href="#demo" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">
            Live Demo
          </a>
          <a href="#why-it-matters" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">
            Insights
          </a>
        </nav>

        {/* CTA */}
        <button className="relative overflow-hidden group px-6 py-2.5 rounded-full bg-slate-900 text-white font-medium text-sm transition-all hover:bg-slate-800 shadow-[0_0_0_0_rgba(79,70,229,0)] hover:shadow-[0_0_20px_0_rgba(79,70,229,0.3)]">
          <span className="relative z-10 flex items-center gap-2">
            Upload Resume
          </span>
          <div className="absolute inset-0 bg-indigo-600 translate-y-[100%] group-hover:translate-y-0 transition-transform duration-300 ease-[0.16,1,0.3,1] z-0" />
          <span className="absolute inset-0 z-10 flex items-center justify-center gap-2 translate-y-[-100%] group-hover:translate-y-0 transition-transform duration-300 ease-[0.16,1,0.3,1] text-white font-medium text-sm">
            Upload Resume
          </span>
        </button>
      </div>
    </motion.header>
  );
}

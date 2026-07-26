import { motion } from "framer-motion";
import { useRef, useState } from "react";
import { Upload } from "lucide-react";

export function FinalUploadCTA() {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (!buttonRef.current) return;
    const { left, top, width, height } = buttonRef.current.getBoundingClientRect();
    const centerX = left + width / 2;
    const centerY = top + height / 2;
    
    // Magnetic pull
    const distanceX = e.clientX - centerX;
    const distanceY = e.clientY - centerY;
    
    setPosition({ x: distanceX * 0.2, y: distanceY * 0.2 });
  };

  const handleMouseLeave = () => {
    setPosition({ x: 0, y: 0 });
  };

  return (
    <section className="py-40 bg-slate-50 relative overflow-hidden">
      <div className="max-w-4xl mx-auto px-6 text-center relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 1 }}
        >
          <h2 className="text-5xl md:text-7xl font-serif text-slate-900 mb-10 tracking-tight">
            Ready to structure your career?
          </h2>
          
          <div className="flex flex-col items-center justify-center gap-6">
            <motion.button
              ref={buttonRef}
              onMouseMove={handleMouseMove}
              onMouseLeave={handleMouseLeave}
              animate={{ x: position.x, y: position.y }}
              transition={{ type: "spring", stiffness: 150, damping: 15, mass: 0.1 }}
              className="relative group px-10 py-5 rounded-full bg-indigo-600 text-white font-medium text-lg overflow-hidden shadow-[0_10px_40px_-10px_rgba(79,70,229,0.5)]"
            >
              <div className="absolute inset-0 bg-slate-900 translate-y-[100%] group-hover:translate-y-0 transition-transform duration-500 ease-[0.16,1,0.3,1] z-0" />
              <span className="relative z-10 flex items-center justify-center gap-3">
                <Upload size={20} />
                Upload Resume
              </span>
            </motion.button>
            
            <button className="text-slate-500 hover:text-slate-900 font-medium text-sm transition-colors border-b border-transparent hover:border-slate-900">
              View Sample Report
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

import { motion } from "framer-motion";

export function TransformationStory() {
  return (
    <section id="story" className="py-32 bg-white relative">
      <div className="max-w-5xl mx-auto px-6">
        <div className="grid md:grid-cols-2 gap-20 items-center">
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
          >
            <h2 className="text-4xl md:text-5xl font-serif text-slate-900 mb-8 leading-tight">
              Chaos becomes <br />
              <span className="text-indigo-600">Structure.</span>
            </h2>
            <p className="text-lg text-slate-600 mb-6 font-medium leading-relaxed">
              A resume begins as an unstructured document. Dense text, irregular formatting, and hidden value.
            </p>
            <p className="text-lg text-slate-600 font-medium leading-relaxed">
              We extract the noise. The information becomes structured. The structured information becomes intelligence. The insights become your competitive edge.
            </p>
          </motion.div>

          <motion.div
            className="relative h-[400px] w-full rounded-3xl bg-slate-50 border border-slate-100 overflow-hidden flex items-center justify-center p-8"
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 1, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
          >
            {/* Visual representation of chaos to structure */}
            <div className="absolute inset-0 bg-noise opacity-30 mix-blend-multiply pointer-events-none" />
            <div className="relative z-10 w-full h-full flex flex-col justify-between">
              <div className="flex gap-4">
                <motion.div 
                  className="w-1/3 h-2 bg-slate-200 rounded-full" 
                  initial={{ rotate: -15, y: 20 }}
                  whileInView={{ rotate: 0, y: 0 }}
                  transition={{ duration: 1, delay: 0.5 }}
                />
                <motion.div 
                  className="w-1/2 h-2 bg-indigo-200 rounded-full"
                  initial={{ rotate: 10, y: -20 }}
                  whileInView={{ rotate: 0, y: 0 }}
                  transition={{ duration: 1, delay: 0.6 }}
                />
              </div>
              <div className="flex flex-col gap-4">
                {[...Array(4)].map((_, i) => (
                  <motion.div 
                    key={i}
                    className="w-full h-12 bg-white rounded-xl border border-slate-100 flex items-center px-4 shadow-sm"
                    initial={{ opacity: 0, x: 20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.6, delay: 0.8 + i * 0.1 }}
                  >
                    <div className="w-8 h-8 rounded-full bg-slate-100 mr-4" />
                    <div className="w-24 h-2 bg-slate-200 rounded-full" />
                    <div className="w-12 h-2 bg-indigo-100 rounded-full ml-auto" />
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

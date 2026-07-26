import { motion } from "framer-motion";
import { UploadCloud, Network, Zap } from "lucide-react";

const steps = [
  {
    icon: <UploadCloud size={24} className="text-indigo-600" />,
    title: "Upload & Parse",
    desc: "Drop your PDF. Our deterministic pipeline handles the extraction flawlessly.",
  },
  {
    icon: <Network size={24} className="text-indigo-600" />,
    title: "Graph Extraction",
    desc: "We build a semantic knowledge graph of your skills, experience, and history.",
  },
  {
    icon: <Zap size={24} className="text-indigo-600" />,
    title: "Score & Benchmark",
    desc: "Instantly see how you rank against industry standards and specific job descriptions.",
  }
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-32 bg-slate-50 relative">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div 
          className="text-center mb-20"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
        >
          <h2 className="text-4xl font-serif text-slate-900 mb-6">Built for Intelligence</h2>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto font-medium">
            Unlike traditional applicant tracking systems that simply read text, we understand context.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, i) => (
            <motion.div
              key={i}
              className="paper-card p-8 group hover:-translate-y-2 transition-transform duration-500"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.8, delay: i * 0.2, ease: [0.16, 1, 0.3, 1] }}
            >
              <div className="w-14 h-14 rounded-2xl bg-indigo-50 flex items-center justify-center mb-8 group-hover:scale-110 transition-transform duration-500">
                {step.icon}
              </div>
              <h3 className="text-xl font-semibold text-slate-900 mb-4">{step.title}</h3>
              <p className="text-slate-600 leading-relaxed font-medium">{step.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

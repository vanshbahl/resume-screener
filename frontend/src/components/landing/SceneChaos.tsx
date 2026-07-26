import {
  motion,
  AnimatePresence,
  useMotionValue,
  useSpring,
  useTransform,
} from "framer-motion";
import { useEffect, useState, useCallback, useRef } from "react";

/*
 * Scene One — "Chaos"
 *
 * An editorial composition: headline left, resume right.
 * The AI quietly begins understanding the document.
 * Entities detach. Structure emerges.
 * Everything softly resets. Seamlessly. Forever.
 */

// ─── Resume Content ───────────────────────────────────────────────────
const RESUME = {
  name:    "Jordan Chen",
  title:   "Staff Software Engineer",
  contact: "San Francisco, CA",
  sections: [
    {
      heading: "Experience",
      items: [
        {
          primary:   "Staff Engineer — Acme Corp",
          secondary: "Led migration of 3 legacy services to event-driven architecture. Reduced p95 latency by 40%.",
          tertiary:  "2021 – Present",
        },
        {
          primary:   "Senior Engineer — Nexus Labs",
          secondary: "Built real-time scoring pipeline processing 2M documents/day.",
          tertiary:  "2018 – 2021",
        },
      ],
    },
    {
      heading: "Skills",
      items: [
        { primary: "Python · TypeScript · Go · React", secondary: "AWS · Kafka · PostgreSQL · Redis", tertiary: "" },
      ],
    },
    {
      heading: "Education",
      items: [
        { primary: "B.S. Computer Science — UC Berkeley", secondary: "", tertiary: "2018" },
      ],
    },
  ],
};

// ─── Entity chips extracted by the AI ────────────────────────────────
// Each chip has: the text, the label category, and final float position
// relative to the scene center (used when detached)
const ENTITIES = [
  { id: "role",      text: "Staff Engineer",   label: "role",      dx: -300, dy: -100 },
  { id: "skills",    text: "Python · React",   label: "skills",    dx:  260, dy:  -70 },
  { id: "tenure",    text: "5+ Years",         label: "tenure",    dx: -240, dy:  110 },
  { id: "arch",      text: "Event-Driven",     label: "expertise", dx:  270, dy:   90 },
  { id: "edu",       text: "UC Berkeley",      label: "education", dx:   30, dy:  200 },
];

// ─── AI Reasoning Messages ────────────────────────────────────────────
const THOUGHTS = [
  "Parsing document structure…",
  "Identifying professional experience…",
  "Detecting technical competencies…",
  "Mapping career trajectory…",
  "Extracting semantic relationships…",
];

// ─── Spring configs ───────────────────────────────────────────────────
const SPRING_GENTLE = { type: "spring" as const, stiffness: 28, damping: 22, mass: 1.4 };
const SPRING_SOFT   = { type: "spring" as const, stiffness: 45, damping: 28, mass: 1.0 };

// ─── Paper texture SVG ────────────────────────────────────────────────
const PAPER_TEXTURE = `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='1'/%3E%3C/svg%3E")`;

export function SceneChaos() {
  // Phase machine:
  // 0 = still (page load pause)
  // 1 = scanning (beam sweeps)
  // 2 = highlighting (entities appear on card)
  // 3 = detaching (entities float away)
  // 4 = floating (entities orbit)
  // 5 = fading (everything dissolves, resets)
  const [phase, setPhase]   = useState(0);
  const [thought, setThought] = useState(0);
  const loopRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  // Mouse parallax for the resume
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const sx = useSpring(mouseX, { stiffness: 18, damping: 32 });
  const sy = useSpring(mouseY, { stiffness: 18, damping: 32 });
  const paperX       = useTransform(sx, [-1, 1], [-10,  10]);
  const paperY       = useTransform(sy, [-1, 1], [-7,    7]);
  const paperRotateY = useTransform(sx, [-1, 1], [-2.5, 2.5]);
  const paperRotateX = useTransform(sy, [-1, 1], [ 1.5, -1.5]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    mouseX.set((e.clientX / window.innerWidth  - 0.5) * 2);
    mouseY.set((e.clientY / window.innerHeight - 0.5) * 2);
  }, [mouseX, mouseY]);

  // Phase timeline
  useEffect(() => {
    const schedule = [
      { delay: 1800, next: 1 }, // still    → scanning
      { delay: 2800, next: 2 }, // scanning → highlighting
      { delay: 2000, next: 3 }, // highlight→ detaching
      { delay: 3200, next: 4 }, // detaching→ floating
      { delay: 4500, next: 5 }, // floating → fading
      { delay: 2000, next: 0 }, // fading   → reset
    ];
    const step = schedule[phase];
    if (!step) return;
    loopRef.current = setTimeout(() => {
      setPhase(step.next);
      if (step.next > 0 && step.next <= 4) setThought(step.next - 1);
    }, step.delay);
    return () => clearTimeout(loopRef.current);
  }, [phase]);

  const isResumeVisible = phase <= 3;
  const isScanning      = phase === 1;
  const isHighlighting  = phase >= 2 && phase <= 3;
  const isDetached      = phase >= 3;
  const isFloating      = phase >= 4;
  const isFading        = phase === 5;

  return (
    <section
      className="relative min-h-screen w-full overflow-hidden flex items-center justify-center"
      style={{ background: "var(--color-paper)" }}
      onMouseMove={handleMouseMove}
    >
      {/* ── Subtle paper grain overlay ── */}
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.018] mix-blend-multiply"
        style={{ backgroundImage: PAPER_TEXTURE }}
      />

      {/* ── Volumetric soft light (bleeds behind both headline and resume) ── */}
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[700px] pointer-events-none"
        style={{
          background: "radial-gradient(ellipse 60% 50% at 55% 50%, rgba(67,56,202,0.04) 0%, transparent 80%)",
          filter: "blur(40px)",
        }}
      />

      {/* ─────────────────────────────────────────────────────────────────
          DESKTOP LAYOUT: Editorial two-column — headline left, resume right
          MOBILE LAYOUT: Stacked — resume centered, headline above
      ─────────────────────────────────────────────────────────────────── */}
      <div className="relative z-10 w-full max-w-6xl mx-auto px-8 flex flex-col md:flex-row items-center gap-16 md:gap-24">

        {/* ── Left Column: Headline ── */}
        <motion.div
          className="flex-none md:w-[42%] text-left"
          initial={{ opacity: 0, x: -24 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 1.6, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
        >
          <h1
            className="text-[clamp(3.2rem,6.5vw,6rem)] leading-[1.0] tracking-[-0.04em] text-[var(--color-ink)]"
            style={{ fontFamily: "var(--font-serif)" }}
          >
            Intelligence
            <br />
            <span
              className="italic"
              style={{ color: "var(--color-ink)", opacity: 0.28 }}
            >
              from chaos.
            </span>
          </h1>

          {/* Subline — quiet, monospaced */}
          <motion.p
            className="mt-6 text-[13px] font-mono uppercase tracking-[0.18em] text-[var(--color-ink)]/35 leading-relaxed"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1.4, delay: 0.9 }}
          >
            Resume Intelligence
            <br />
            understands careers.
          </motion.p>

          {/* AI thought — under the subline */}
          <div className="mt-10 h-5">
            <AnimatePresence mode="wait">
              {phase > 0 && phase < 5 && (
                <motion.div
                  key={thought}
                  initial={{ opacity: 0, y: 5, filter: "blur(4px)" }}
                  animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                  exit={{ opacity: 0, y: -5, filter: "blur(4px)" }}
                  transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                  className="text-[11px] font-mono tracking-widest uppercase"
                  style={{ color: "var(--color-intelligence)", opacity: 0.7 }}
                >
                  {THOUGHTS[thought]}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>

        {/* ── Right Column: Resume ── */}
        <div className="relative flex-none" style={{ perspective: "1600px" }}>
          <motion.div
            style={{
              x: paperX,
              y: paperY,
              rotateX: paperRotateX,
              rotateY: paperRotateY,
            }}
            animate={{
              opacity: isFading ? 0 : 1,
              scale:   isFading ? 0.93 : 1,
            }}
            transition={{ duration: 2.0, ease: [0.16, 1, 0.3, 1] }}
          >
            {/* Volumetric light bloom behind paper */}
            <div
              className="absolute -inset-16 pointer-events-none"
              style={{
                background:
                  "radial-gradient(ellipse at center, rgba(67,56,202,0.06) 0%, transparent 65%)",
                filter: "blur(50px)",
              }}
            />

            {/* Layer 2 — deepest shadow sheet */}
            <div
              className="absolute inset-0 rounded-sm bg-white pointer-events-none"
              style={{
                transform: "rotate(-3deg) translate(-10px, 14px)",
                border: "1px solid rgba(0,0,0,0.025)",
                opacity: 0.45,
                boxShadow: "0 8px 30px rgba(0,0,0,0.04)",
              }}
            />
            {/* Layer 1 — middle sheet */}
            <div
              className="absolute inset-0 rounded-sm bg-white pointer-events-none"
              style={{
                transform: "rotate(1.8deg) translate(6px, 8px)",
                border: "1px solid rgba(0,0,0,0.035)",
                opacity: 0.65,
                boxShadow: "0 6px 20px rgba(0,0,0,0.04)",
              }}
            />

            {/* Layer 0 — main paper */}
            <motion.div
              className="relative w-[320px] md:w-[360px] bg-[#fafafa] rounded-sm overflow-hidden"
              style={{
                boxShadow:
                  "0 60px 120px -20px rgba(0,0,0,0.18), 0 24px 60px -12px rgba(0,0,0,0.07), 0 4px 16px rgba(0,0,0,0.03)",
                border: "1px solid rgba(0,0,0,0.055)",
              }}
              animate={{
                y:        isResumeVisible ? [0, -9, 0] : -30,
                rotateZ:  isResumeVisible ? [-0.4, 0.4, -0.4] : 0,
                opacity:  isResumeVisible ? 1 : 0,
              }}
              transition={{
                y:       isResumeVisible
                  ? { duration: 9, repeat: Infinity, ease: "easeInOut" }
                  : SPRING_GENTLE,
                rotateZ: isResumeVisible
                  ? { duration: 14, repeat: Infinity, ease: "easeInOut" }
                  : { duration: 0 },
                opacity: SPRING_GENTLE,
              }}
            >
              {/* Paper noise */}
              <div
                className="absolute inset-0 pointer-events-none opacity-[0.045] mix-blend-multiply"
                style={{ backgroundImage: PAPER_TEXTURE }}
              />

              {/* Resume content */}
              <div className="px-8 py-9 space-y-5 text-left">
                {/* Header */}
                <div className="mb-5 pb-4 border-b border-[var(--color-ink)]/[0.06]">
                  <div className="text-base font-semibold text-[var(--color-ink)] tracking-tight">
                    {RESUME.name}
                  </div>
                  <div className="text-xs text-[var(--color-ink)]/50 mt-0.5 tracking-wide">
                    {RESUME.title}
                  </div>
                  <div className="text-[10px] text-[var(--color-ink)]/28 mt-0.5 font-mono">
                    {RESUME.contact}
                  </div>
                </div>

                {/* Sections */}
                {RESUME.sections.map((section, si) => (
                  <div key={si}>
                    <div className="text-[9px] font-mono uppercase tracking-[0.18em] text-[var(--color-ink)]/28 mb-2">
                      {section.heading}
                    </div>
                    <div className="space-y-3">
                      {section.items.map((item, ii) => (
                        <div key={ii}>
                          <div className="text-[12.5px] font-medium text-[var(--color-ink)]/82 leading-snug">
                            {item.primary}
                          </div>
                          {item.secondary && (
                            <div className="text-[10.5px] text-[var(--color-ink)]/38 mt-0.5 leading-relaxed">
                              {item.secondary}
                            </div>
                          )}
                          {item.tertiary && (
                            <div className="text-[9px] font-mono text-[var(--color-ink)]/22 mt-0.5">
                              {item.tertiary}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* AI Scan beam */}
              <motion.div
                className="absolute left-0 right-0 h-12 pointer-events-none"
                style={{
                  background:
                    "linear-gradient(to bottom, transparent, rgba(67,56,202,0.05), rgba(67,56,202,0.1), rgba(67,56,202,0.05), transparent)",
                  borderTop:    "1px solid rgba(67,56,202,0.12)",
                  borderBottom: "1px solid rgba(67,56,202,0.08)",
                }}
                initial={{ top: "-20%", opacity: 0 }}
                animate={{
                  top:     isScanning ? "110%" : "-20%",
                  opacity: isScanning ? 1 : 0,
                }}
                transition={{ duration: 4.0, ease: [0.4, 0, 0.6, 1] }}
              />
            </motion.div>
          </motion.div>
        </div>
      </div>

      {/* ── Detached Entity Chips ── */}
      {/* These orbit in the absolute space of the section, not relative to the column */}
      {ENTITIES.map((entity, i) => (
        <motion.div
          key={entity.id}
          className="absolute z-20 flex items-center gap-0"
          style={{
            // Start near the right column center
            left: "50%",
            top:  "50%",
          }}
          initial={false}
          animate={{
            x: isDetached
              ? entity.dx + 130  /* offset rightward to near-resume space */
              : 80,
            y: isDetached ? entity.dy : 0,
            opacity: isHighlighting ? 0.9 : isDetached ? 0.85 : 0,
            scale:   isFading ? 0.75 : isDetached ? 1 : 0.9,
          }}
          transition={{ ...SPRING_SOFT, delay: isDetached ? i * 0.09 : 0 }}
        >
          <div
            className="flex items-center gap-2 px-3 py-1.5 bg-white/90 backdrop-blur-sm rounded-md text-[11.5px] font-medium text-[var(--color-ink)]/78"
            style={{
              boxShadow:
                "0 6px 24px -6px rgba(0,0,0,0.08), 0 1px 4px rgba(0,0,0,0.04)",
              border: "1px solid rgba(0,0,0,0.055)",
            }}
          >
            {entity.text}
            <span
              className="text-[8.5px] font-mono uppercase tracking-[0.12em]"
              style={{ color: "var(--color-intelligence)", opacity: 0.65 }}
            >
              {entity.label}
            </span>
          </div>

          {/* Orbit pulse */}
          {isFloating && (
            <motion.div
              className="absolute -inset-2 rounded-xl pointer-events-none"
              style={{ border: "1px solid rgba(67,56,202,0.12)" }}
              animate={{ scale: [1, 1.18, 1], opacity: [0, 0.5, 0] }}
              transition={{ duration: 3.5, repeat: Infinity, delay: i * 0.55 }}
            />
          )}
        </motion.div>
      ))}
    </section>
  );
}

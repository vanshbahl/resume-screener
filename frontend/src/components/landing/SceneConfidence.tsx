import {
  motion,
  useMotionValue,
  useSpring,
  useTransform,
  AnimatePresence,
} from "framer-motion";
import { useRef, useState, useCallback } from "react";
import { useGlobalDrag } from "./DragContext";

/*
 * Scene Three — "Confidence"
 *
 * Radical simplicity. One headline. One interaction.
 * The upload zone is the emotional destination.
 * The ENTIRE page reacts when a file is dragged in.
 */

// ─── Ambient particle dots ────────────────────────────────────────────
// Pre-seeded so they feel organic, not random-on-each-render
const PARTICLES = [
  { id: 0, x: "12%",  y: "22%",  size: 2.5, dur: 6.0, del: 0.0 },
  { id: 1, x: "82%",  y: "18%",  size: 1.5, dur: 8.0, del: 1.2 },
  { id: 2, x: "70%",  y: "74%",  size: 2.0, dur: 7.0, del: 0.6 },
  { id: 3, x: "22%",  y: "66%",  size: 1.5, dur: 9.0, del: 2.1 },
  { id: 4, x: "88%",  y: "50%",  size: 2.0, dur: 5.5, del: 0.3 },
  { id: 5, x: "38%",  y: "14%",  size: 1.5, dur: 7.5, del: 1.8 },
  { id: 6, x: "58%",  y: "86%",  size: 2.5, dur: 6.5, del: 0.9 },
  { id: 7, x: "6%",   y: "46%",  size: 1.5, dur: 8.5, del: 2.4 },
  { id: 8, x: "92%",  y: "32%",  size: 2.0, dur: 7.2, del: 0.4 },
  { id: 9, x: "46%",  y: "92%",  size: 1.5, dur: 6.8, del: 1.5 },
  { id: 10, x: "16%", y: "84%",  size: 2.0, dur: 9.2, del: 3.0 },
  { id: 11, x: "76%", y: "10%",  size: 1.5, dur: 5.8, del: 0.7 },
];

export function SceneConfidence() {
  const dropzoneRef  = useRef<HTMLDivElement>(null);
  const [isHovering, setIsHovering] = useState(false);
  const { isGlobalDragActive } = useGlobalDrag();

  // ── Magnetic 3D tilt on dropzone ──────────────────────────────────
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const sx = useSpring(mouseX, { stiffness: 45, damping: 28, mass: 0.8 });
  const sy = useSpring(mouseY, { stiffness: 45, damping: 28, mass: 0.8 });
  const tiltX  = useTransform(sy, [-1, 1], [ 4, -4]);
  const tiltY  = useTransform(sx, [-1, 1], [-4,  4]);
  const shiftX = useTransform(sx, [-1, 1], [-14, 14]);
  const shiftY = useTransform(sy, [-1, 1], [-10, 10]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!dropzoneRef.current) return;
    const { left, top, width, height } = dropzoneRef.current.getBoundingClientRect();
    mouseX.set(((e.clientX - left) / width  - 0.5) * 2);
    mouseY.set(((e.clientY - top)  / height - 0.5) * 2);
  }, [mouseX, mouseY]);

  const handleMouseLeave = useCallback(() => {
    mouseX.set(0);
    mouseY.set(0);
    setIsHovering(false);
  }, [mouseX, mouseY]);

  const isActive = isGlobalDragActive || isHovering;

  return (
    <section
      id="upload"
      className="relative min-h-screen w-full flex flex-col items-center justify-center overflow-hidden"
      style={{
        background: isActive
          ? "hsl(240 14% 4%)"
          : "#000",
        transition: "background 1.2s ease",
      }}
    >
      {/* ── Subtle grain ── */}
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.022] mix-blend-screen"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
        }}
      />

      {/* ── Ambient particles — drift toward center on drag ── */}
      {PARTICLES.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full pointer-events-none"
          style={{
            left: p.x,
            top:  p.y,
            width:  p.size,
            height: p.size,
            background: isActive
              ? "rgba(129,140,248,0.55)"
              : "rgba(255,255,255,0.18)",
          }}
          animate={
            isActive
              ? {
                  left: "50%",
                  top:  "50%",
                  x:    `${(Math.random() - 0.5) * 80}px`,
                  y:    `${(Math.random() - 0.5) * 80}px`,
                  opacity: [0, 0.7, 0],
                  scale:   [0.5, 1.2, 0.5],
                }
              : {
                  opacity: [0, 0.45, 0],
                  scale:   [0.8, 1.1, 0.8],
                  y:       [0, -8, 0],
                }
          }
          transition={{
            duration: isActive ? p.dur * 0.6 : p.dur,
            repeat:   Infinity,
            delay:    p.del,
            ease:     "easeInOut",
          }}
        />
      ))}

      {/* ── Ambient glow bloom ── */}
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full pointer-events-none"
        animate={{
          width:   isActive ? 1100 : 500,
          height:  isActive ? 1100 : 500,
          opacity: isActive ? 0.18  : 0.05,
        }}
        transition={{ type: "spring", stiffness: 28, damping: 20 }}
        style={{
          background:
            "radial-gradient(circle, rgba(67,56,202,0.45), transparent 70%)",
          filter: "blur(80px)",
        }}
      />

      {/* ── Headline ── */}
      <motion.div
        className="relative z-10 text-center px-6 max-w-3xl mb-16"
        initial={{ opacity: 0, y: 32 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 1.6, ease: [0.16, 1, 0.3, 1] }}
        animate={{ opacity: isActive ? 0.25 : 1 }}
      >
        <h2
          className="text-[clamp(2.2rem,5.5vw,4.8rem)] leading-[1.08] tracking-[-0.03em] mb-5"
          style={{
            fontFamily: "var(--font-serif)",
            color: isActive ? "rgba(255,255,255,0.5)" : "rgba(255,255,255,0.88)",
            transition: "color 1s ease",
          }}
        >
          The next recruiter won't guess.
        </h2>
        <p
          className="text-[clamp(1.1rem,2.2vw,1.6rem)] leading-[1.5] font-light"
          style={{
            fontFamily: "var(--font-serif)",
            color: isActive ? "rgba(255,255,255,0.08)" : "rgba(255,255,255,0.22)",
            transition: "color 1s ease",
          }}
        >
          Neither should you.
        </p>
      </motion.div>

      {/* ── Upload Zone ── */}
      <motion.div
        className="relative z-10 w-full max-w-lg px-6"
        initial={{ opacity: 0, y: 40 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-60px" }}
        transition={{ duration: 1.6, ease: [0.16, 1, 0.3, 1], delay: 0.18 }}
        animate={{
          scale: isActive ? 1.03 : 1,
        }}
      >
        {/* 3D perspective wrapper */}
        <div style={{ perspective: "1000px" }}>
          <motion.div
            ref={dropzoneRef}
            onMouseMove={handleMouseMove}
            onMouseEnter={() => setIsHovering(true)}
            onMouseLeave={handleMouseLeave}
            style={{
              rotateX: tiltX,
              rotateY: tiltY,
              x: shiftX,
              y: shiftY,
              height: isActive ? "320px" : "280px",
              transition: "height 0.8s cubic-bezier(0.16,1,0.3,1)",
            }}
            className="relative w-full rounded-2xl flex flex-col items-center justify-center cursor-pointer"
          >
            {/* SVG border — precision-drawn, dashed when idle */}
            <svg
              className="absolute inset-0 w-full h-full pointer-events-none"
              style={{ borderRadius: "16px" }}
            >
              <rect
                x="1.5" y="1.5"
                width="calc(100% - 3px)"
                height="calc(100% - 3px)"
                rx="14.5"
                fill="none"
                stroke={isActive ? "rgba(129,140,248,0.55)" : "rgba(255,255,255,0.1)"}
                strokeWidth={isActive ? 1.5 : 1}
                strokeDasharray={isActive ? "0" : "5 8"}
                style={{ transition: "stroke 0.9s ease, stroke-width 0.5s ease, stroke-dasharray 0.9s ease" }}
              />
            </svg>

            {/* Background fill */}
            <motion.div
              className="absolute inset-0 rounded-2xl pointer-events-none"
              animate={{
                backgroundColor: isActive
                  ? "rgba(67,56,202,0.07)"
                  : "rgba(255,255,255,0.015)",
              }}
              transition={{ duration: 0.8, ease: "easeOut" }}
            />

            {/* Content */}
            <div className="relative z-10 flex flex-col items-center gap-5">
              {/* Upload icon */}
              <motion.div
                animate={{
                  scale: isActive ? 1.12 : 1,
                  y:     isActive ? -6   : 0,
                }}
                transition={{ type: "spring", stiffness: 160, damping: 14 }}
              >
                <svg
                  width="38" height="38"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke={isActive ? "rgba(129,140,248,0.85)" : "rgba(255,255,255,0.28)"}
                  strokeWidth="1.4"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  style={{ transition: "stroke 0.7s ease" }}
                >
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </motion.div>

              {/* Label */}
              <div className="text-center">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={isGlobalDragActive ? "drag" : "idle"}
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -5 }}
                    transition={{ duration: 0.4 }}
                    className="text-[15px] font-medium mb-1.5"
                    style={{
                      fontFamily: "var(--font-serif)",
                      color: isActive
                        ? "rgba(255,255,255,0.92)"
                        : "rgba(255,255,255,0.42)",
                    }}
                  >
                    {isGlobalDragActive ? "Release to begin" : "Drop your resume here"}
                  </motion.div>
                </AnimatePresence>
                <div
                  className="text-[10px] font-mono uppercase tracking-[0.16em]"
                  style={{
                    color: isActive
                      ? "rgba(129,140,248,0.5)"
                      : "rgba(255,255,255,0.18)",
                    transition: "color 0.8s ease",
                  }}
                >
                  PDF or DOCX — up to 10 MB
                </div>
              </div>
            </div>

            {/* Breathing pulse ring — idle only */}
            {!isActive && (
              <motion.div
                className="absolute inset-0 rounded-2xl pointer-events-none"
                style={{ border: "1px solid rgba(255,255,255,0.04)" }}
                animate={{ scale: [1, 1.04, 1], opacity: [0, 0.5, 0] }}
                transition={{ duration: 4.5, repeat: Infinity, ease: "easeInOut" }}
              />
            )}
          </motion.div>
        </div>
      </motion.div>

      {/* ── Footer ── */}
      <div className="absolute bottom-6 left-0 right-0 flex justify-center z-10">
        <div
          className="flex items-center gap-6 text-[10px] font-mono uppercase tracking-[0.16em]"
          style={{ color: "rgba(255,255,255,0.12)" }}
        >
          <span>Resume Intelligence</span>
          <span>·</span>
          <span>© {new Date().getFullYear()}</span>
        </div>
      </div>
    </section>
  );
}

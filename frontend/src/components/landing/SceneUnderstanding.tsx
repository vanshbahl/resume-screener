import { motion, useScroll, useTransform } from "framer-motion";
import { useRef, useState, useCallback } from "react";

import { useGlobalDrag } from "./DragContext";

/*
 * Scene Two — "Understanding"
 *
 * The resume is gone. Only intelligence remains.
 * A living knowledge graph breathes in the dark.
 * Hovering reveals relationships.
 * One massive sentence. Nothing else.
 */

// ─── Graph Topology ──────────────────────────────────────────────────
interface GraphNode {
  id: string;
  label: string;
  type: "primary" | "secondary";
  x: number;
  y: number;
  description: string;
}

interface GraphEdge {
  from: string;
  to: string;
}

const NODES: GraphNode[] = [
  { id: "candidate", label: "J. Chen",          type: "primary",   x: 0,    y: 0,     description: "Candidate Profile" },
  { id: "role",      label: "Staff Engineer",    type: "primary",   x: -220, y: -130,  description: "Current Position" },
  { id: "skills",    label: "Python · React",    type: "primary",   x: 240,  y: -90,   description: "Core Competencies" },
  { id: "tenure",    label: "5+ Years",          type: "secondary", x: -160, y: 130,   description: "Professional Tenure" },
  { id: "impact",    label: "Event-Driven Arch", type: "secondary", x: 180,  y: 150,   description: "Key Achievement" },
  { id: "education", label: "UC Berkeley",       type: "secondary", x: -50,  y: 200,   description: "Academic Background" },
  { id: "domain",    label: "Distributed Systems", type: "secondary", x: 280, y: 30,  description: "Domain Expertise" },
  { id: "growth",    label: "Senior → Staff",    type: "secondary", x: -280, y: 10,    description: "Career Trajectory" },
];

const EDGES: GraphEdge[] = [
  { from: "candidate", to: "role" },
  { from: "candidate", to: "skills" },
  { from: "candidate", to: "tenure" },
  { from: "candidate", to: "impact" },
  { from: "candidate", to: "education" },
  { from: "role", to: "domain" },
  { from: "skills", to: "domain" },
  { from: "role", to: "growth" },
  { from: "tenure", to: "growth" },
  { from: "impact", to: "skills" },
];

// Center of the SVG viewBox
const CX = 400;
const CY = 280;

export function SceneUnderstanding() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });

  const { isGlobalDragActive } = useGlobalDrag();

  // Parallax and cinematic background dissolve
  const backgroundOpacity = useTransform(scrollYProgress, [0, 0.4], [0, 1]);
  // Use a much finer grain for microscopic dots that become denser
  const particleOpacity = useTransform(scrollYProgress, [0.1, 0.5], [0, 0.6]);
  const headlineY = useTransform(scrollYProgress, [0, 1], [80, -80]);
  const headlineOpacity = useTransform(scrollYProgress, [0, 0.25, 0.75, 1], [0, 1, 1, 0]);

  // Hovered node
  const [hovered, setHovered] = useState<string | null>(null);

  const getNode = useCallback((id: string) => NODES.find((n) => n.id === id), []);

  const isConnected = useCallback(
    (nodeId: string) => {
      if (!hovered) return false;
      return EDGES.some(
        (e) =>
          (e.from === hovered && e.to === nodeId) ||
          (e.to === hovered && e.from === nodeId) ||
          nodeId === hovered
      );
    },
    [hovered]
  );

  return (
    <section
      ref={containerRef}
      className="relative min-h-screen w-full flex flex-col items-center justify-center overflow-hidden"
    >
      {/* Cinematic Black Overlay dissolving over the previous white section */}
      <motion.div 
        className="absolute inset-0 z-0 bg-black pointer-events-none"
        style={{ opacity: backgroundOpacity }} 
      />

      {/* Point-cloud particle emergence (microscopic dots, high frequency) */}
      <motion.div 
        className="absolute inset-0 z-0 pointer-events-none mix-blend-screen"
        style={{ 
          opacity: particleOpacity,
          backgroundImage: "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 600 600' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='2.5' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.4'/%3E%3C/svg%3E\")"
        }}
      />

      {/* Headline */}
      <motion.div
        className="absolute top-[10vh] left-0 right-0 text-center z-20 px-6 pointer-events-none"
        style={{ y: headlineY, opacity: headlineOpacity }}
        animate={{ opacity: isGlobalDragActive ? 0.1 : 1 }}
        transition={{ duration: 1 }}
      >
        <h2
          className="text-[clamp(2.5rem,6vw,5.5rem)] leading-[1.1] tracking-[-0.03em]"
          style={{ fontFamily: "var(--font-serif)", color: "rgba(255,255,255,0.85)" }}
        >
          We don't read résumés.<br />
          <span className="italic" style={{ color: "rgba(255,255,255,0.3)" }}>
            We understand careers.
          </span>
        </h2>
      </motion.div>

      {/* Knowledge Graph */}
      <motion.div 
        className="relative z-10 w-full max-w-4xl h-[560px] flex items-center justify-center mt-16"
        animate={{
          scale: isGlobalDragActive ? 0.9 : 1,
          y: isGlobalDragActive ? 60 : 0,
        }}
        transition={{ type: "spring", stiffness: 40, damping: 25 }}
      >
        <svg
          viewBox="0 0 800 560"
          className="w-full h-full"
          style={{ overflow: "visible" }}
        >
          {/* Edges */}
          {EDGES.map((edge, i) => {
            const from = getNode(edge.from);
            const to = getNode(edge.to);
            if (!from || !to) return null;

            const highlighted = hovered && (isConnected(from.id) && isConnected(to.id));
            const midX = (from.x + to.x) / 2 + CX;
            const midY = (from.y + to.y) / 2 + CY + (i % 2 === 0 ? -20 : 20);

            return (
              <motion.path
                key={`${edge.from}-${edge.to}`}
                d={`M ${CX + from.x} ${CY + from.y} Q ${midX} ${midY} ${CX + to.x} ${CY + to.y}`}
                fill="none"
                stroke={highlighted ? "rgba(129,140,248,0.5)" : "rgba(255,255,255,0.06)"}
                strokeWidth={highlighted ? 2 : 1}
                strokeLinecap="round"
                initial={{ pathLength: 0 }}
                whileInView={{ pathLength: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 1.8, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] }}
                style={{ transition: "stroke 0.5s ease, stroke-width 0.5s ease" }}
              />
            );
          })}

          {/* Nodes */}
          {NODES.map((node, i) => {
            const isPrimary = node.type === "primary";
            const isHovered = hovered === node.id;
            const connected = isConnected(node.id);
            const dimmed = hovered !== null && !connected;

            const r = isPrimary ? 6 : 4;

            return (
              <g
                key={node.id}
                onMouseEnter={() => setHovered(node.id)}
                onMouseLeave={() => setHovered(null)}
                style={{ cursor: "pointer" }}
              >
                {/* Pulse ring for primary nodes */}
                {isPrimary && (
                  <motion.circle
                    cx={CX + node.x}
                    cy={CY + node.y}
                    r={r + 12}
                    fill="none"
                    stroke="rgba(129,140,248,0.15)"
                    strokeWidth={1}
                    animate={{ r: [r + 12, r + 20, r + 12], opacity: [0, 0.4, 0] }}
                    transition={{ duration: 4, repeat: Infinity, delay: i * 0.7 }}
                  />
                )}

                {/* Node dot */}
                <motion.circle
                  cx={CX + node.x}
                  cy={CY + node.y}
                  r={isHovered ? r + 3 : r}
                  fill={isHovered ? "#818cf8" : isPrimary ? "rgba(255,255,255,0.8)" : "rgba(255,255,255,0.3)"}
                  style={{
                    transition: "fill 0.3s ease, r 0.3s ease",
                    opacity: dimmed ? 0.15 : 1,
                    filter: isHovered ? "drop-shadow(0 0 8px rgba(129,140,248,0.5))" : "none",
                  }}
                  initial={{ scale: 0 }}
                  whileInView={{ scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ type: "spring" as const, stiffness: 200, damping: 15, delay: 0.5 + i * 0.08 }}
                />

                {/* Label */}
                <motion.text
                  x={CX + node.x}
                  y={CY + node.y + (isPrimary ? -18 : -14)}
                  textAnchor="middle"
                  fill={dimmed ? "rgba(255,255,255,0.08)" : "rgba(255,255,255,0.5)"}
                  fontSize={isPrimary ? 12 : 10}
                  fontFamily="var(--font-mono)"
                  letterSpacing="0.05em"
                  style={{ transition: "fill 0.4s ease", textTransform: "uppercase" }}
                >
                  {node.label}
                </motion.text>

                {/* Hover description */}
                {isHovered && (
                  <motion.text
                    x={CX + node.x}
                    y={CY + node.y + (isPrimary ? 24 : 20)}
                    textAnchor="middle"
                    fill="rgba(129,140,248,0.8)"
                    fontSize={10}
                    fontFamily="var(--font-sans)"
                    initial={{ opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {node.description}
                  </motion.text>
                )}
              </g>
            );
          })}
        </svg>
      </motion.div>
    </section>
  );
}

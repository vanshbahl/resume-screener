import { motion, useScroll, useMotionValueEvent } from "framer-motion";
import { useState } from "react";

/*
 * Navigation — near-invisible.
 * Logo on the left. A single "Upload" link on the right.
 * No nav links. The page is too short to need them.
 */

export function Navigation() {
  const { scrollY } = useScroll();
  const [scrolled, setScrolled] = useState(false);

  useMotionValueEvent(scrollY, "change", (latest) => {
    setScrolled(latest > 60);
  });

  return (
    <motion.header
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1.2, delay: 0.8, ease: [0.16, 1, 0.3, 1] }}
      className="fixed top-0 left-0 right-0 z-50 flex justify-center px-6 py-6"
    >
      <div className="flex items-center justify-between w-full max-w-5xl">
        {/* Logo */}
        <div className="flex items-center gap-2.5">
          <div
            className="w-6 h-6 rounded-md flex items-center justify-center"
            style={{ background: "var(--color-intelligence)" }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
          </div>
          <span
            className="text-sm font-medium tracking-tight"
            style={{
              color: scrolled ? "rgba(255,255,255,0.8)" : "var(--color-ink)",
              transition: "color 0.6s ease",
            }}
          >
            Resume Intelligence
          </span>
        </div>

        {/* Single CTA */}
        <a
          href="#upload"
          className="text-xs font-mono uppercase tracking-[0.15em] pb-0.5"
          style={{
            color: scrolled ? "rgba(255,255,255,0.4)" : "rgba(0,0,0,0.35)",
            borderBottom: `1px solid ${scrolled ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)"}`,
            transition: "color 0.6s ease, border-color 0.6s ease",
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = scrolled ? "rgba(255,255,255,0.8)" : "var(--color-ink)";
            e.currentTarget.style.borderColor = scrolled ? "rgba(255,255,255,0.4)" : "var(--color-ink)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = scrolled ? "rgba(255,255,255,0.4)" : "rgba(0,0,0,0.35)";
            e.currentTarget.style.borderColor = scrolled ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.1)";
          }}
        >
          Upload
        </a>
      </div>
    </motion.header>
  );
}

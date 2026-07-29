import { useState } from "react";
import { Navigation } from "./components/landing/Navigation";
import { SceneChaos } from "./components/landing/SceneChaos";
import { SceneUnderstanding } from "./components/landing/SceneUnderstanding";
import { SceneConfidence } from "./components/landing/SceneConfidence";
import { DragProvider } from "./components/landing/DragContext";
import { ValidationSuite } from "./components/validation/ValidationSuite";

function App() {
  const [view, setView] = useState<"landing" | "validate">("validate");

  return (
    <div className="min-h-screen bg-slate-950">
      {/* View Switcher Header Bar */}
      <div className="bg-slate-900 border-b border-slate-800 px-6 py-2 flex items-center justify-between text-xs text-slate-400 z-50 relative font-mono">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Resume Intelligence Engine</span>
        </div>
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setView("landing")}
            className={`px-3 py-1 rounded transition-all font-sans text-xs font-medium ${
              view === "landing"
                ? "bg-slate-800 text-white font-semibold shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Landing Page
          </button>
          <button
            onClick={() => setView("validate")}
            className={`px-3 py-1 rounded transition-all font-sans text-xs font-medium ${
              view === "validate"
                ? "bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/30"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            Pipeline Validation Suite
          </button>
        </div>
      </div>

      {view === "landing" ? (
        <DragProvider>
          <Navigation />
          <main>
            <SceneChaos />
            <SceneUnderstanding />
            <SceneConfidence />
          </main>
        </DragProvider>
      ) : (
        <ValidationSuite />
      )}
    </div>
  );
}

export default App;

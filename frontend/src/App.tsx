import { Navigation } from "./components/landing/Navigation";
import { HeroExperience } from "./components/landing/HeroExperience";
import { TransformationStory } from "./components/landing/TransformationStory";
import { HowItWorks } from "./components/landing/HowItWorks";
import { InteractiveDemo } from "./components/landing/InteractiveDemo";
import { WhyItMatters } from "./components/landing/WhyItMatters";
import { FinalUploadCTA } from "./components/landing/FinalUploadCTA";
import { Footer } from "./components/landing/Footer";

function App() {
  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 selection:bg-indigo-200 selection:text-indigo-900">
      <Navigation />
      <main>
        <HeroExperience />
        <TransformationStory />
        <HowItWorks />
        <InteractiveDemo />
        <WhyItMatters />
        <FinalUploadCTA />
      </main>
      <Footer />
    </div>
  );
}

export default App;

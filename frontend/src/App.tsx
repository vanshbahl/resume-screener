import { Navigation } from "./components/landing/Navigation";
import { SceneChaos } from "./components/landing/SceneChaos";
import { SceneUnderstanding } from "./components/landing/SceneUnderstanding";
import { SceneConfidence } from "./components/landing/SceneConfidence";
import { DragProvider } from "./components/landing/DragContext";

function App() {
  return (
    <DragProvider>
      <Navigation />
      <main>
        <SceneChaos />
        <SceneUnderstanding />
        <SceneConfidence />
      </main>
    </DragProvider>
  );
}

export default App;

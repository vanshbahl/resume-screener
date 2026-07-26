import { createContext, useContext, useState, useEffect } from "react";
import type { ReactNode } from "react";

interface DragContextType {
  isGlobalDragActive: boolean;
}

const DragContext = createContext<DragContextType>({ isGlobalDragActive: false });

export const useGlobalDrag = () => useContext(DragContext);

export function DragProvider({ children }: { children: ReactNode }) {
  const [isGlobalDragActive, setIsGlobalDragActive] = useState(false);

  useEffect(() => {
    let dragCounter = 0;

    const handleDragEnter = (e: DragEvent) => {
      e.preventDefault();
      dragCounter++;
      if (dragCounter === 1) {
        setIsGlobalDragActive(true);
      }
    };

    const handleDragLeave = (e: DragEvent) => {
      e.preventDefault();
      dragCounter--;
      if (dragCounter === 0) {
        setIsGlobalDragActive(false);
      }
    };

    const handleDragOver = (e: DragEvent) => {
      e.preventDefault();
    };

    const handleDrop = (e: DragEvent) => {
      e.preventDefault();
      dragCounter = 0;
      setIsGlobalDragActive(false);
    };

    window.addEventListener("dragenter", handleDragEnter);
    window.addEventListener("dragleave", handleDragLeave);
    window.addEventListener("dragover", handleDragOver);
    window.addEventListener("drop", handleDrop);

    return () => {
      window.removeEventListener("dragenter", handleDragEnter);
      window.removeEventListener("dragleave", handleDragLeave);
      window.removeEventListener("dragover", handleDragOver);
      window.removeEventListener("drop", handleDrop);
    };
  }, []);

  return (
    <DragContext.Provider value={{ isGlobalDragActive }}>
      {children}
    </DragContext.Provider>
  );
}

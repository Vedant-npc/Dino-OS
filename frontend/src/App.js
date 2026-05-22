import React, { useState, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import InitScreen from './components/InitScreen';
import MainDashboard from './components/MainDashboard';
import './App.css';

function App() {
  const [isInitialized, setIsInitialized] = useState(false);
  const [systemInfo, setSystemInfo] = useState(null);

  useEffect(() => {
    // Initialize system info and perform startup sequence
    const initializeApp = async () => {
      try {
        if (window.electron) {
          const info = await window.electron.getSystemInfo();
          setSystemInfo(info);
        }
        
        // Simulate initialization sequence
        setTimeout(() => {
          setIsInitialized(true);
        }, 3000);
      } catch (error) {
        console.error('Initialization error:', error);
        // Continue anyway
        setTimeout(() => {
          setIsInitialized(true);
        }, 3000);
      }
    };

    initializeApp();
  }, []);

  return (
    <div className="w-screen h-screen bg-[#020712] overflow-hidden">
      <AnimatePresence mode="wait">
        {!isInitialized ? (
          <InitScreen key="init" onComplete={() => setIsInitialized(true)} />
        ) : (
          <MainDashboard key="dashboard" systemInfo={systemInfo} />
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;

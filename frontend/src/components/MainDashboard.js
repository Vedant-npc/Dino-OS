import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bot,
  CheckCircle2,
  Command,
  Crosshair,
  MessageCircle,
  Mic,
  Radar,
  Wifi,
} from 'lucide-react';
import VoiceAssistant from './VoiceAssistant';
import CommandConsole from './CommandConsole';
import HolographicWidgets from './HolographicWidgets';
import ChatInterface from './ChatInterface';
import FloatingWindow from './FloatingWindow';
import './MainDashboard.css';

const MainDashboard = ({ systemInfo }) => {
  const [activeWindows, setActiveWindows] = useState([]);
  const [voiceActive, setVoiceActive] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);
  const [consoleToggle, setConsoleToggle] = useState(0);
  const [systemMetrics, setSystemMetrics] = useState({
    cpu: 35,
    ram: 52,
    temp: 65,
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setSystemMetrics({
        cpu: Math.floor(Math.random() * 80) + 10,
        ram: Math.floor(Math.random() * 70) + 30,
        temp: Math.floor(Math.random() * 30) + 50,
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const toggleVoice = () => setVoiceActive((current) => !current);
    const toggleConsole = () => setConsoleToggle((current) => current + 1);

    if (window.electron) {
      window.electron.onToggleVoiceAssistant(toggleVoice);
      window.electron.onToggleCommandConsole(toggleConsole);
    }

    window.addEventListener('dino-toggle-voice', toggleVoice);
    window.addEventListener('dino-toggle-console', toggleConsole);

    const handleLocalShortcut = (event) => {
      if (event.key === 'F8' || (event.ctrlKey && event.shiftKey && event.key.toLowerCase() === 'v')) {
        event.preventDefault();
        toggleVoice();
      }
      if (event.ctrlKey && event.shiftKey && event.key.toLowerCase() === 'c') {
        event.preventDefault();
        toggleConsole();
      }
    };

    window.addEventListener('keydown', handleLocalShortcut);
    return () => {
      window.removeEventListener('dino-toggle-voice', toggleVoice);
      window.removeEventListener('dino-toggle-console', toggleConsole);
      window.removeEventListener('keydown', handleLocalShortcut);
    };
  }, []);

  const handleAddWindow = (windowData) => {
    const newWindow = {
      id: Date.now(),
      ...windowData,
      position: { x: Math.random() * 400, y: Math.random() * 300 },
    };
    setActiveWindows([...activeWindows, newWindow]);
  };

  const handleCloseWindow = (windowId) => {
    setActiveWindows(activeWindows.filter((w) => w.id !== windowId));
  };

  return (
    <motion.div
      className="dino-shell relative h-screen w-screen overflow-hidden"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="dino-wallpaper" />

      <motion.div
        className="dashboard-topbar"
        initial={{ y: -80 }}
        animate={{ y: 0 }}
        transition={{ delay: 0.3, duration: 0.6 }}
      >
        <div className="brand-lockup">
          <div className="brand-mark">
            <Radar size={21} />
          </div>
          <div>
            <h1>DINO ARC</h1>
            <p>Neural command interface</p>
          </div>
        </div>

        <div className="topbar-status">
          <div className="status-pill">
            <Wifi size={16} />
            <span>Online</span>
          </div>
          <div className={`status-pill ${isListening ? 'is-active' : ''}`}>
            <Mic size={16} />
            <span>{isListening ? 'Listening' : 'Ready'}</span>
          </div>
          <div className="time-pill" id="time">
            --:-- AM
          </div>
        </div>
      </motion.div>

      <main className="dashboard-content">
        <section className="hero-panel">
          <div className="arc-reactor" aria-hidden="true">
            <div className="arc-ring arc-ring-one" />
            <div className="arc-ring arc-ring-two" />
            <div className="arc-core">
              <Crosshair size={42} />
            </div>
          </div>
          <div>
            <p className="eyebrow">Arc intelligence online</p>
            <h2>Systems ready, Vedant.</h2>
            <p className="hero-copy">
              Voice, chat, apps, files, searches, and system actions are routed through a live command core.
            </p>
          </div>
          <div className="hero-actions">
            <button className="primary-action" onClick={() => setVoiceActive(true)}>
              <Mic size={18} />
              Voice
            </button>
            <button className="secondary-action" onClick={() => setChatOpen(true)}>
              <MessageCircle size={18} />
              Chat
            </button>
            <button className="secondary-action" onClick={() => setConsoleToggle((current) => current + 1)}>
              <Command size={18} />
              Console
            </button>
          </div>
        </section>

        <HolographicWidgets systemMetrics={systemMetrics} />

        <section className="quick-strip">
          <div className="quick-item">
            <CheckCircle2 size={18} />
            <span>Targeting layer calibrated</span>
          </div>
          <div className="quick-item">
            <Bot size={18} />
            <span>Reasoning core online</span>
          </div>
          <div className="quick-item">
            <Mic size={18} />
            <span>Voice uplink {isListening ? 'active' : 'standing by'}</span>
          </div>
        </section>

        <motion.button
          className={`floating-action voice-action ${voiceActive ? 'is-active' : ''}`}
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setVoiceActive(!voiceActive)}
          aria-label="Toggle voice assistant"
        >
          <Mic size={24} />
        </motion.button>

        <motion.button
          className={`floating-action chat-action ${chatOpen ? 'is-active' : ''}`}
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setChatOpen(!chatOpen)}
          aria-label="Toggle chat"
        >
          <MessageCircle size={22} />
        </motion.button>
      </main>

      <AnimatePresence>
        {voiceActive && (
          <VoiceAssistant
            isListening={isListening}
            setIsListening={setIsListening}
            onCommand={(response) => {
              const execution = response?.execution || response;
              const parsedCommand = response?.parsed_command || execution?.command || 'voice command';
              handleAddWindow({
                title: execution?.success ? 'Command Executed' : 'Command Error',
                content: execution?.message || response?.error || `Could not execute: ${parsedCommand}`,
              });
            }}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {chatOpen && (
          <ChatInterface
            onClose={() => setChatOpen(false)}
            onWindowOpen={handleAddWindow}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {activeWindows.map((window) => (
          <FloatingWindow
            key={window.id}
            id={window.id}
            title={window.title}
            content={window.content}
            onClose={handleCloseWindow}
          />
        ))}
      </AnimatePresence>

      <CommandConsole onWindowOpen={handleAddWindow} toggleSignal={consoleToggle} />
      <UpdateClock />
    </motion.div>
  );
};

const UpdateClock = () => {
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const timeEl = document.getElementById('time');
      if (timeEl) {
        timeEl.textContent = now.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        });
      }
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return null;
};

export default MainDashboard;

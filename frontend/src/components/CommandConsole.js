import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Command, Terminal, X } from 'lucide-react';
import './CommandConsole.css';

const CommandConsole = ({ onWindowOpen, toggleSignal }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [history, setHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const inputRef = useRef(null);

  const commands = {
    help: 'Available commands: open, search, screenshot, folder, lock, coding, project, run, info, time, clear',
    time: new Date().toLocaleString(),
    info: 'DINO OS v1.0 - AI desktop assistant',
    clear: 'console_clear',
    open: 'Usage: open <application>',
    search: 'Usage: search <query>',
    screenshot: 'Screenshot taken and saved',
    run: 'Usage: run <shell command> (requires ENABLE_SHELL_COMMANDS=True)',
  };

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    if (toggleSignal > 0) {
      setIsOpen((current) => !current);
      setInput('');
      setHistoryIndex(-1);
    }
  }, [toggleSignal]);

  const handleKeyDown = (e) => {
    if (e.key === '`' && e.ctrlKey) {
      setIsOpen(!isOpen);
      setInput('');
      setHistoryIndex(-1);
    } else if (e.key === 'ArrowUp' && isOpen) {
      e.preventDefault();
      if (historyIndex < history.length - 1) {
        const newIndex = historyIndex + 1;
        setHistoryIndex(newIndex);
        setInput(history[history.length - 1 - newIndex]);
      }
    } else if (e.key === 'ArrowDown' && isOpen) {
      e.preventDefault();
      if (historyIndex > 0) {
        const newIndex = historyIndex - 1;
        setHistoryIndex(newIndex);
        setInput(history[history.length - 1 - newIndex]);
      } else if (historyIndex === 0) {
        setHistoryIndex(-1);
        setInput('');
      }
    }
  };

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, historyIndex, history]);

  const executeCommand = async (cmd) => {
    const trimmedCmd = cmd.trim().toLowerCase();

    if (!trimmedCmd) return;

    setHistory([...history, trimmedCmd]);
    setHistoryIndex(-1);

    if (trimmedCmd === 'console_clear' || trimmedCmd === 'clear') {
      setHistory([]);
      setInput('');
      return;
    }

    const [mainCmd, ...args] = trimmedCmd.split(' ');

    if (mainCmd === 'open') {
      const app = args.join(' ');
      if (app) executeSystemCommand('open', app);
    } else if (mainCmd === 'search') {
      const query = args.join(' ');
      if (query) executeSystemCommand('search', query);
    } else if (mainCmd === 'screenshot') {
      executeSystemCommand('screenshot');
    } else if (mainCmd === 'folder' || mainCmd === 'mkdir') {
      const folderName = args.join(' ');
      if (folderName) executeSystemCommand('create-folder', folderName);
    } else if (mainCmd === 'lock') {
      executeSystemCommand('lock');
    } else if (mainCmd === 'coding') {
      executeSystemCommand('coding-mode');
    } else if (mainCmd === 'project') {
      executeSystemCommand('open-project');
    } else if (mainCmd === 'run') {
      const shellCommand = args.join(' ');
      if (shellCommand) executeSystemCommand('run-shell', shellCommand);
    } else if (mainCmd === 'info' || mainCmd === 'time' || mainCmd === 'help') {
      onWindowOpen({
        title: mainCmd.toUpperCase(),
        content: commands[mainCmd],
      });
    } else if (commands[mainCmd]) {
      onWindowOpen({
        title: mainCmd.toUpperCase(),
        content: commands[mainCmd],
      });
    } else {
      onWindowOpen({
        title: 'Command Not Found',
        content: `Unknown command: ${mainCmd}\nType 'help' for available commands`,
      });
    }

    setInput('');
  };

  const executeSystemCommand = async (cmd, arg = null) => {
    try {
      if (window.api) {
        const response = await window.api.callBackend('/execute', 'POST', {
          command: cmd,
          argument: arg,
        });

        onWindowOpen({
          title: response.success ? 'Command Executed' : 'Command Error',
          content: response.success
            ? `${cmd}${arg ? ` ${arg}` : ''} - ${response.message || 'Success'}`
            : response.error || response.message || 'Failed to execute command',
        });
      }
    } catch (error) {
      onWindowOpen({
        title: 'Command Error',
        content: error.message,
      });
    }
  };

  return (
    <>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="console-backdrop"
            initial={{ opacity: 0, y: -24 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -24 }}
            transition={{ duration: 0.12, ease: 'easeOut' }}
          >
            <div className="console-panel">
              <div className="console-header">
                <div>
                  <Terminal size={18} />
                  <h2>Command Console</h2>
                </div>
                <button onClick={() => setIsOpen(false)} aria-label="Close console">
                  <X size={18} />
                </button>
              </div>

              <div className="console-history">
                {history.length === 0 ? (
                  <p className="console-empty">Ready for commands.</p>
                ) : (
                  history.map((cmd, idx) => (
                    <p key={idx}>
                      <span>$</span> {cmd}
                    </p>
                  ))
                )}
              </div>

              <div className="console-input-row">
                <Command size={18} />
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      executeCommand(input);
                    }
                  }}
                  placeholder="open spotify"
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        className="console-toggle"
        onClick={() => setIsOpen(!isOpen)}
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.95 }}
      >
        <Terminal size={17} />
        Console
      </motion.button>
    </>
  );
};

export default CommandConsole;

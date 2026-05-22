import React, { useCallback, useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { Mic, X } from 'lucide-react';
import './VoiceAssistant.css';

const VoiceAssistant = ({ isListening, setIsListening, onCommand }) => {
  const isProcessingRef = useRef(false);
  const shouldListenRef = useRef(true);
  const backendListenRef = useRef(false);
  const retryTimerRef = useRef(null);
  const [transcript, setTranscript] = useState('');
  const [statusMessage, setStatusMessage] = useState('Initializing voice uplink...');
  const [commandResult, setCommandResult] = useState('');

  const callBackend = useCallback(async (endpoint, method = 'GET', data = null) => {
    if (window.api?.callBackend) {
      return window.api.callBackend(endpoint, method, data);
    }

    const options = {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(`http://127.0.0.1:8000${endpoint}`, options);
    return response.json();
  }, []);

  const startBackendListening = useCallback(async () => {
    if (backendListenRef.current || isProcessingRef.current || !shouldListenRef.current) {
      return;
    }

    backendListenRef.current = true;
    setIsListening(true);
    setStatusMessage('Listening through neural voice uplink...');

    try {
      const response = await callBackend('/listen-command', 'POST', {
        timeout: 6,
        phrase_time_limit: 4,
      });

      const heardText = response?.text || '';
      if (heardText) {
        setTranscript(heardText.toLowerCase());
      }

      const execution = response?.execution || response;
      const message = execution?.message || response?.message || response?.error || 'No command response';
      setCommandResult(message);
      setStatusMessage(heardText ? `Heard: ${heardText}` : message);

      if (response?.success || response?.execution || heardText) {
        onCommand(response);
      }
    } catch (error) {
      setCommandResult(error.message);
      setStatusMessage(error.message);
    } finally {
      backendListenRef.current = false;
      setIsListening(false);
      if (shouldListenRef.current) {
        retryTimerRef.current = window.setTimeout(() => startBackendListening(), 500);
      }
    }
  }, [callBackend, onCommand, setIsListening]);

  useEffect(() => {
    setStatusMessage('Voice uplink calibrated.');
    retryTimerRef.current = window.setTimeout(() => startBackendListening(), 250);

    return () => {
      shouldListenRef.current = false;
      window.clearTimeout(retryTimerRef.current);
    };
  }, [startBackendListening]);

  const stopListening = () => {
    shouldListenRef.current = false;
    window.clearTimeout(retryTimerRef.current);
    backendListenRef.current = false;
    setIsListening(false);
  };

  return (
    <motion.div
      className="voice-backdrop"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.12 }}
    >
      <motion.div
        className="voice-panel"
        initial={{ opacity: 0, y: 24, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 24, scale: 0.96 }}
        transition={{ duration: 0.12, ease: 'easeOut' }}
      >
        <button className="voice-close" onClick={stopListening} aria-label="Close voice assistant">
          <X size={18} />
        </button>

        <div className={`voice-mic ${isListening ? 'is-listening' : ''}`}>
          <Mic size={34} />
        </div>

        <p className="voice-kicker">{isListening ? 'Listening' : 'Voice uplink ready'}</p>
        <h2>{statusMessage}</h2>

        {transcript && (
          <div className="voice-transcript">
            <span>Heard</span>
            <p>{transcript}</p>
          </div>
        )}

        {commandResult && (
          <div className="voice-result">
            <span>Result</span>
            <p>{commandResult}</p>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
};

export default VoiceAssistant;

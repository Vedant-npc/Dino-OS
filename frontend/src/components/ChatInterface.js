import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Bot, Send, X } from 'lucide-react';
import './ChatInterface.css';

const ChatInterface = ({ onClose, onWindowOpen }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: 'Good evening, Vedant. Arc core is online.',
      sender: 'ai',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const currentInput = input;
    const userMessage = {
      id: messages.length + 1,
      text: currentInput,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);
    setInput('');
    setIsLoading(true);

    setTimeout(() => {
      const responses = [
        'Running a quick tactical scan.',
        'I have a clean vector for that.',
        'Analysis complete. Ready for the next command.',
        'I am routing that through the command core.',
      ];

      const aiMessage = {
        id: messages.length + 2,
        text: responses[Math.floor(Math.random() * responses.length)],
        sender: 'ai',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);
      setIsLoading(false);

      if (window.api) {
        window.api.callBackend('/chat', 'POST', { message: currentInput }).catch(console.error);
      }
    }, 1000);
  };

  return (
    <motion.div
      className="chat-panel"
      initial={{ opacity: 0, scale: 0.96, y: 24 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.96, y: 24 }}
      transition={{ duration: 0.12, ease: 'easeOut' }}
    >
      <div className="chat-header">
        <div>
          <span className="chat-avatar">
            <Bot size={18} />
          </span>
          <h3>DINO ARC</h3>
        </div>
        <button onClick={onClose} aria-label="Close chat">
          <X size={18} />
        </button>
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <motion.div
            key={message.id}
            className={`chat-message-row ${message.sender === 'user' ? 'is-user' : ''}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.12, ease: 'easeOut' }}
          >
            <div className="chat-bubble">
              <p>{message.text}</p>
              <span>{message.timestamp.toLocaleTimeString()}</span>
            </div>
          </motion.div>
        ))}

        {isLoading && (
          <motion.div className="chat-message-row" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="chat-bubble is-loading">
              <span />
              <span />
              <span />
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={sendMessage} className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Transmit command"
        />
        <button type="submit" aria-label="Send message">
          <Send size={18} />
        </button>
      </form>
    </motion.div>
  );
};

export default ChatInterface;

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { GripHorizontal, X } from 'lucide-react';
import './FloatingWindow.css';

const FloatingWindow = ({ id, title, content, onClose }) => {
  const [position, setPosition] = useState({
    x: Math.random() * 400,
    y: Math.random() * 300,
  });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStart({
      x: e.clientX - position.x,
      y: e.clientY - position.y,
    });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;

    setPosition({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => setIsDragging(false);

  React.useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);

      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isDragging, dragStart]);

  return (
    <motion.div
      className="floating-window"
      style={{
        left: position.x,
        top: position.y,
        cursor: isDragging ? 'grabbing' : 'default',
      }}
      initial={{ opacity: 0, scale: 0.96, y: 12 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.96, y: 12 }}
      transition={{ duration: 0.12, ease: 'easeOut' }}
    >
      <div className="floating-titlebar" onMouseDown={handleMouseDown}>
        <div>
          <GripHorizontal size={16} />
          <h2>{title}</h2>
        </div>
        <button onClick={() => onClose(id)} aria-label="Close window">
          <X size={18} />
        </button>
      </div>

      <div className="floating-content">
        {typeof content === 'string' ? <p>{content}</p> : content}
      </div>
    </motion.div>
  );
};

export default FloatingWindow;

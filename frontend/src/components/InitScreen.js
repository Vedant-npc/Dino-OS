import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Sparkles } from 'lucide-react';
import './InitScreen.css';

const initSteps = [
  'Igniting arc core',
  'Linking assistant cortex',
  'Calibrating voice uplink',
  'Mapping command protocols',
  'Interface ready',
];

const InitScreen = ({ onComplete }) => {
  const [steps, setSteps] = useState([]);

  useEffect(() => {
    let index = 0;
    let timer;

    const nextStep = () => {
      if (index >= initSteps.length) {
        timer = setTimeout(onComplete, 700);
        return;
      }

      setSteps((prev) => [...prev, initSteps[index]]);
      index += 1;
      timer = setTimeout(nextStep, 360);
    };

    timer = setTimeout(nextStep, 250);
    return () => clearTimeout(timer);
  }, [onComplete]);

  return (
    <motion.div
      className="init-screen"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.35 }}
    >
      <motion.div
        className="init-card"
        initial={{ opacity: 0, y: 18, scale: 0.98 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.45 }}
      >
        <div className="init-logo">
          <Sparkles size={26} />
        </div>
        <h1>DINO ARC</h1>
        <p>Welcome back, Vedant. Systems are coming online.</p>

        <div className="init-steps">
          {steps.map((step, idx) => (
            <motion.div
              key={`${step}-${idx}`}
              className="init-step"
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2 }}
            >
              <CheckCircle2 size={17} />
              <span>{step}</span>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default InitScreen;

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, CalendarDays, Clock3, Cpu, HardDrive, Thermometer, Zap } from 'lucide-react';
import './HolographicWidgets.css';

const HolographicWidgets = ({ systemMetrics }) => {
  const [time, setTime] = useState(new Date());
  const [aiStatus, setAiStatus] = useState('Standby');

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const statuses = ['Standby', 'Scanning', 'Mapping', 'Thinking'];
    const interval = setInterval(() => {
      setAiStatus(statuses[Math.floor(Math.random() * statuses.length)]);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const Widget = ({ title, value, icon: Icon, tone = 'blue' }) => (
    <motion.div
      className={`metric-card metric-card-${tone}`}
      whileHover={{ y: -3 }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="metric-icon">
        <Icon size={20} />
      </div>
      <div>
        <p>{title}</p>
        <strong>{value}</strong>
      </div>
    </motion.div>
  );

  const ProgressBar = ({ label, value, icon: Icon }) => (
    <div className="resource-row">
      <div className="resource-heading">
        <span>
          <Icon size={16} />
          {label}
        </span>
        <strong>{value}%</strong>
      </div>
      <div className="resource-track">
        <motion.div
          className={`resource-fill ${value > 80 ? 'is-warm' : ''}`}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
    </div>
  );

  return (
    <motion.div
      className="overview-grid"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5, duration: 0.5 }}
    >
      <Widget
        title="Time"
        value={time.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
        })}
        icon={Clock3}
        tone="blue"
      />

      <Widget
        title="Date"
        value={time.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric',
        })}
        icon={CalendarDays}
        tone="green"
      />

      <Widget title="AI Core" value={aiStatus} icon={Zap} tone="amber" />

      <motion.div
        className="resource-card"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.8, duration: 0.5 }}
      >
        <div className="resource-card-title">
          <Activity size={18} />
          <span>Suit telemetry</span>
        </div>
        <ProgressBar label="CPU" value={systemMetrics.cpu} icon={Cpu} />
        <ProgressBar label="RAM" value={systemMetrics.ram} icon={HardDrive} />
        <ProgressBar label="TEMP" value={Math.floor((systemMetrics.temp / 100) * 100)} icon={Thermometer} />
      </motion.div>
    </motion.div>
  );
};

export default HolographicWidgets;

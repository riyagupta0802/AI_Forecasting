import React from 'react';

/**
 * Reusable glowing cyber status badge component
 */
export const StatusBadge = ({ variant = 'phase', text, icon: Icon }) => {
  const variantClass = {
    phase: 'badge-phase',
    connected: 'badge-connected',
    disconnected: 'badge-disconnected',
    checking: 'badge-checking',
  }[variant] || 'badge-phase';

  return (
    <span className={`badge ${variantClass}`}>
      <span className="pulse-dot" />
      {Icon && <Icon size={12} />}
      <span>{text}</span>
    </span>
  );
};

export default StatusBadge;


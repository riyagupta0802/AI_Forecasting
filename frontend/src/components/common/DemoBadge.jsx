import React from 'react';
import { useLanguage } from '../../hooks/useLanguage';

/**
 * Reusable Demo/Simulated tag to clearly disclose prototype data
 */
export const DemoBadge = ({ type = 'demo', size = 'normal', className = '', customText = null }) => {
  const { t } = useLanguage();

  if (customText) {
    return (
      <span
        className={`demo-badge ${size === 'small' ? 'demo-badge-sm' : ''} ${className}`}
        style={{
          border: '1px solid var(--accent-green)',
          color: 'var(--accent-green)',
          background: 'rgba(16, 185, 129, 0.15)',
          fontWeight: 600,
        }}
        title="Evaluated from real model analysis"
      >
        {customText}
      </span>
    );
  }

  const labelMap = {
    demo: t('badges.demo'),
    sample: t('badges.sample'),
    simulated: t('badges.simulated'),
    awaitingModel: t('badges.awaitingModel'),
    conceptPreview: t('badges.conceptPreview'),
    prototype: t('badges.prototype'),
    live: t('badges.live'),
    verified: t('badges.verified'),
    dataset: 'Source: Uploaded Dataset',
    analyzed: 'Real Analysis',
  };

  const styleClass = {
    demo: 'demo-badge-cyan',
    sample: 'demo-badge-blue',
    simulated: 'demo-badge-amber',
    awaitingModel: 'demo-badge-purple',
    conceptPreview: 'demo-badge-indigo',
    prototype: 'demo-badge-emerald',
    live: 'demo-badge-emerald',
    verified: 'demo-badge-cyan',
    dataset: 'demo-badge-emerald',
    analyzed: 'demo-badge-emerald',
  }[type] || 'demo-badge-cyan';

  return (
    <span
      className={`demo-badge ${styleClass} ${size === 'small' ? 'demo-badge-sm' : ''} ${className}`}
      title="Prototype disclosure"
    >
      {labelMap[type] || labelMap.demo}
    </span>
  );
};

export default DemoBadge;


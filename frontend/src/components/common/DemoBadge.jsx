import React from 'react';
import { useLanguage } from '../../hooks/useLanguage';

/**
 * Reusable Demo/Simulated tag to clearly disclose prototype data
 */
export const DemoBadge = ({ type = 'demo', size = 'normal', className = '' }) => {
  const { t } = useLanguage();

  const labelMap = {
    demo: t('badges.demo'),
    sample: t('badges.sample'),
    simulated: t('badges.simulated'),
    awaitingModel: t('badges.awaitingModel'),
    conceptPreview: t('badges.conceptPreview'),
    prototype: t('badges.prototype'),
    live: t('badges.live'),
    verified: t('badges.verified'),
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
  }[type] || 'demo-badge-cyan';

  return (
    <span
      className={`demo-badge ${styleClass} ${size === 'small' ? 'demo-badge-sm' : ''} ${className}`}
      title="Prototype disclosure - not live measurement"
    >
      {labelMap[type] || labelMap.demo}
    </span>
  );
};

export default DemoBadge;


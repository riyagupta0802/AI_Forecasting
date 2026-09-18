import React from 'react';
import { Cpu } from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';
import DemoBadge from './DemoBadge';

export const EmptyState = ({
  icon: Icon = Cpu,
  title,
  description,
  badgeType = 'awaitingModel',
}) => {
  const { t } = useLanguage();

  return (
    <div className="empty-state-card">
      <div className="empty-state-icon-wrap">
        <Icon size={28} />
      </div>
      <div className="empty-state-content">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', justifyContent: 'center', marginBottom: '0.4rem' }}>
          <h4>{title || t('emptyState.awaitingTitle')}</h4>
          <DemoBadge type={badgeType} size="small" />
        </div>
        <p>{description || t('emptyState.awaitingDesc')}</p>
      </div>
    </div>
  );
};

export default EmptyState;


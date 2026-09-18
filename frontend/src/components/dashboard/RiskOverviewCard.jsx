import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';
import DemoBadge from '../common/DemoBadge';

export const RiskOverviewCard = () => {
  const { t } = useLanguage();

  const categories = [
    { name: t('risk.normal'), percent: 78, count: '973 flows', color: 'var(--accent-green)' },
    { name: t('risk.suspicious'), percent: 14, count: '175 flows', color: 'var(--accent-cyan)' },
    { name: t('risk.highRisk'), percent: 6, count: '75 flows', color: 'var(--accent-amber)' },
    { name: t('risk.critical'), percent: 2, count: '25 flows', color: 'var(--accent-red)' },
  ];

  return (
    <div className="soc-card risk-overview-card">
      <div className="soc-card-header">
        <div className="soc-card-title-group">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <ShieldAlert size={20} className="accent-amber-icon" />
            <h3 className="soc-card-title">{t('risk.title')}</h3>
          </div>
          <p className="soc-card-sub">{t('risk.subtitle')}</p>
        </div>
        <DemoBadge type="demo" />
      </div>

      <div className="risk-level-banner">
        <div className="risk-banner-text">
          <span className="risk-banner-label">{t('risk.overallScore')}</span>
          <span className="risk-banner-score text-amber">{t('risk.overallScoreVal')}</span>
        </div>
        <span className="risk-banner-note">{t('risk.scoreNote')}</span>
      </div>

      <div className="risk-bars-list">
        {categories.map((cat, idx) => (
          <div key={idx} className="risk-bar-item">
            <div className="risk-bar-header">
              <span className="risk-bar-name">{cat.name}</span>
              <div className="risk-bar-meta">
                <span className="risk-bar-count">{cat.count}</span>
                <span className="risk-bar-percent" style={{ color: cat.color }}>{cat.percent}%</span>
              </div>
            </div>
            <div className="risk-bar-track">
              <div
                className="risk-bar-fill"
                style={{ width: `${cat.percent}%`, backgroundColor: cat.color }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RiskOverviewCard;


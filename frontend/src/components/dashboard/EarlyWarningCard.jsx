import React from 'react';
import { AlertTriangle, ShieldCheck, Eye, Compass } from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';
import DemoBadge from '../common/DemoBadge';

export const EarlyWarningCard = () => {
  const { t } = useLanguage();

  return (
    <div className="soc-card early-warning-card">
      <div className="soc-card-header">
        <div className="soc-card-title-group">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <AlertTriangle size={20} className="accent-red-icon" />
            <h3 className="soc-card-title">{t('earlyWarnings.title')}</h3>
          </div>
          <p className="soc-card-sub">{t('earlyWarnings.pageSubtitle')}</p>
        </div>
        <DemoBadge type="prototype" />
      </div>

      <div className="early-warning-triage-box">
        <div className="ew-field-row">
          <span className="ew-field-label">
            <Eye size={15} />
            {t('earlyWarnings.warningLevel')}
          </span>
          <div className="ew-field-val-wrap">
            <span className="ew-status-pill pill-monitoring">{t('earlyWarnings.warningLevelVal')}</span>
            <DemoBadge type="sample" size="small" />
          </div>
        </div>

        <div className="ew-field-row">
          <span className="ew-field-label">
            <AlertTriangle size={15} />
            {t('earlyWarnings.potentialRisk')}
          </span>
          <div className="ew-field-val-wrap">
            <span className="ew-text-muted">{t('earlyWarnings.potentialRiskVal')}</span>
            <DemoBadge type="awaitingModel" size="small" />
          </div>
        </div>

        <div className="ew-field-row">
          <span className="ew-field-label">
            <Compass size={15} />
            {t('earlyWarnings.recommendedAction')}
          </span>
          <div className="ew-field-val-wrap">
            <span className="ew-text-muted">{t('earlyWarnings.recommendedActionVal')}</span>
            <DemoBadge type="awaitingModel" size="small" />
          </div>
        </div>
      </div>

      <p className="ew-disclaimer-note">
        {t('earlyWarnings.prototypeNotice')}
      </p>
    </div>
  );
};

export default EarlyWarningCard;


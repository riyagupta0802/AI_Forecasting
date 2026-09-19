import React from 'react';
import { TrendingUp, Clock, AlertTriangle, ShieldCheck, Cpu, ArrowRight, Layers } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import AttackForecastCard from '../components/dashboard/AttackForecastCard';
import DemoBadge from '../components/common/DemoBadge';
import EmptyState from '../components/common/EmptyState';

export const AttackForecastPage = () => {
  const { t } = useLanguage();

  return (
    <div className="soc-page attack-forecast-page">
      {/* Primary Forecast Card */}
      <AttackForecastCard />

      {/* Model Status & Forecasting Architecture Overview */}
      <div className="soc-card forecast-architecture-card">
        <div className="soc-card-header">
          <div className="soc-card-title-group">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <Cpu size={20} className="accent-indigo-icon" />
              <h3 className="soc-card-title">{t('forecast.modelStatus')}</h3>
            </div>
            <p className="soc-card-sub">{t('forecast.modelStatusNote')}</p>
          </div>
          <DemoBadge type="awaitingModel" />
        </div>

        <div className="forecast-specs-grid">
          <div className="forecast-spec-box">
            <span className="spec-label">Temporal Architecture</span>
            <span className="spec-val">Bidirectional LSTM + Temporal Attention</span>
            <span className="spec-sub">Sequence window: 30 time steps (Future Phase)</span>
          </div>

          <div className="forecast-spec-box">
            <span className="spec-label">Multi-Class Classifier</span>
            <span className="spec-val">XGBoost Ensemble</span>
            <span className="spec-sub">CICIDS benchmark classes (Future Phase)</span>
          </div>

          <div className="forecast-spec-box">
            <span className="spec-label">Explainability</span>
            <span className="spec-val">TreeSHAP & Flow Attribution</span>
            <span className="spec-sub">Feature contribution scores (Future Phase)</span>
          </div>

          <div className="forecast-spec-box">
            <span className="spec-label">Escalation Window</span>
            <span className="spec-val">{t('forecast.timeToEscalationVal')}</span>
            <span className="spec-sub">Regression target (Future Phase)</span>
          </div>
        </div>

        <div className="awaiting-ml-notice-banner">
          <EmptyState
            icon={Cpu}
            title={t('forecast.possibleNextStageVal')}
            description={t('forecast.disclaimer')}
            badgeType="awaitingModel"
          />
        </div>
      </div>
    </div>
  );
};

export default AttackForecastPage;


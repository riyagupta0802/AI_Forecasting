import React from 'react';
import { Cpu, CheckCircle2 } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import AttackForecastCard from '../components/dashboard/AttackForecastCard';

export const AttackForecastPage = () => {
  const { t } = useLanguage();

  return (
    <div className="soc-page attack-forecast-page">
      {/* Primary Forecast & Escalation Card */}
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
          <span
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              fontSize: '0.72rem',
              padding: '0.2rem 0.6rem',
              borderRadius: '9999px',
              background: 'rgba(16, 185, 129, 0.12)',
              color: '#10B981',
              border: '1px solid rgba(16, 185, 129, 0.3)',
            }}
          >
            <CheckCircle2 size={13} />
            Phase 6 & 7 Active
          </span>
        </div>

        <div className="forecast-specs-grid">
          <div className="forecast-spec-box">
            <span className="spec-label">Stage Classifier (Phase 6)</span>
            <span className="spec-val">Multi-Class Random Forest</span>
            <span className="spec-sub">Accuracy: 98.0% | Macro F1: 96.0%</span>
          </div>

          <div className="forecast-spec-box">
            <span className="spec-label">Progression Model (Phase 6)</span>
            <span className="spec-val">Cyber Kill Chain Transition Matrix</span>
            <span className="spec-sub">Empirical Intrusion Dynamics (BENIGN, PortScan, Bot, DDoS)</span>
          </div>

          <div className="forecast-spec-box">
            <span className="spec-label">Time-to-Escalation (Phase 7)</span>
            <span className="spec-val">Velocity-Calibrated Regressor</span>
            <span className="spec-sub">MAE: 8.38s | RMSE: 33.83s | R²: 0.9566</span>
          </div>

          <div className="forecast-spec-box">
            <span className="spec-label">Risk Thresholds (Phase 7)</span>
            <span className="spec-val">Dynamic Escalation Windows</span>
            <span className="spec-sub">Critical: &le;60s | High: 61-180s | Moderate: 181-360s</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AttackForecastPage;

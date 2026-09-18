import React from 'react';
import { TrendingUp, Clock, ShieldAlert, Cpu, AlertCircle, ArrowRight } from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';
import DemoBadge from '../common/DemoBadge';

export const AttackForecastCard = ({ forecastData }) => {
  const { t } = useLanguage();

  const currentPattern = forecastData?.current_pattern || t('forecast.currentPatternVal');
  const possibleNextStage = forecastData?.possible_next_stage || t('forecast.possibleNextStageVal');
  const confidenceVal = forecastData?.confidence !== null && forecastData?.confidence !== undefined
    ? `${forecastData.confidence}%`
    : t('forecast.forecastConfidenceVal');
  const timeToEscalationVal = forecastData?.time_to_escalation !== null && forecastData?.time_to_escalation !== undefined
    ? `${forecastData.time_to_escalation}s`
    : t('forecast.timeToEscalationVal');

  const stages = [
    { name: t('forecast.stageRecon'), status: 'active', prob: '84%', active: true },
    { name: t('forecast.stageScan'), status: 'detected', prob: '68%', active: true },
    { name: t('forecast.stageExploit'), status: 'forecasted', prob: '52%', projected: true },
    { name: t('forecast.stageEscalate'), status: 'projected', prob: '35%', projected: true },
    { name: t('forecast.stageExfil'), status: 'awaiting', prob: '12%', projected: true },
  ];

  return (
    <div className="soc-card attack-forecast-card">
      <div className="soc-card-header">
        <div className="soc-card-title-group">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <TrendingUp size={20} className="accent-cyan-icon" />
            <h3 className="soc-card-title">{t('forecast.title')}</h3>
          </div>
          <p className="soc-card-sub">{t('forecast.subtitle')}</p>
        </div>
        <DemoBadge type="awaitingModel" />
      </div>

      {/* Primary Forecast Metrics Grid */}
      <div className="forecast-metrics-grid">
        <div className="forecast-metric-box">
          <span className="forecast-metric-label">{t('forecast.currentPattern')}</span>
          <span className="forecast-metric-val">{currentPattern}</span>
          <DemoBadge type="sample" size="small" />
        </div>

        <div className="forecast-metric-box highlight-box">
          <span className="forecast-metric-label">{t('forecast.possibleNextStage')}</span>
          <span className="forecast-metric-val text-amber">{possibleNextStage}</span>
          <DemoBadge type="awaitingModel" size="small" />
        </div>

        <div className="forecast-metric-box">
          <span className="forecast-metric-label">{t('forecast.forecastConfidence')}</span>
          <span className="forecast-metric-val text-muted">{confidenceVal}</span>
          <DemoBadge type="awaitingModel" size="small" />
        </div>

        <div className="forecast-metric-box">
          <span className="forecast-metric-label">{t('forecast.timeToEscalation')}</span>
          <span className="forecast-metric-val text-cyan">{timeToEscalationVal}</span>
          <DemoBadge type="awaitingModel" size="small" />
        </div>
      </div>

      {/* Visual Attack Trajectory Placeholder */}
      <div className="forecast-trajectory-section">
        <div className="trajectory-header">
          <span className="trajectory-title">{t('forecast.trajectoryTitle')}</span>
          <span className="trajectory-note">{t('forecast.disclaimer')}</span>
        </div>

        <div className="trajectory-stages-track">
          {stages.map((stage, idx) => (
            <div
              key={idx}
              className={`trajectory-stage-node ${stage.projected ? 'node-projected' : 'node-observed'}`}
            >
              <div className="stage-dot-wrap">
                <span className={`stage-dot ${stage.projected ? 'dot-dashed' : 'dot-solid'}`} />
                {idx < stages.length - 1 && <span className="stage-line" />}
              </div>
              <span className="stage-name">{stage.name}</span>
              <span className="stage-prob-badge">
                {stage.projected ? t('forecast.awaitingModelData') : `${stage.prob} (${t('badges.simulated')})`}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="forecast-footer-callout">
        <AlertCircle size={15} />
        <span>{t('forecast.modelStatusNote')}</span>
      </div>
    </div>
  );
};

export default AttackForecastCard;


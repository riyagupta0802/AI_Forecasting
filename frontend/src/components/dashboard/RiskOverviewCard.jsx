import React, { useState, useEffect } from 'react';
import { ShieldAlert } from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';
import DemoBadge from '../common/DemoBadge';
import apiService from '../../services/api';

export const RiskOverviewCard = ({ analysisData: propData }) => {
  const { t } = useLanguage();
  const [analysisData, setAnalysisData] = useState(propData || apiService.getLastAnalysis());

  useEffect(() => {
    if (propData) {
      setAnalysisData(propData);
    }
  }, [propData]);

  useEffect(() => {
    const handleUpdate = (e) => {
      setAnalysisData(e.detail);
    };
    window.addEventListener('netoracle-analysis-updated', handleUpdate);
    return () => window.removeEventListener('netoracle-analysis-updated', handleUpdate);
  }, []);

  const isAnalyzed = Boolean(analysisData && analysisData.total_records);

  const categories = isAnalyzed
    ? [
        {
          name: t('risk.normal'),
          percent: Math.round(100 - (analysisData.attack_percentage || 0)),
          count: `${analysisData.benign_count?.toLocaleString()} flows`,
          color: 'var(--accent-green)',
        },
        {
          name: `${analysisData.dominant_attack_stage || 'Attack'} Threat`,
          percent: Math.round(analysisData.attack_percentage || 0),
          count: `${analysisData.attack_count?.toLocaleString()} flows`,
          color: analysisData.risk_score >= 70 ? 'var(--accent-red)' : (analysisData.risk_score >= 40 ? 'var(--accent-amber)' : 'var(--accent-cyan)'),
        },
      ]
    : [
        { name: t('risk.normal'), percent: 78, count: '973 flows', color: 'var(--accent-green)' },
        { name: t('risk.suspicious'), percent: 14, count: '175 flows', color: 'var(--accent-cyan)' },
        { name: t('risk.highRisk'), percent: 6, count: '75 flows', color: 'var(--accent-amber)' },
        { name: t('risk.critical'), percent: 2, count: '25 flows', color: 'var(--accent-red)' },
      ];

  const scoreDisplay = isAnalyzed ? `${analysisData.risk_score} / 100` : t('risk.overallScoreVal');
  const scoreColor = isAnalyzed
    ? (analysisData.risk_score >= 70 ? 'text-red' : (analysisData.risk_score >= 40 ? 'text-amber' : 'text-cyan'))
    : 'text-amber';

  const scoreNote = isAnalyzed
    ? `Evaluated from ${analysisData.dataset_name} (${analysisData.total_records?.toLocaleString()} flows)`
    : t('risk.scoreNote');

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
        {isAnalyzed ? (
          <DemoBadge customText={`Source: ${analysisData.dataset_name}`} size="small" />
        ) : (
          <DemoBadge type="demo" size="small" />
        )}
      </div>

      <div className="risk-level-banner">
        <div className="risk-banner-text">
          <span className="risk-banner-label">{t('risk.overallScore')}</span>
          <span className={`risk-banner-score ${scoreColor}`}>{scoreDisplay}</span>
        </div>
        <span className="risk-banner-note">{scoreNote}</span>
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

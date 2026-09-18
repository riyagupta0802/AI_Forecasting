import React, { useState } from 'react';
import { AlertTriangle, ShieldAlert, CheckCircle2, Eye, Filter } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import DemoBadge from '../components/common/DemoBadge';

export const EarlyWarningsPage = () => {
  const { t } = useLanguage();
  const [filter, setFilter] = useState('all');

  const warnings = [
    {
      id: 1,
      level: 'High',
      severityClass: 'level-high',
      event: t('earlyWarnings.card1Event'),
      risk: t('earlyWarnings.card1Risk'),
      status: t('earlyWarnings.card1Status'),
      response: t('earlyWarnings.card1Response'),
    },
    {
      id: 2,
      level: 'Medium',
      severityClass: 'level-med',
      event: t('earlyWarnings.card2Event'),
      risk: t('earlyWarnings.card2Risk'),
      status: t('earlyWarnings.card2Status'),
      response: t('earlyWarnings.card2Response'),
    },
    {
      id: 3,
      level: 'Critical',
      severityClass: 'level-critical',
      event: t('earlyWarnings.card3Event'),
      risk: t('earlyWarnings.card3Risk'),
      status: t('earlyWarnings.card3Status'),
      response: t('earlyWarnings.card3Response'),
    },
  ];

  const filteredWarnings = warnings.filter((w) => {
    if (filter === 'all') return true;
    return w.level.toLowerCase() === filter.toLowerCase();
  });

  return (
    <div className="soc-page early-warnings-page">
      {/* Triage Header with Severity Filters */}
      <div className="soc-card warnings-filter-bar">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-secondary)' }}>
            <Filter size={16} />
            <span style={{ fontSize: '0.85rem' }}>{t('earlyWarnings.allSeverities')}:</span>
          </div>

          <div className="filter-pill-group">
            {['all', 'critical', 'high', 'medium'].map((sev) => (
              <button
                key={sev}
                type="button"
                className={`filter-btn ${filter === sev ? 'active' : ''}`}
                onClick={() => setFilter(sev)}
              >
                {sev === 'all'
                  ? t('earlyWarnings.allSeverities')
                  : sev === 'critical'
                    ? t('earlyWarnings.filterCritical')
                    : sev === 'high'
                      ? t('earlyWarnings.filterHigh')
                      : t('earlyWarnings.filterMedium')}
              </button>
            ))}
          </div>
        </div>

        <DemoBadge type="prototype" />
      </div>

      {/* Warnings List */}
      <div className="warnings-cards-list">
        {filteredWarnings.map((w) => (
          <div key={w.id} className="soc-card warning-detail-card">
            <div className="warning-card-top">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span className={`warning-level-tag ${w.severityClass}`}>{w.level}</span>
                <h4 className="warning-event-title">{w.event}</h4>
              </div>
              <DemoBadge type="simulated" size="small" />
            </div>

            <div className="warning-fields-grid">
              <div className="warning-field-block">
                <span className="w-label">{t('earlyWarnings.potentialRisk')}</span>
                <p className="w-val">{w.risk}</p>
              </div>

              <div className="warning-field-block">
                <span className="w-label">Status</span>
                <span className="w-status-badge">{w.status}</span>
              </div>

              <div className="warning-field-block response-block">
                <span className="w-label">{t('earlyWarnings.recommendedAction')}</span>
                <p className="w-response-text">{w.response}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="warnings-footer-notice">
        <AlertTriangle size={16} />
        <span>{t('earlyWarnings.prototypeNotice')}</span>
      </div>
    </div>
  );
};

export default EarlyWarningsPage;


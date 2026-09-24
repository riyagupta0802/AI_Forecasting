import React, { useState, useEffect, useCallback } from 'react';
import {
  AlertTriangle,
  ShieldAlert,
  CheckCircle2,
  Eye,
  Filter,
  RefreshCw,
  Clock,
  Compass,
  Terminal,
  Activity,
  Layers,
  History,
  HelpCircle,
  Hash,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import DemoBadge from '../components/common/DemoBadge';
import apiService from '../services/api';

export const EarlyWarningsPage = () => {
  const { t } = useLanguage();

  const [activeSeverityFilter, setActiveSeverityFilter] = useState('ALL');
  const [selectedScenario, setSelectedScenario] = useState('auto');
  const [warningData, setWarningData] = useState(null);
  const [statusData, setStatusData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedWarningId, setExpandedWarningId] = useState(null);

  const loadWarningData = useCallback(async (scenario = 'auto', sevFilter = 'ALL') => {
    setIsLoading(true);
    try {
      const [warnRes, statRes] = await Promise.all([
        apiService.getWarnings({
          context: scenario,
          severity: sevFilter !== 'ALL' ? sevFilter : undefined,
          limit: 50,
        }),
        apiService.getWarningsStatus(),
      ]);

      if (warnRes && warnRes.data) {
        setWarningData(warnRes.data);
      } else if (warnRes && warnRes.warnings !== undefined) {
        setWarningData(warnRes);
      }

      if (statRes && statRes.data) {
        setStatusData(statRes.data);
      }
    } catch (err) {
      console.error('Failed to load Early Warnings page data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadWarningData(selectedScenario, activeSeverityFilter);
  }, [loadWarningData, selectedScenario, activeSeverityFilter]);

  const activeWarning = warningData?.active_warning;
  const historyList = warningData?.session_history || [];

  const getSeverityTagClass = (sev) => {
    switch (sev?.toUpperCase()) {
      case 'CRITICAL':
        return 'level-critical';
      case 'HIGH':
        return 'level-high';
      case 'MEDIUM':
        return 'level-med';
      case 'LOW':
        return 'level-low';
      case 'INFO':
      default:
        return 'level-info';
    }
  };

  const toggleExpand = (id) => {
    setExpandedWarningId((prev) => (prev === id ? null : id));
  };

  return (
    <div className="soc-page early-warnings-page">
      {/* Triage Control Bar */}
      <div className="soc-card warnings-filter-bar">
        <div className="controls-header-row">
          <div className="controls-title-group">
            <h3 className="controls-heading">{t('earlyWarnings.pageTitle')}</h3>
            <p className="controls-sub">{t('earlyWarnings.pageSubtitle')}</p>
          </div>
          <div className="controls-badges-group">
            <span className="api-status-pill pill-online">
              <CheckCircle2 size={13} />
              ENGINE: {statusData?.status === 'ready' ? 'READY' : 'ONLINE'}
            </span>
            <DemoBadge type="live" />
          </div>
        </div>

        {/* Filter controls row */}
        <div className="warnings-filter-controls-row">
          {/* Severity Filter Pills */}
          <div className="filter-pill-container">
            <span className="filter-label-text">
              <Filter size={14} />
              {t('earlyWarnings.severity')}:
            </span>
            <div className="filter-pill-group">
              {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'].map((sev) => (
                <button
                  key={sev}
                  type="button"
                  className={`filter-btn ${activeSeverityFilter === sev ? 'active' : ''}`}
                  onClick={() => setActiveSeverityFilter(sev)}
                >
                  {sev === 'ALL'
                    ? t('earlyWarnings.filterAll')
                    : sev === 'CRITICAL'
                    ? t('earlyWarnings.filterCritical')
                    : sev === 'HIGH'
                    ? t('earlyWarnings.filterHigh')
                    : sev === 'MEDIUM'
                    ? t('earlyWarnings.filterMedium')
                    : sev === 'LOW'
                    ? t('earlyWarnings.filterLow')
                    : t('earlyWarnings.filterInfo')}
                </button>
              ))}
            </div>
          </div>

          {/* Threat Scenario Context */}
          <div className="scenario-selector-container">
            <span className="filter-label-text">{t('earlyWarnings.evaluateContext')}:</span>
            <select
              className="soc-select-input"
              value={selectedScenario}
              onChange={(e) => setSelectedScenario(e.target.value)}
            >
              <option value="auto">{t('earlyWarnings.scenarioAuto')}</option>
              <option value="portscan">{t('earlyWarnings.scenarioPortscan')}</option>
              <option value="bot">{t('earlyWarnings.scenarioBot')}</option>
              <option value="ddos">{t('earlyWarnings.scenarioDdos')}</option>
              <option value="benign">{t('earlyWarnings.scenarioBenign')}</option>
            </select>
          </div>

          <button
            className="btn-filter-refresh"
            onClick={() => loadWarningData(selectedScenario, activeSeverityFilter)}
            disabled={isLoading}
            title={t('earlyWarnings.refresh')}
          >
            <RefreshCw size={13} className={isLoading ? 'spin-icon' : ''} />
            <span>{isLoading ? t('earlyWarnings.evaluating') : t('earlyWarnings.refresh')}</span>
          </button>
        </div>
      </div>

      {/* Primary Active Alert Showcase Card */}
      {activeWarning && (
        <div
          className={`soc-card active-warning-hero-card ${
            activeWarning.severity === 'CRITICAL'
              ? 'hero-critical'
              : activeWarning.severity === 'HIGH'
              ? 'hero-high'
              : activeWarning.severity === 'MEDIUM'
              ? 'hero-medium'
              : 'hero-baseline'
          }`}
        >
          <div className="hero-top-row">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              <span className={`warning-level-tag ${getSeverityTagClass(activeWarning.severity)}`}>
                {activeWarning.severity}
              </span>
              <span className="hero-type-label">{activeWarning.warning_type}</span>
              <span className={`hero-status-pill pill-${activeWarning.status.toLowerCase()}`}>
                {activeWarning.status}
              </span>
            </div>
            <div className="hero-meta-right">
              <span className="font-mono text-cyan">
                <Hash size={12} />
                {activeWarning.warning_id}
              </span>
              <span className="hero-timestamp">
                <Clock size={12} />
                {activeWarning.timestamp}
              </span>
            </div>
          </div>

          <h3 className="hero-alert-title">{activeWarning.title}</h3>
          <p className="hero-alert-message">{activeWarning.message}</p>

          {/* Quick Threat Vectors */}
          <div className="hero-vectors-grid">
            <div className="vector-card">
              <span className="vector-k">{t('earlyWarnings.currentState')}</span>
              <span className="vector-v font-mono">{activeWarning.current_state}</span>
            </div>
            <div className="vector-card">
              <span className="vector-k">{t('earlyWarnings.predictedState')}</span>
              <span className="vector-v font-mono font-forecast">{activeWarning.predicted_state}</span>
            </div>
            <div className="vector-card">
              <span className="vector-k">{t('earlyWarnings.timeToEscalation')}</span>
              <span className="vector-v font-mono font-escalation">{activeWarning.escalation_window}</span>
            </div>
            <div className="vector-card">
              <span className="vector-k">{t('earlyWarnings.confidence')}</span>
              <span className="vector-v font-mono font-cyan">{(activeWarning.confidence * 100).toFixed(1)}%</span>
            </div>
          </div>

          {/* Recommended Triage Action */}
          <div className="hero-action-box">
            <div className="hero-action-header">
              <Compass size={15} className="accent-indigo-icon" />
              <h4 className="hero-action-title">{t('earlyWarnings.recommendedAttention')}</h4>
            </div>
            <p className="hero-action-desc">{activeWarning.recommended_attention}</p>
          </div>

          {/* Evidence Grid Breakdown */}
          <div className="hero-evidence-wrapper">
            <h4 className="evidence-section-title">
              <ShieldAlert size={15} className="accent-indigo-icon" />
              {t('earlyWarnings.evidence')} ({activeWarning.evidence?.length || 0} Empirical Vectors)
            </h4>
            <div className="evidence-cards-grid">
              {(activeWarning.evidence || []).map((ev, idx) => (
                <div key={idx} className="evidence-grid-card">
                  <div className="evidence-card-top">
                    <span className={`evidence-badge badge-${ev.evidence_type}`}>
                      {ev.evidence_type.toUpperCase()}
                    </span>
                    <span className="evidence-source-tag">{ev.source}</span>
                  </div>
                  <h5 className="evidence-card-headline">{ev.headline}</h5>
                  <p className="evidence-card-desc">{ev.description}</p>
                  {ev.confidence !== null && ev.confidence !== undefined && (
                    <span className="evidence-confidence-tag">
                      Confidence: {(ev.confidence * 100).toFixed(1)}%
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Warning History Log Card */}
      <div className="soc-card warning-history-card">
        <div className="soc-card-header">
          <div className="soc-card-title-group">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <History size={20} className="accent-indigo-icon" />
              <h3 className="soc-card-title">{t('earlyWarnings.warningHistory')}</h3>
            </div>
            <p className="soc-card-sub">
              Auditable session buffer tracking alert progressions and lifecycle transitions ({historyList.length} alerts)
            </p>
          </div>
          <DemoBadge type="verified" />
        </div>

        {historyList.length > 0 ? (
          <div className="table-responsive">
            <table className="soc-table">
              <thead>
                <tr>
                  <th>Alert ID</th>
                  <th>Timestamp</th>
                  <th>Severity</th>
                  <th>Warning Type</th>
                  <th>Current State</th>
                  <th>Predicted Stage</th>
                  <th>Escalation</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {historyList.map((item) => {
                  const isExpanded = expandedWarningId === item.warning_id;
                  return (
                    <React.Fragment key={item.warning_id}>
                      <tr>
                        <td className="font-mono text-cyan">{item.warning_id}</td>
                        <td className="font-mono text-secondary">{item.timestamp?.substring(11, 19)} UTC</td>
                        <td>
                          <span className={`warning-level-tag ${getSeverityTagClass(item.severity)}`}>
                            {item.severity}
                          </span>
                        </td>
                        <td className="font-mono">{item.warning_type}</td>
                        <td className="font-mono">{item.current_state}</td>
                        <td className="font-mono font-forecast">{item.predicted_state}</td>
                        <td className="font-mono font-escalation">{item.escalation_window}</td>
                        <td>
                          <span className={`ew-lifecycle-tag tag-${item.status.toLowerCase()}`}>
                            {item.status}
                          </span>
                        </td>
                        <td>
                          <button
                            className="btn-table-expand"
                            onClick={() => toggleExpand(item.warning_id)}
                          >
                            {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                          </button>
                        </td>
                      </tr>

                      {isExpanded && (
                        <tr className="expanded-row-details">
                          <td colSpan={9}>
                            <div className="history-details-panel">
                              <p className="history-explanation">
                                <strong>Explanation:</strong> {item.message}
                              </p>
                              <p className="history-advice">
                                <strong>Advisory:</strong> {item.recommended_attention}
                              </p>
                              <div className="history-evidence-chips">
                                <strong>Evidence:</strong>
                                {(item.evidence || []).map((ev, i) => (
                                  <span key={i} className="history-evidence-chip">
                                    [{ev.evidence_type.toUpperCase()}] {ev.headline}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="story-empty-state">
            <span>{t('earlyWarnings.noActiveWarnings')}</span>
          </div>
        )}
      </div>

      {/* Disclosed Limitations Banner */}
      <div className="warnings-footer-notice">
        <AlertTriangle size={16} />
        <span>
          <strong>{t('story.limitationsTitle')}:</strong> {t('earlyWarnings.disclaimer')}
        </span>
      </div>
    </div>
  );
};

export default EarlyWarningsPage;

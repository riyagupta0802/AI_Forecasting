import React, { useState, useEffect, useCallback } from 'react';
import {
  AlertTriangle,
  ShieldCheck,
  Eye,
  Compass,
  Clock,
  RefreshCw,
  Layers,
  Terminal,
  Activity,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';
import DemoBadge from '../common/DemoBadge';
import apiService from '../../services/api';

export const EarlyWarningCard = ({ warningData: propWarning = null }) => {
  const { t } = useLanguage();

  const lastAnalysis = apiService.getLastAnalysis();
  const [scenario, setScenario] = useState('auto');
  const [warningData, setWarningData] = useState(propWarning || lastAnalysis?.early_warning || null);
  const [isLoading, setIsLoading] = useState(!propWarning && !lastAnalysis?.early_warning);
  const [isEvidenceExpanded, setIsEvidenceExpanded] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (propWarning) setWarningData(propWarning);
  }, [propWarning]);

  useEffect(() => {
    const handleUpdate = (e) => {
      if (e.detail?.early_warning) setWarningData(e.detail.early_warning);
    };
    window.addEventListener('netoracle-analysis-updated', handleUpdate);
    return () => window.removeEventListener('netoracle-analysis-updated', handleUpdate);
  }, []);

  const fetchWarning = useCallback(async (selectedScenario = 'auto') => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiService.getWarnings({ context: selectedScenario, limit: 40 });
      if (res && res.data) {
        setWarningData(res.data);
      } else if (res && res.active_warning !== undefined) {
        setWarningData(res);
      } else {
        setError(res?.error || 'Failed to retrieve early warnings');
      }
    } catch (err) {
      console.error('Error fetching early warnings:', err);
      setError(err.message || 'Network error fetching early warnings');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!propWarning && !lastAnalysis?.early_warning) {
      fetchWarning(scenario);
    }
  }, [fetchWarning, scenario, propWarning]);

  const activeWarning = warningData?.active_warning || warningData;
  const severity = activeWarning?.severity || 'INFO';
  const hasElevatedWarning = (warningData?.has_active_warning || severity !== 'INFO') && severity !== 'INFO';

  const getSeverityBadgeClass = (sev) => {
    switch (sev?.toUpperCase()) {
      case 'CRITICAL':
        return 'pill-critical';
      case 'HIGH':
        return 'pill-high';
      case 'MEDIUM':
        return 'pill-medium';
      case 'LOW':
        return 'pill-low';
      case 'INFO':
      default:
        return 'pill-info';
    }
  };

  return (
    <div className={`soc-card early-warning-card ${hasElevatedWarning ? 'warning-card-elevated' : 'warning-card-baseline'}`}>
      {/* Header */}
      <div className="soc-card-header">
        <div className="soc-card-title-group">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <AlertTriangle
              size={20}
              className={hasElevatedWarning ? 'accent-red-icon' : 'accent-green-icon'}
            />
            <h3 className="soc-card-title">{t('earlyWarnings.title')}</h3>
          </div>
          <p className="soc-card-sub">{t('earlyWarnings.pageSubtitle')}</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            className="btn-story-refresh"
            onClick={() => fetchWarning(scenario)}
            disabled={isLoading}
            title={t('earlyWarnings.refresh')}
          >
            <RefreshCw size={13} className={isLoading ? 'spin-icon' : ''} />
          </button>
          {lastAnalysis ? (
            <DemoBadge customText={`Source: ${lastAnalysis.dataset_name}`} size="small" />
          ) : (
            <DemoBadge type="live" />
          )}
        </div>
      </div>

      {/* Scenario Evaluation Tabs */}
      <div className="warning-scenario-bar">
        <span className="warning-scenario-label">{t('earlyWarnings.evaluateContext')}:</span>
        <div className="warning-scenario-tabs">
          {[
            { id: 'auto', label: 'Auto' },
            { id: 'portscan', label: 'PortScan' },
            { id: 'bot', label: 'Bot' },
            { id: 'ddos', label: 'DDoS' },
            { id: 'benign', label: 'BENIGN' },
          ].map((item) => (
            <button
              key={item.id}
              className={`warning-tab-btn ${scenario === item.id ? 'active' : ''}`}
              onClick={() => setScenario(item.id)}
              disabled={isLoading}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Alert Box */}
      {isLoading && !warningData ? (
        <div className="story-loading-state">
          <RefreshCw size={20} className="spin-icon" />
          <span>{t('earlyWarnings.evaluating')}</span>
        </div>
      ) : activeWarning ? (
        <div className="early-warning-triage-box">
          {/* Top Banner Row: Severity & Warning Type */}
          <div className="ew-header-status-row">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
              <span className={`ew-severity-pill ${getSeverityBadgeClass(severity)}`}>
                {severity}
              </span>
              <span className="ew-type-badge">{activeWarning.warning_type || 'Alert'}</span>
              <span className={`ew-lifecycle-tag tag-${(activeWarning?.status || 'new').toLowerCase()}`}>
                {activeWarning.status || 'ACTIVE'}
              </span>
            </div>
            <span className="ew-timestamp-text">
              <Clock size={11} />
              {(activeWarning?.timestamp && typeof activeWarning.timestamp === 'string' ? activeWarning.timestamp.substring(11, 19) : '--:--:--')} UTC
            </span>
          </div>

          {/* Alert Title & Message */}
          <div className="ew-body-content">
            <h4 className="ew-alert-title">{activeWarning.title}</h4>
            <p className="ew-alert-desc">{activeWarning.message}</p>
          </div>

          {/* Quick Threat Vector Details */}
          <div className="ew-metrics-grid">
            <div className="ew-metric-cell">
              <span className="ew-cell-label">{t('earlyWarnings.currentState')}</span>
              <span className="ew-cell-val font-mono">{activeWarning.current_state}</span>
            </div>
            <div className="ew-metric-cell">
              <span className="ew-cell-label">{t('earlyWarnings.predictedState')}</span>
              <span className="ew-cell-val font-mono font-forecast">{activeWarning.predicted_state}</span>
            </div>
            <div className="ew-metric-cell">
              <span className="ew-cell-label">{t('earlyWarnings.timeToEscalation')}</span>
              <span className="ew-cell-val font-mono font-escalation">{activeWarning.escalation_window}</span>
            </div>
          </div>

          {/* Recommended SOC Attention */}
          <div className="ew-action-box">
            <div className="ew-action-header">
              <Compass size={14} className="accent-indigo-icon" />
              <span className="ew-action-title">{t('earlyWarnings.recommendedAttention')}</span>
            </div>
            <p className="ew-action-text">{activeWarning.recommended_attention}</p>
          </div>

          {/* Supporting Evidence Toggle */}
          {activeWarning.evidence && activeWarning.evidence.length > 0 && (
            <div className="ew-evidence-section">
              <button
                className="btn-toggle-evidence"
                onClick={() => setIsEvidenceExpanded((prev) => !prev)}
              >
                <span>
                  {t('earlyWarnings.evidence')} ({activeWarning.evidence.length} items)
                </span>
                {isEvidenceExpanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
              </button>

              {isEvidenceExpanded && (
                <div className="ew-evidence-list">
                  {activeWarning.evidence.map((ev, idx) => (
                    <div key={idx} className="ew-evidence-item">
                      <div className="evidence-item-top">
                        <span className={`evidence-type-tag tag-${(ev.evidence_type || 'info').toLowerCase()}`}>
                          {(ev.evidence_type || 'INFO').toUpperCase()}
                        </span>
                        <span className="evidence-headline">{ev.headline}</span>
                      </div>
                      <p className="evidence-desc">{ev.description}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="story-empty-state">
          <span>{t('earlyWarnings.noActiveWarnings')}</span>
        </div>
      )}

      {/* Scope Disclaimer */}
      <p className="ew-disclaimer-note">
        <strong>{t('story.limitationsTitle')}:</strong> {t('earlyWarnings.disclaimer')}
      </p>
    </div>
  );
};

export default EarlyWarningCard;

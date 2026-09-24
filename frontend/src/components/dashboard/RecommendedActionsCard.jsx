import React, { useState, useEffect, useCallback } from 'react';
import {
  ShieldCheck,
  Eye,
  Search,
  Lock,
  Network,
  AlertTriangle,
  Info,
  CheckCircle2,
  Clock,
  ArrowRight,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';
import apiService from '../../services/api';

const getCategoryIcon = (category) => {
  switch ((category || '').toLowerCase()) {
    case 'monitor':
      return Eye;
    case 'investigate':
      return Search;
    case 'isolate':
    case 'contain':
      return Lock;
    case 'escalate':
      return AlertTriangle;
    case 'preserve':
    case 'review':
    default:
      return ShieldCheck;
  }
};

const getPriorityClass = (priority) => {
  switch ((priority || '').toUpperCase()) {
    case 'CRITICAL':
      return 'priority-critical';
    case 'HIGH':
      return 'priority-high';
    case 'MEDIUM':
      return 'priority-med';
    case 'LOW':
    default:
      return 'priority-low';
  }
};

export const RecommendedActionsCard = () => {
  const { t } = useLanguage();
  const [recommendations, setRecommendations] = useState([]);
  const [summary, setSummary] = useState(null);
  const [selectedContext, setSelectedContext] = useState('auto');
  const [isLoading, setIsLoading] = useState(false);
  const [updatingId, setUpdatingId] = useState(null);

  const fetchRecommendations = useCallback(async (context) => {
    setIsLoading(true);
    try {
      const res = await apiService.getRecommendations({ context: context || selectedContext });
      if (res.ok && res.data) {
        setRecommendations(res.data.recommendations || []);
        setSummary(res.data.summary || null);
      }
    } catch (err) {
      console.warn('Failed to fetch recommendations:', err);
    } finally {
      setIsLoading(false);
    }
  }, [selectedContext]);

  useEffect(() => {
    fetchRecommendations(selectedContext);
  }, [fetchRecommendations, selectedContext]);

  const handleScenarioChange = (ctx) => {
    setSelectedContext(ctx);
  };

  const handleStatusToggle = async (recId, currentStatus) => {
    const nextStatus = currentStatus === 'PENDING' ? 'ACKNOWLEDGED' : 'PENDING';
    setUpdatingId(recId);
    try {
      const res = await apiService.updateRecommendationStatus(recId, nextStatus);
      if (res.ok && res.data) {
        setRecommendations((prev) =>
          prev.map((r) => (r.id === recId ? { ...r, status: res.data.status, updated_at: res.data.updated_at } : r))
        );
        if (summary) {
          setSummary((prev) => ({
            ...prev,
            pending: nextStatus === 'PENDING' ? prev.pending + 1 : Math.max(0, prev.pending - 1),
            acknowledged: nextStatus === 'ACKNOWLEDGED' ? prev.acknowledged + 1 : Math.max(0, prev.acknowledged - 1),
          }));
        }
      }
    } catch (err) {
      console.error('Failed to update recommendation status:', err);
    } finally {
      setUpdatingId(null);
    }
  };

  return (
    <div className="soc-card recommended-actions-card">
      <div className="soc-card-header">
        <div className="soc-card-title-group">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <ShieldCheck size={20} className="accent-green-icon" />
            <h3 className="soc-card-title">{t('recommendations.title')}</h3>
          </div>
          <p className="soc-card-sub">{t('recommendations.pageSubtitle')}</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span className="rec-live-badge">{t('recommendations.liveBadge')}</span>
          {summary && (
            <span className="rec-summary-pill">
              {summary.pending} {t('recommendations.pendingReview')}
            </span>
          )}
        </div>
      </div>

      {/* Scenario Evaluation Toolbar */}
      <div className="rec-scenario-toolbar">
        <span className="rec-scenario-label">{t('recommendations.scenarioFilter')}:</span>
        <div className="rec-scenario-buttons">
          {[
            { id: 'auto', label: t('recommendations.scenarioAuto') },
            { id: 'portscan', label: 'PortScan' },
            { id: 'bot', label: 'Botnet C2' },
            { id: 'ddos', label: 'DDoS Flood' },
            { id: 'benign', label: 'BENIGN' },
          ].map((sc) => (
            <button
              key={sc.id}
              type="button"
              className={`rec-scenario-btn ${selectedContext === sc.id ? 'active' : ''}`}
              onClick={() => handleScenarioChange(sc.id)}
              disabled={isLoading}
            >
              {sc.label}
            </button>
          ))}
        </div>
        <button
          type="button"
          className="rec-refresh-btn"
          onClick={() => fetchRecommendations(selectedContext)}
          title={t('recommendations.refresh')}
          disabled={isLoading}
        >
          <RefreshCw size={14} className={isLoading ? 'pulse-dot' : ''} />
        </button>
      </div>

      {/* Guidance Banner */}
      <div className="recommendations-banner">
        <Info size={16} />
        <span>{t('recommendations.defensiveDisclaimer')}</span>
      </div>

      {/* Recommendations Cards Grid */}
      {isLoading ? (
        <div className="rec-loading-container">
          <RefreshCw size={22} className="pulse-dot" />
          <span>{t('recommendations.evaluating')}</span>
        </div>
      ) : recommendations.length === 0 ? (
        <div className="rec-empty-box">
          <CheckCircle2 size={32} className="accent-green-icon" />
          <p>{t('recommendations.noRecommendations')}</p>
        </div>
      ) : (
        <div className="recommendations-grid">
          {recommendations.map((rec) => {
            const Icon = getCategoryIcon(rec.category);
            const priorityClass = getPriorityClass(rec.priority);
            const isUpdating = updatingId === rec.id;

            return (
              <div key={rec.id} className="rec-item-card">
                <div className="rec-item-top">
                  <div className="rec-icon-wrap">
                    <Icon size={16} />
                  </div>
                  <div className="rec-badge-group">
                    <span className={`rec-priority-badge ${priorityClass}`}>{rec.priority}</span>
                    <span className="rec-category-chip">{rec.category}</span>
                    <span className={`rec-status-tag status-${rec.status.toLowerCase()}`}>
                      {rec.status}
                    </span>
                  </div>
                </div>

                <h4 className="rec-item-title">{rec.title}</h4>

                {/* What to do & Why */}
                <div className="rec-body-block">
                  <div className="rec-action-row">
                    <span className="rec-label">{t('recommendations.whatToDo')}:</span>
                    <p className="rec-action-text">{rec.action}</p>
                  </div>
                  <div className="rec-reason-row">
                    <span className="rec-label">{t('recommendations.why')}:</span>
                    <p className="rec-reason-text">{rec.reason}</p>
                  </div>
                </div>

                {/* Grounded Evidence List */}
                {rec.evidence && rec.evidence.length > 0 && (
                  <div className="rec-evidence-block">
                    <span className="rec-evidence-header">{t('recommendations.whatEvidence')}:</span>
                    <ul className="rec-evidence-list">
                      {rec.evidence.slice(0, 3).map((item, idx) => (
                        <li key={idx} className="rec-evidence-item">
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="rec-item-footer">
                  <span className="rec-target-asset">
                    {t('recommendations.targetAsset')}: <code>{rec.target_asset}</code>
                  </span>
                  <button
                    type="button"
                    className={`rec-status-btn ${rec.status === 'ACKNOWLEDGED' ? 'btn-acknowledged' : 'btn-pending'}`}
                    onClick={() => handleStatusToggle(rec.id, rec.status)}
                    disabled={isUpdating}
                  >
                    {isUpdating ? (
                      <RefreshCw size={12} className="pulse-dot" />
                    ) : rec.status === 'ACKNOWLEDGED' ? (
                      <>
                        <CheckCircle2 size={12} /> {t('recommendations.statusAcknowledged')}
                      </>
                    ) : (
                      <>
                        <Clock size={12} /> {t('recommendations.btnAcknowledge')}
                      </>
                    )}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Footer Navigation Link */}
      <div className="rec-card-bottom-bar">
        <p className="rec-auto-disclaimer">
          {t('recommendations.noAutoActionNotice')}
        </p>
        <a href="/recommendations" className="rec-view-all-link">
          {t('recommendations.viewAllLink')} <ArrowRight size={14} />
        </a>
      </div>
    </div>
  );
};

export default RecommendedActionsCard;

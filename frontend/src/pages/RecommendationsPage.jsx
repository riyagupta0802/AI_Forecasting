import React, { useState, useEffect, useCallback } from 'react';
import {
  ShieldCheck,
  Eye,
  Search,
  Lock,
  AlertTriangle,
  Info,
  CheckCircle2,
  Clock,
  RefreshCw,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
  RotateCcw,
} from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import apiService from '../services/api';

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

export const RecommendationsPage = () => {
  const { t } = useLanguage();
  const [recommendations, setRecommendations] = useState([]);
  const [summary, setSummary] = useState(null);
  const [activePosture, setActivePosture] = useState('NORMAL_BASELINE');
  const [selectedContext, setSelectedContext] = useState('auto');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedPriority, setSelectedPriority] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [isLoading, setIsLoading] = useState(false);
  const [updatingId, setUpdatingId] = useState(null);
  const [expandedEvidence, setExpandedEvidence] = useState({});

  const fetchRecommendations = useCallback(async (context) => {
    setIsLoading(true);
    try {
      const res = await apiService.getRecommendations({ context: context || selectedContext });
      if (res.ok && res.data) {
        setRecommendations(res.data.recommendations || []);
        setSummary(res.data.summary || null);
        setActivePosture(res.data.active_threat_posture || 'NORMAL_BASELINE');
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

  const handleStatusUpdate = async (recId, targetStatus) => {
    setUpdatingId(recId);
    try {
      const res = await apiService.updateRecommendationStatus(recId, targetStatus);
      if (res.ok && res.data) {
        setRecommendations((prev) =>
          prev.map((r) => (r.id === recId ? { ...r, status: res.data.status, updated_at: res.data.updated_at } : r))
        );
        // Refresh summary
        setSummary((prev) => {
          if (!prev) return prev;
          const currentRec = recommendations.find((r) => r.id === recId);
          const oldStatus = currentRec ? currentRec.status : 'PENDING';
          const newSummary = { ...prev };
          if (oldStatus === 'PENDING') newSummary.pending = Math.max(0, newSummary.pending - 1);
          if (oldStatus === 'ACKNOWLEDGED') newSummary.acknowledged = Math.max(0, newSummary.acknowledged - 1);
          if (oldStatus === 'RESOLVED') newSummary.resolved = Math.max(0, newSummary.resolved - 1);

          if (targetStatus === 'PENDING') newSummary.pending += 1;
          if (targetStatus === 'ACKNOWLEDGED') newSummary.acknowledged += 1;
          if (targetStatus === 'RESOLVED') newSummary.resolved += 1;
          return newSummary;
        });
      }
    } catch (err) {
      console.error('Failed to update recommendation status:', err);
    } finally {
      setUpdatingId(null);
    }
  };

  const toggleEvidence = (recId) => {
    setExpandedEvidence((prev) => ({
      ...prev,
      [recId]: !prev[recId],
    }));
  };

  // Client-side filtering across Category, Priority, and Status
  const filteredRecs = recommendations.filter((r) => {
    const matchCat =
      selectedCategory === 'all' || r.category.toLowerCase() === selectedCategory.toLowerCase();
    const matchPrio =
      selectedPriority === 'all' || r.priority.toLowerCase() === selectedPriority.toLowerCase();
    const matchStat =
      selectedStatus === 'all' || r.status.toLowerCase() === selectedStatus.toLowerCase();
    return matchCat && matchPrio && matchStat;
  });

  return (
    <div className="soc-page recommendations-page">
      {/* Top Header & Scenario Evaluation Bar */}
      <div className="soc-card rec-header-card">
        <div className="rec-header-top">
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <ShieldCheck size={24} className="accent-green-icon" />
              <h2 className="soc-page-title">{t('recommendations.pageTitle')}</h2>
              <span className="rec-live-badge">{t('recommendations.liveBadge')}</span>
            </div>
            <p className="soc-page-sub">{t('recommendations.pageSubtitle')}</p>
          </div>
          <div className="rec-header-actions">
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
              <RefreshCw size={15} className={isLoading ? 'pulse-dot' : ''} />
            </button>
          </div>
        </div>

        {/* 5 Top Metric Stat Cards */}
        {summary && (
          <div className="rec-metrics-strip">
            <div className="rec-metric-card">
              <span className="rec-metric-val">{summary.total}</span>
              <span className="rec-metric-lbl">{t('recommendations.totalRecommendations')}</span>
            </div>
            <div className="rec-metric-card metric-pending">
              <span className="rec-metric-val">{summary.pending}</span>
              <span className="rec-metric-lbl">{t('recommendations.pendingReview')}</span>
            </div>
            <div className="rec-metric-card metric-acknowledged">
              <span className="rec-metric-val">{summary.acknowledged}</span>
              <span className="rec-metric-lbl">{t('recommendations.acknowledgedCount')}</span>
            </div>
            <div className="rec-metric-card metric-resolved">
              <span className="rec-metric-val">{summary.resolved}</span>
              <span className="rec-metric-lbl">{t('recommendations.resolvedCount')}</span>
            </div>
            <div className="rec-metric-card metric-posture">
              <span className="rec-metric-val">{activePosture}</span>
              <span className="rec-metric-lbl">{t('recommendations.highestPriority')}</span>
            </div>
          </div>
        )}
      </div>

      {/* Multi-Dimensional Filter Bar */}
      <div className="soc-card rec-filter-container">
        {/* Category Filter */}
        <div className="rec-filter-row">
          <span className="rec-filter-heading">
            <SlidersHorizontal size={14} /> Category:
          </span>
          <div className="rec-cat-pills">
            {[
              { id: 'all', label: t('recommendations.categoryAll') },
              { id: 'monitor', label: t('recommendations.categoryMonitor') },
              { id: 'investigate', label: t('recommendations.categoryInvestigate') },
              { id: 'review', label: t('recommendations.categoryReview') },
              { id: 'isolate', label: t('recommendations.categoryIsolate') },
              { id: 'contain', label: t('recommendations.categoryContain') },
              { id: 'escalate', label: t('recommendations.categoryEscalate') },
              { id: 'preserve', label: t('recommendations.categoryPreserve') },
            ].map((cat) => (
              <button
                key={cat.id}
                type="button"
                className={`rec-cat-btn ${selectedCategory === cat.id ? 'active' : ''}`}
                onClick={() => setSelectedCategory(cat.id)}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Priority & Status Filters */}
        <div className="rec-filter-row secondary-filters">
          <div className="rec-filter-group">
            <span className="rec-filter-heading">Priority:</span>
            <div className="rec-pill-group">
              {[
                { id: 'all', label: t('recommendations.priorityAll') },
                { id: 'critical', label: t('recommendations.priorityCritical') },
                { id: 'high', label: t('recommendations.priorityHigh') },
                { id: 'medium', label: t('recommendations.priorityMedium') },
                { id: 'low', label: t('recommendations.priorityLow') },
              ].map((prio) => (
                <button
                  key={prio.id}
                  type="button"
                  className={`rec-cat-btn-sm ${selectedPriority === prio.id ? 'active' : ''}`}
                  onClick={() => setSelectedPriority(prio.id)}
                >
                  {prio.label}
                </button>
              ))}
            </div>
          </div>

          <div className="rec-filter-group">
            <span className="rec-filter-heading">Status:</span>
            <div className="rec-pill-group">
              {[
                { id: 'all', label: 'All' },
                { id: 'pending', label: t('recommendations.statusPending') },
                { id: 'acknowledged', label: t('recommendations.statusAcknowledged') },
                { id: 'resolved', label: t('recommendations.statusResolved') },
              ].map((st) => (
                <button
                  key={st.id}
                  type="button"
                  className={`rec-cat-btn-sm ${selectedStatus === st.id ? 'active' : ''}`}
                  onClick={() => setSelectedStatus(st.id)}
                >
                  {st.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Advisory Guidance Notice */}
      <div className="recommendations-banner">
        <Info size={16} />
        <div>
          <strong>{t('recommendations.defensiveDisclaimer')}</strong>
        </div>
      </div>

      {/* Recommendations Cards Grid */}
      {isLoading ? (
        <div className="rec-loading-container">
          <RefreshCw size={26} className="pulse-dot" />
          <span>{t('recommendations.evaluating')}</span>
        </div>
      ) : filteredRecs.length === 0 ? (
        <div className="soc-card rec-empty-card">
          <CheckCircle2 size={36} className="accent-green-icon" />
          <h3 className="rec-empty-title">{t('recommendations.noRecommendations')}</h3>
          <p className="rec-empty-sub">
            No active security conditions require intervention under current filter criteria.
          </p>
        </div>
      ) : (
        <div className="recommendations-detailed-grid">
          {filteredRecs.map((rec) => {
            const Icon = getCategoryIcon(rec.category);
            const priorityClass = getPriorityClass(rec.priority);
            const isUpdating = updatingId === rec.id;
            const isExpanded = expandedEvidence[rec.id];

            return (
              <div key={rec.id} className="soc-card rec-detail-card">
                {/* Header */}
                <div className="rec-detail-header">
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div className="rec-icon-box">
                      <Icon size={20} />
                    </div>
                    <div>
                      <h4 className="rec-detail-title">{rec.title}</h4>
                      <div className="rec-sub-meta">
                        <span className="rec-detail-asset">
                          Target: <code>{rec.target_asset}</code>
                        </span>
                        <span className="rec-meta-bullet">•</span>
                        <span className="rec-detail-rule">Rule: <code>{rec.rule_id}</code></span>
                      </div>
                    </div>
                  </div>
                  <div className="rec-top-badges">
                    <span className={`rec-priority-badge ${priorityClass}`}>{rec.priority}</span>
                    <span className="rec-category-chip">{rec.category}</span>
                    <span className={`rec-status-tag status-${rec.status.toLowerCase()}`}>
                      {rec.status}
                    </span>
                  </div>
                </div>

                {/* Body: What to do & Why */}
                <div className="rec-detail-body">
                  <div className="rec-section-block">
                    <span className="rec-block-title">{t('recommendations.whatToDo')}</span>
                    <p className="rec-action-callout">{rec.action}</p>
                  </div>

                  <div className="rec-section-block">
                    <span className="rec-block-title">{t('recommendations.why')}</span>
                    <p className="rec-reason-callout">{rec.reason}</p>
                  </div>

                  {/* Supporting Evidence Trail */}
                  {rec.evidence && rec.evidence.length > 0 && (
                    <div className="rec-evidence-accordion">
                      <button
                        type="button"
                        className="rec-evidence-toggle-btn"
                        onClick={() => toggleEvidence(rec.id)}
                      >
                        <span>
                          {t('recommendations.evidenceTitle')} ({rec.evidence.length})
                        </span>
                        {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                      </button>

                      {isExpanded && (
                        <ul className="rec-evidence-expanded-list">
                          {rec.evidence.map((ev, idx) => (
                            <li key={idx} className="rec-evidence-expanded-item">
                              <span className="rec-ev-bullet">•</span>
                              <span>{ev}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </div>

                {/* Footer with Operator Status Actions */}
                <div className="rec-detail-footer">
                  <div className="rec-footer-meta">
                    <span className="rec-id-tag">{rec.id}</span>
                    <span className="rec-time-tag">Updated: {new Date(rec.updated_at).toLocaleTimeString()}</span>
                  </div>

                  <div className="rec-actions-group">
                    {rec.status === 'PENDING' && (
                      <>
                        <button
                          type="button"
                          className="btn-status-act btn-ack"
                          onClick={() => handleStatusUpdate(rec.id, 'ACKNOWLEDGED')}
                          disabled={isUpdating}
                        >
                          <CheckCircle2 size={13} /> {t('recommendations.btnAcknowledge')}
                        </button>
                        <button
                          type="button"
                          className="btn-status-act btn-res"
                          onClick={() => handleStatusUpdate(rec.id, 'RESOLVED')}
                          disabled={isUpdating}
                        >
                          {t('recommendations.btnResolve')}
                        </button>
                      </>
                    )}

                    {rec.status === 'ACKNOWLEDGED' && (
                      <>
                        <button
                          type="button"
                          className="btn-status-act btn-res"
                          onClick={() => handleStatusUpdate(rec.id, 'RESOLVED')}
                          disabled={isUpdating}
                        >
                          <CheckCircle2 size={13} /> {t('recommendations.btnResolve')}
                        </button>
                        <button
                          type="button"
                          className="btn-status-act btn-reopen"
                          onClick={() => handleStatusUpdate(rec.id, 'PENDING')}
                          disabled={isUpdating}
                        >
                          <RotateCcw size={13} /> {t('recommendations.btnReopen')}
                        </button>
                      </>
                    )}

                    {rec.status === 'RESOLVED' && (
                      <button
                        type="button"
                        className="btn-status-act btn-reopen"
                        onClick={() => handleStatusUpdate(rec.id, 'PENDING')}
                        disabled={isUpdating}
                      >
                        <RotateCcw size={13} /> {t('recommendations.btnReopen')}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Page Footer */}
      <div className="rec-page-footer-banner">
        <Info size={16} />
        <div>
          <strong>{t('recommendations.defensiveDisclaimer')}</strong>
          <p>{t('recommendations.noAutoActionNotice')}</p>
        </div>
      </div>
    </div>
  );
};

export default RecommendationsPage;

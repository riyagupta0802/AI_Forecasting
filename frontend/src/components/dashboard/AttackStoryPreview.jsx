import React, { useState, useEffect, useCallback } from 'react';
import {
  GitMerge,
  Clock,
  ShieldAlert,
  Cpu,
  RefreshCw,
  Terminal,
  Activity,
  Layers,
  HelpCircle,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';
import DemoBadge from '../common/DemoBadge';
import apiService from '../../services/api';

export const AttackStoryPreview = ({ showCorrelationGraph = true, storyData: propStory = null }) => {
  const { t } = useLanguage();

  const lastAnalysis = apiService.getLastAnalysis();
  const [selectedScenario, setSelectedScenario] = useState('ALL');
  const [storyData, setStoryData] = useState(propStory || lastAnalysis?.attack_story || null);
  const [isLoading, setIsLoading] = useState(!propStory && !lastAnalysis?.attack_story);
  const [error, setError] = useState(null);
  const [expandedNodeId, setExpandedNodeId] = useState(null);

  useEffect(() => {
    if (propStory) setStoryData(propStory);
  }, [propStory]);

  useEffect(() => {
    const handleUpdate = (e) => {
      if (e.detail?.attack_story) setStoryData(e.detail.attack_story);
    };
    window.addEventListener('netoracle-analysis-updated', handleUpdate);
    return () => window.removeEventListener('netoracle-analysis-updated', handleUpdate);
  }, []);

  const fetchAttackStory = useCallback(async (scenario = 'ALL') => {
    setIsLoading(true);
    setError(null);

    try {
      const params = {
        limit: 40,
        context: scenario.toLowerCase(),
      };
      if (scenario !== 'ALL') {
        params.category = scenario;
      }

      const res = await apiService.getAttackStory(params);
      if (res && res.ok && res.data) {
        setStoryData(res.data);
      } else if (res && res.data && res.data.timeline) {
        // Direct payload handling
        setStoryData(res.data);
      } else {
        setError(res?.error || 'Failed to retrieve attack story');
      }
    } catch (err) {
      console.error('Error fetching attack story:', err);
      setError(err.message || 'Network error fetching attack story');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!propStory && !lastAnalysis?.attack_story) {
      fetchAttackStory(selectedScenario);
    }
  }, [fetchAttackStory, selectedScenario, propStory]);

  const handleScenarioChange = (scenario) => {
    setSelectedScenario(scenario);
    setExpandedNodeId(null);
  };

  const getSeverityBadgeClass = (severity, isForecast) => {
    if (isForecast) return 'badge-forecast';
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return 'badge-critical';
      case 'HIGH':
        return 'badge-high';
      case 'MEDIUM':
        return 'badge-med';
      case 'LOW':
      case 'BENIGN':
      default:
        return 'badge-low';
    }
  };

  const toggleNodeExpand = (nodeId) => {
    setExpandedNodeId((prev) => (prev === nodeId ? null : nodeId));
  };

  return (
    <div className="soc-card attack-story-card">
      {/* Header */}
      <div className="soc-card-header">
        <div className="soc-card-title-group">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <GitMerge size={20} className="accent-indigo-icon" />
            <h3 className="soc-card-title">{t('story.title')}</h3>
          </div>
          <p className="soc-card-sub">{t('story.liveSubtitle')}</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <button
            className="btn-story-refresh"
            onClick={() => fetchAttackStory(selectedScenario)}
            disabled={isLoading}
            title={t('story.refreshStory')}
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

      {/* Scenario Filter Controls */}
      <div className="story-scenario-bar">
        <span className="story-scenario-label">{t('story.scenarioFilter')}:</span>
        <div className="story-scenario-tabs">
          {['ALL', 'PortScan', 'Bot', 'DDoS', 'BENIGN'].map((scenario) => (
            <button
              key={scenario}
              className={`story-tab-btn ${selectedScenario === scenario ? 'active' : ''}`}
              onClick={() => handleScenarioChange(scenario)}
              disabled={isLoading}
            >
              {scenario === 'ALL' ? t('story.allCategories') : scenario}
            </button>
          ))}
        </div>
      </div>

      {/* Telemetry Scope & Limitations Disclaimer */}
      <div className="story-disclaimer-banner">
        <Cpu size={16} />
        <span>
          <strong>{t('story.limitationsTitle')}:</strong>{' '}
          {storyData?.limitations || t('story.correlationDisclaimer')}
        </span>
      </div>

      {/* Quick Metrics Bar */}
      {storyData && (
        <div className="story-quick-metrics-row">
          <div className="story-metric-chip">
            <span className="metric-chip-label">{t('story.activePosture')}</span>
            <span className="metric-chip-val posture-val">{storyData.current_state}</span>
          </div>
          <div className="story-metric-chip">
            <span className="metric-chip-label">{t('story.eventCount')}</span>
            <span className="metric-chip-val">{storyData.event_count}</span>
          </div>
          <div className="story-metric-chip">
            <span className="metric-chip-label">{t('story.clusterCount')}</span>
            <span className="metric-chip-val">{storyData.cluster_count}</span>
          </div>
          <div className="story-metric-chip">
            <span className="metric-chip-label">{t('story.timelineNodes')}</span>
            <span className="metric-chip-val">{storyData.timeline_node_count}</span>
          </div>
        </div>
      )}

      {/* 5-Question Structured Security Incident Narrative */}
      {storyData?.narrative && (
        <div className="story-narrative-box">
          <div className="narrative-box-header">
            <HelpCircle size={16} className="accent-indigo-icon" />
            <h4 className="narrative-box-title">{t('story.socQuestionsTitle')}</h4>
          </div>

          <div className="narrative-qa-grid">
            <div className="narrative-qa-item">
              <span className="qa-question">1. {t('story.whatHappened')}</span>
              <p className="qa-answer">{storyData.narrative.what_happened}</p>
            </div>

            <div className="narrative-qa-item">
              <span className="qa-question">2. {t('story.whatHappenedNext')}</span>
              <p className="qa-answer">{storyData.narrative.what_happened_next}</p>
            </div>

            <div className="narrative-qa-item active-threat-item">
              <span className="qa-question">3. {t('story.whatIsHappeningNow')}</span>
              <p className="qa-answer font-accent">{storyData.narrative.what_is_happening_now}</p>
            </div>

            <div className="narrative-qa-item forecast-item">
              <span className="qa-question">4. {t('story.whatMayHappenNext')}</span>
              <p className="qa-answer font-forecast">{storyData.narrative.what_may_happen_next}</p>
            </div>

            <div className="narrative-qa-item escalation-item">
              <span className="qa-question">5. {t('story.howIsThreatEscalating')}</span>
              <p className="qa-answer font-escalation">{storyData.narrative.how_is_threat_escalating}</p>
            </div>
          </div>
        </div>
      )}

      {/* Chronological Timeline Sequence */}
      <div className="story-timeline-container">
        {isLoading && !storyData ? (
          <div className="story-loading-state">
            <RefreshCw size={22} className="spin-icon" />
            <span>{t('story.loadingStory')}</span>
          </div>
        ) : error && !storyData ? (
          <div className="story-error-state">
            <AlertTriangle size={20} className="accent-red-icon" />
            <span>{error}</span>
          </div>
        ) : storyData?.timeline && storyData.timeline.length > 0 ? (
          storyData.timeline.map((event, idx) => {
            const isExpanded = expandedNodeId === event.node_id;
            return (
              <div key={event.node_id || idx} className="story-timeline-item">
                <div className="story-timeline-rail">
                  <span
                    className={`story-rail-node ${
                      event.is_forecast
                        ? 'rail-node-forecast'
                        : event.is_current
                        ? 'rail-node-current'
                        : ''
                    }`}
                  >
                    {String(idx + 1).padStart(2, '0')}
                  </span>
                  {idx < storyData.timeline.length - 1 && <span className="story-rail-line" />}
                </div>

                <div
                  className={`story-event-card ${
                    event.is_forecast
                      ? 'event-forecast-card'
                      : event.is_current
                      ? 'event-current-card'
                      : ''
                  }`}
                >
                  <div className="story-event-top">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <h4 className="story-event-title">{event.title}</h4>
                      {event.is_current && <span className="tag-current-badge">CURRENT THREAT</span>}
                      {event.is_forecast && <span className="tag-forecast-badge">ML FORECAST</span>}
                    </div>
                    <div className="story-event-meta">
                      <span className={`story-severity-tag ${getSeverityBadgeClass(event.severity, event.is_forecast)}`}>
                        {event.severity}
                      </span>
                      <span className="story-event-time">
                        <Clock size={12} />
                        {event.timestamp_label}
                      </span>
                    </div>
                  </div>

                  <p className="story-event-desc">{event.description}</p>

                  <div className="story-node-footer">
                    <span className="story-node-stage">
                      <Layers size={12} />
                      {event.stage}
                    </span>

                    {event.target_ports && event.target_ports.length > 0 && (
                      <span className="story-node-ports">
                        <Terminal size={12} />
                        Ports: {event.target_ports.slice(0, 4).join(', ')}
                        {event.target_ports.length > 4 ? ` (+${event.target_ports.length - 4})` : ''}
                      </span>
                    )}

                    {event.details && Object.keys(event.details).length > 0 && (
                      <button
                        className="btn-toggle-details"
                        onClick={() => toggleNodeExpand(event.node_id)}
                      >
                        {isExpanded ? (
                          <>
                            Less <ChevronUp size={12} />
                          </>
                        ) : (
                          <>
                            Telemetry Details <ChevronDown size={12} />
                          </>
                        )}
                      </button>
                    )}
                  </div>

                  {/* Expandable Flow Telemetry Drawer */}
                  {isExpanded && event.details && (
                    <div className="story-details-drawer">
                      <div className="details-grid">
                        {event.details.total_packets !== undefined && (
                          <div className="detail-item">
                            <span className="detail-k">Packets</span>
                            <span className="detail-v">{event.details.total_packets}</span>
                          </div>
                        )}
                        {event.details.total_bytes !== undefined && (
                          <div className="detail-item">
                            <span className="detail-k">Bytes</span>
                            <span className="detail-v">{event.details.total_bytes}</span>
                          </div>
                        )}
                        {event.details.duration_ms !== undefined && (
                          <div className="detail-item">
                            <span className="detail-k">Duration</span>
                            <span className="detail-v">
                              {typeof event.details.duration_ms === 'number'
                                ? `${event.details.duration_ms.toFixed(2)} ms`
                                : (event.details.duration_ms || '—')}
                            </span>
                          </div>
                        )}
                        {event.details.syn_flag_count !== undefined && (
                          <div className="detail-item">
                            <span className="detail-k">SYN Flags</span>
                            <span className="detail-v">{event.details.syn_flag_count}</span>
                          </div>
                        )}
                        {event.details.ack_flag_count !== undefined && (
                          <div className="detail-item">
                            <span className="detail-k">ACK Flags</span>
                            <span className="detail-v">{event.details.ack_flag_count}</span>
                          </div>
                        )}
                        {event.details.velocity_factor !== undefined && (
                          <div className="detail-item">
                            <span className="detail-k">Velocity Factor</span>
                            <span className="detail-v">{event.details.velocity_factor}x</span>
                          </div>
                        )}
                        {event.details.model_confidence !== undefined && (
                          <div className="detail-item">
                            <span className="detail-k">Model Confidence</span>
                            <span className="detail-v">
                              {typeof event.details.model_confidence === 'number'
                                ? `${(event.details.model_confidence * 100).toFixed(1)}%`
                                : 'N/A'}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        ) : (
          <div className="story-empty-state">
            <span>{t('story.noEventsFound')}</span>
          </div>
        )}
      </div>

      {/* Correlation Sequence Graph Chips */}
      {showCorrelationGraph && storyData?.clusters && storyData.clusters.length > 0 && (
        <div className="story-graph-preview">
          <span className="graph-preview-title">{t('story.correlationGraph')}</span>
          <div className="graph-nodes-row">
            {storyData.clusters.map((cluster, idx) => (
              <React.Fragment key={cluster.cluster_id || idx}>
                <span
                  className={`graph-node-chip ${
                    cluster.category === 'BENIGN'
                      ? 'chip-observed'
                      : cluster.severity === 'CRITICAL' || cluster.severity === 'HIGH'
                      ? 'chip-critical'
                      : 'chip-warning'
                  }`}
                  title={`${cluster.event_count} flows across ports ${Array.isArray(cluster.destination_ports) ? cluster.destination_ports.slice(0, 3).join(', ') : 'any'}`}
                >
                  {cluster.category} ({cluster.event_count})
                </span>
                {idx < storyData.clusters.length - 1 && <span className="graph-chip-arrow">→</span>}
              </React.Fragment>
            ))}
            {storyData.forecast?.predicted_stage && (
              <>
                <span className="graph-chip-arrow">→</span>
                <span className="graph-node-chip chip-forecast">
                  {storyData.forecast.predicted_stage} (Forecast)
                </span>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AttackStoryPreview;

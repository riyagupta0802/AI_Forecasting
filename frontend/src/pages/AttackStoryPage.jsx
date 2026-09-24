import React, { useState, useEffect, useCallback } from 'react';
import {
  GitMerge,
  Clock,
  ArrowRight,
  Share2,
  ShieldAlert,
  Layers,
  Terminal,
  Activity,
  Filter,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Search,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import AttackStoryPreview from '../components/dashboard/AttackStoryPreview';
import DemoBadge from '../components/common/DemoBadge';
import apiService from '../services/api';

export const AttackStoryPage = () => {
  const { t } = useLanguage();

  const [activeScenario, setActiveScenario] = useState('ALL');
  const [activeSeverity, setActiveSeverity] = useState('ALL');
  const [eventLimit, setEventLimit] = useState(50);
  const [storyData, setStoryData] = useState(null);
  const [statusData, setStatusData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRawEventsExpanded, setIsRawEventsExpanded] = useState(false);
  const [eventSearchQuery, setEventSearchQuery] = useState('');

  const loadStoryPageData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [storyRes, statusRes] = await Promise.all([
        apiService.getAttackStory({
          category: activeScenario !== 'ALL' ? activeScenario : undefined,
          severity: activeSeverity !== 'ALL' ? activeSeverity : undefined,
          context: activeScenario.toLowerCase(),
          limit: eventLimit,
        }),
        apiService.getAttackStoryStatus(),
      ]);

      if (storyRes && storyRes.data) {
        setStoryData(storyRes.data);
      }
      if (statusRes && statusRes.data) {
        setStatusData(statusRes.data);
      }
    } catch (err) {
      console.error('Failed to load Attack Story page data:', err);
    } finally {
      setIsLoading(false);
    }
  }, [activeScenario, activeSeverity, eventLimit]);

  useEffect(() => {
    loadStoryPageData();
  }, [loadStoryPageData]);

  const filteredRawEvents = (storyData?.events_sample || []).filter((evt) => {
    if (!eventSearchQuery.trim()) return true;
    const query = eventSearchQuery.toLowerCase();
    return (
      evt.event_id?.toLowerCase().includes(query) ||
      evt.service_name?.toLowerCase().includes(query) ||
      String(evt.destination_port).includes(query) ||
      evt.category?.toLowerCase().includes(query)
    );
  });

  return (
    <div className="soc-page attack-story-page">
      {/* Top Status & Controls Strip */}
      <div className="story-controls-card">
        <div className="controls-header-row">
          <div className="controls-title-group">
            <h3 className="controls-heading">{t('story.pageTitle')}</h3>
            <p className="controls-sub">{t('story.liveSubtitle')}</p>
          </div>
          <div className="controls-badges-group">
            <span className="api-status-pill pill-online">
              <CheckCircle2 size={13} />
              API: {statusData?.status === 'ready' ? 'READY' : 'ONLINE'}
            </span>
            <DemoBadge type="live" />
          </div>
        </div>

        <div className="controls-filters-row">
          <div className="filter-group">
            <label className="filter-label">{t('story.scenarioFilter')}:</label>
            <select
              className="soc-select-input"
              value={activeScenario}
              onChange={(e) => setActiveScenario(e.target.value)}
            >
              <option value="ALL">{t('story.allCategories')}</option>
              <option value="PortScan">PortScan (Host Reconnaissance)</option>
              <option value="Bot">Bot (C2 Staging & IRC)</option>
              <option value="DDoS">DDoS (Web Flood Disruption)</option>
              <option value="BENIGN">BENIGN (Normal Baseline)</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">{t('story.severityFilter')}:</label>
            <select
              className="soc-select-input"
              value={activeSeverity}
              onChange={(e) => setActiveSeverity(e.target.value)}
            >
              <option value="ALL">{t('story.allSeverities')}</option>
              <option value="CRITICAL">CRITICAL</option>
              <option value="HIGH">HIGH</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="LOW">LOW</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="filter-label">Flow Limit:</label>
            <select
              className="soc-select-input"
              value={eventLimit}
              onChange={(e) => setEventLimit(Number(e.target.value))}
            >
              <option value={25}>25 flows</option>
              <option value={50}>50 flows (Standard)</option>
              <option value={100}>100 flows</option>
              <option value={200}>200 flows</option>
            </select>
          </div>

          <button
            className="btn-filter-refresh"
            onClick={loadStoryPageData}
            disabled={isLoading}
            title={t('story.refreshStory')}
          >
            <RefreshCw size={14} className={isLoading ? 'spin-icon' : ''} />
            <span>{isLoading ? t('story.loadingStory') : t('story.refreshStory')}</span>
          </button>
        </div>
      </div>

      {/* Primary Timeline View with 5 SOC Questions Narrative */}
      <AttackStoryPreview showCorrelationGraph={false} />

      {/* Deep Event Graph Correlation Diagram */}
      <div className="soc-card graph-correlation-card">
        <div className="soc-card-header">
          <div className="soc-card-title-group">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <Share2 size={20} className="accent-indigo-icon" />
              <h3 className="soc-card-title">{t('story.correlationGraph')}</h3>
            </div>
            <p className="soc-card-sub">
              Empirical service-port clusters and cross-stage transition linkages
            </p>
          </div>
          <DemoBadge type="verified" />
        </div>

        {/* Dynamic Multi-Stage Flow Graph */}
        <div className="graph-nodes-flow-container">
          {storyData?.clusters && storyData.clusters.length > 0 ? (
            storyData.clusters.map((cluster, idx) => (
              <React.Fragment key={cluster.cluster_id || idx}>
                <div
                  className={`correlation-node-card ${
                    cluster.category !== 'BENIGN' ? 'node-threat-active' : ''
                  }`}
                >
                  <div className="cnode-top">
                    <span className="cnode-id">{cluster.cluster_id}</span>
                    <span
                      className={`cnode-severity ${
                        cluster.severity === 'CRITICAL'
                          ? 'sev-critical'
                          : cluster.severity === 'HIGH'
                          ? 'sev-high'
                          : cluster.severity === 'MEDIUM'
                          ? 'sev-med'
                          : 'sev-low'
                      }`}
                    >
                      {cluster.severity}
                    </span>
                  </div>

                  <h4 className="cnode-label">{cluster.category} Cluster</h4>

                  <div className="cnode-meta">
                    <span className="cnode-proto">
                      <Terminal size={11} />
                      Ports: {cluster.destination_ports.slice(0, 3).join(', ')}
                      {cluster.destination_ports.length > 3 ? ` (+${cluster.destination_ports.length - 3})` : ''}
                    </span>
                    <span className="cnode-time">
                      <Clock size={11} />
                      {cluster.time_span}
                    </span>
                  </div>

                  <div className="cnode-stage-pill">
                    <Layers size={11} />
                    {cluster.kill_chain_stage}
                  </div>

                  <div className="cnode-footer-stats">
                    <span>{cluster.event_count} flows</span>
                    <span>{cluster.total_packets} pkts</span>
                    <span>{(cluster.total_bytes / 1024).toFixed(1)} KB</span>
                  </div>
                </div>

                {idx < storyData.clusters.length - 1 && (
                  <div className="cnode-link" aria-label="Causality link">
                    <span className="clink-label">{t('story.relationshipLabel')}</span>
                    <div className="clink-arrow-line">
                      <ArrowRight size={18} />
                    </div>
                  </div>
                )}
              </React.Fragment>
            ))
          ) : (
            <div className="graph-empty-message">
              <span>{t('story.noEventsFound')}</span>
            </div>
          )}

          {/* Forecasted Stage Node */}
          {storyData?.forecast?.predicted_stage && (
            <>
              <div className="cnode-link" aria-label="Forecast transition">
                <span className="clink-label">ML Transition</span>
                <div className="clink-arrow-line link-forecast-arrow">
                  <ArrowRight size={18} />
                </div>
              </div>

              <div className="correlation-node-card node-forecast-glow">
                <div className="cnode-top">
                  <span className="cnode-id">FORECAST-01</span>
                  <span className="cnode-severity sev-forecast">ML PROJECTION</span>
                </div>
                <h4 className="cnode-label">{storyData.forecast.predicted_stage}</h4>
                <div className="cnode-meta">
                  <span className="cnode-proto">Transition Probability</span>
                  <span className="cnode-time">
                    {((storyData.forecast.confidence || 0) * 100).toFixed(1)}% Conf.
                  </span>
                </div>
                <div className="cnode-stage-pill">
                  <Layers size={11} />
                  Projected Next Stage
                </div>
                <div className="cnode-footer-stats font-forecast">
                  <span>Escalation: {storyData.escalation?.status || 'Calculated'}</span>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Technical Data Grounding Banner */}
        <div className="graph-footer-banner">
          <ShieldAlert size={16} />
          <span>
            {storyData?.limitations ||
              'Telemetry reflects genuine CICIDS2017 aggregate flow records. Relative timeline offsets are accumulated deterministically from microsecond durations without synthetic fabrication.'}
          </span>
        </div>
      </div>

      {/* Raw Correlated Telemetry Inspector */}
      <div className="soc-card raw-events-table-card">
        <div className="soc-card-header">
          <div className="soc-card-title-group">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <Terminal size={20} className="accent-indigo-icon" />
              <h3 className="soc-card-title">{t('story.inspectEvents')}</h3>
            </div>
            <p className="soc-card-sub">
              Individual flow records with ground-truth ports, durations, and TCP flag metrics ({filteredRawEvents.length} events)
            </p>
          </div>
          <button
            className="btn-toggle-raw"
            onClick={() => setIsRawEventsExpanded((prev) => !prev)}
          >
            {isRawEventsExpanded ? (
              <>
                {t('story.hideEvents')} <ChevronUp size={14} />
              </>
            ) : (
              <>
                {t('story.inspectEvents')} <ChevronDown size={14} />
              </>
            )}
          </button>
        </div>

        {isRawEventsExpanded && (
          <div className="raw-events-content">
            {/* Search Filter Box */}
            <div className="raw-search-bar">
              <Search size={14} className="search-icon" />
              <input
                type="text"
                placeholder="Search event ID, port, service name, or category..."
                value={eventSearchQuery}
                onChange={(e) => setEventSearchQuery(e.target.value)}
                className="raw-search-input"
              />
            </div>

            <div className="table-responsive">
              <table className="soc-table">
                <thead>
                  <tr>
                    <th>Event ID</th>
                    <th>Offset</th>
                    <th>Category</th>
                    <th>Dst Port</th>
                    <th>Service</th>
                    <th>Duration</th>
                    <th>Packets</th>
                    <th>Bytes</th>
                    <th>Flags (SYN / ACK)</th>
                    <th>Severity</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRawEvents.map((evt) => (
                    <tr key={evt.event_id}>
                      <td className="font-mono text-cyan">{evt.event_id}</td>
                      <td className="font-mono">{evt.timestamp_offset}</td>
                      <td>
                        <span
                          className={`category-pill ${
                            evt.category === 'BENIGN'
                              ? 'pill-benign'
                              : evt.category === 'DDoS'
                              ? 'pill-ddos'
                              : evt.category === 'Bot'
                              ? 'pill-bot'
                              : 'pill-portscan'
                          }`}
                        >
                          {evt.category}
                        </span>
                      </td>
                      <td className="font-mono">{evt.destination_port}</td>
                      <td className="text-secondary">{evt.service_name}</td>
                      <td className="font-mono">{evt.duration_ms.toFixed(1)} ms</td>
                      <td className="font-mono">{evt.packet_count}</td>
                      <td className="font-mono">{evt.byte_count} B</td>
                      <td className="font-mono">
                        SYN: {evt.syn_flag_count} | ACK: {evt.ack_flag_count}
                      </td>
                      <td>
                        <span
                          className={`severity-badge ${
                            evt.severity === 'CRITICAL'
                              ? 'sev-critical'
                              : evt.severity === 'HIGH'
                              ? 'sev-high'
                              : evt.severity === 'MEDIUM'
                              ? 'sev-med'
                              : 'sev-low'
                          }`}
                        >
                          {evt.severity}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AttackStoryPage;

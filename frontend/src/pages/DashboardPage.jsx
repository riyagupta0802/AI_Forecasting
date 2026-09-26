import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Globe, ShieldAlert, AlertTriangle, RefreshCw, CheckCircle2 } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import SummaryCard from '../components/dashboard/SummaryCard';
import SecurityPipeline from '../components/dashboard/SecurityPipeline';
import AttackDetectionCard from '../components/dashboard/AttackDetectionCard';
import AttackForecastCard from '../components/dashboard/AttackForecastCard';
import NetworkTrafficChart from '../components/dashboard/NetworkTrafficChart';
import RiskOverviewCard from '../components/dashboard/RiskOverviewCard';
import AttackStoryPreview from '../components/dashboard/AttackStoryPreview';
import EarlyWarningCard from '../components/dashboard/EarlyWarningCard';
import RecommendedActionsCard from '../components/dashboard/RecommendedActionsCard';
import ExplainabilityCard from '../components/dashboard/ExplainabilityCard';
import apiService from '../services/api';

export const DashboardPage = () => {
  const { t } = useLanguage();

  const [analysisData, setAnalysisData] = useState(() => apiService.getLastAnalysis());

  // Fallback demo values if backend is offline or no dataset is analyzed
  const [summaryData, setSummaryData] = useState({
    network_status: 'ONLINE',
    active_connections: 1248,
    detected_anomalies: 7,
    active_warnings: 3,
  });

  const [forecastData, setForecastData] = useState({
    status: 'awaiting_model',
    current_pattern: 'Awaiting ML model',
    possible_next_stage: 'Awaiting ML model',
    confidence: null,
    time_to_escalation: null,
  });

  const [trafficPoints, setTrafficPoints] = useState(null);
  const [isBackendOnline, setIsBackendOnline] = useState(true);
  const [isLoading, setIsLoading] = useState(true);

  // Listen for real-time analysis updates from NetworkTrafficPage
  useEffect(() => {
    const handleAnalysisUpdate = (e) => {
      setAnalysisData(e.detail);
    };
    window.addEventListener('netoracle-analysis-updated', handleAnalysisUpdate);
    return () => window.removeEventListener('netoracle-analysis-updated', handleAnalysisUpdate);
  }, []);

  const fetchDashboardData = useCallback(async () => {
    setIsLoading(true);

    try {
      const [summaryRes, forecastRes, trafficRes, sysRes] = await Promise.all([
        apiService.getNetworkSummary(),
        apiService.getForecastStatus(),
        apiService.getTrafficSample(),
        apiService.getSystemStatus(),
      ]);

      const backendAlive = summaryRes.ok || sysRes.ok;
      setIsBackendOnline(backendAlive);

      if (summaryRes.ok && summaryRes.data) {
        setSummaryData(summaryRes.data);
      }

      if (forecastRes.ok && forecastRes.data) {
        setForecastData(forecastRes.data);
      }

      if (trafficRes.ok && trafficRes.data?.data) {
        setTrafficPoints(trafficRes.data.data);
      }
    } catch (err) {
      console.warn('Backend unavailable, using simulated prototype fallback data:', err);
      setIsBackendOnline(false);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const isAnalyzed = Boolean(analysisData && analysisData.total_records);

  // Compute live summary values when dataset is loaded
  const displayStatus = isAnalyzed ? 'ANALYZED' : (summaryData.network_status || t('dashboard.networkStatusVal'));
  const displayConnections = isAnalyzed
    ? analysisData.total_records.toLocaleString()
    : (summaryData.active_connections ? summaryData.active_connections.toLocaleString() : t('dashboard.activeConnectionsVal'));
  const displayAnomalies = isAnalyzed
    ? String(analysisData.attack_count).padStart(2, '0')
    : String(summaryData.detected_anomalies).padStart(2, '0');
  const displayWarnings = isAnalyzed
    ? String(analysisData.early_warning?.has_active_warning ? 1 : 0).padStart(2, '0')
    : String(summaryData.active_warnings).padStart(2, '0');

  const badgeSource = isAnalyzed ? `Source: ${analysisData.dataset_name}` : null;

  return (
    <div className="soc-page dashboard-page">
      {/* Offline Alert Banner (Only shown if FastAPI backend is unreachable) */}
      {!isBackendOnline && (
        <div className="soc-offline-banner" role="alert">
          <div className="soc-offline-text-group">
            <AlertTriangle size={18} className="accent-amber-icon" />
            <div>
              <strong>{t('api.offlineNotice')}</strong>
              <p>{t('api.fallbackWarning')}</p>
            </div>
          </div>
          <button
            type="button"
            className="btn-offline-retry"
            onClick={fetchDashboardData}
            disabled={isLoading}
          >
            <RefreshCw size={14} className={isLoading ? 'pulse-dot' : ''} />
            {isLoading ? t('status.checking') : t('api.retryButton')}
          </button>
        </div>
      )}

      {/* Active Dataset Ingestion Banner */}
      {isAnalyzed && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0.85rem 1.25rem',
            background: 'rgba(16, 185, 129, 0.08)',
            border: '1px solid var(--accent-green)',
            borderRadius: '8px',
            marginBottom: '1.25rem',
            flexWrap: 'wrap',
            gap: '0.75rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <CheckCircle2 size={18} style={{ color: 'var(--accent-green)', flexShrink: 0 }} />
            <div>
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--accent-green)' }}>
                Analysis Source: {analysisData.dataset_name} ({analysisData.total_records?.toLocaleString()} flows evaluated)
              </span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: '0.6rem' }}>
                {new Date(analysisData.analysis_timestamp).toLocaleTimeString()}
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Attacks: <strong style={{ color: 'var(--accent-red)' }}>{analysisData.attack_count} ({analysisData.attack_percentage}%)</strong> | Benign: <strong style={{ color: 'var(--accent-green)' }}>{analysisData.benign_count}</strong>
            </span>
            <button
              type="button"
              onClick={() => {
                apiService.clearLastAnalysis();
                setAnalysisData(null);
              }}
              style={{
                background: 'transparent',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-muted)',
                fontSize: '0.75rem',
                padding: '0.25rem 0.65rem',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
              title="Reset to default prototype demonstration"
            >
              Reset to Baseline
            </button>
          </div>
        </div>
      )}

      {/* 4 Primary Summary Cards */}
      <section className="summary-cards-grid" aria-label="Security Metrics Summary">
        <SummaryCard
          title={t('dashboard.networkStatus')}
          value={displayStatus}
          subtitle={isAnalyzed ? `${analysisData.total_records} flows evaluated` : t('dashboard.trafficVolumeDesc')}
          icon={Globe}
          badgeType={isAnalyzed ? 'dataset' : 'demo'}
          customBadgeText={badgeSource}
          variant="green"
        />

        <SummaryCard
          title={isAnalyzed ? 'Total Analyzed Flows' : t('dashboard.activeConnections')}
          value={displayConnections}
          subtitle={isAnalyzed ? `${analysisData.benign_count} normal baseline` : t('traffic.liveFlowIndicator')}
          icon={Activity}
          badgeType={isAnalyzed ? 'dataset' : 'simulated'}
          customBadgeText={badgeSource}
          variant="cyan"
        />

        <SummaryCard
          title={isAnalyzed ? 'Detected Attack Flows' : t('dashboard.detectedAnomalies')}
          value={displayAnomalies}
          subtitle={isAnalyzed ? `${analysisData.attack_percentage}% attack rate` : t('dashboard.anomalyChangeDesc')}
          icon={AlertTriangle}
          badgeType={isAnalyzed ? 'dataset' : 'demo'}
          customBadgeText={badgeSource}
          variant="amber"
        />

        <SummaryCard
          title={t('dashboard.activeWarnings')}
          value={displayWarnings}
          subtitle={isAnalyzed ? `Severity: ${analysisData.early_warning?.severity || 'LOW'}` : t('dashboard.warningChangeDesc')}
          icon={ShieldAlert}
          badgeType={isAnalyzed ? 'dataset' : 'demo'}
          customBadgeText={badgeSource}
          variant="red"
        />
      </section>

      {/* Security Pipeline Flow */}
      <section className="pipeline-section-wrapper">
        <SecurityPipeline />
      </section>

      {/* AI Attack Detection - Random Forest Classifier (Phase 5) */}
      <section className="soc-full-width-section">
        <AttackDetectionCard analysisData={analysisData} />
      </section>

      {/* Real Explainable AI (XAI) - TreeExplainer SHAP Analysis (Phase 11) */}
      <section className="soc-full-width-section" id="explainability-section">
        <ExplainabilityCard explanationData={analysisData?.explainability} />
      </section>

      {/* Attack Forecast Major Card (Phase 6 & 7) & Risk Overview */}
      <div className="soc-two-col-grid">
        <AttackForecastCard
          forecastData={analysisData?.forecast || forecastData}
          escalationData={analysisData?.escalation}
        />
        <RiskOverviewCard analysisData={analysisData} />
      </div>

      {/* Network Traffic Telemetry Chart */}
      <section className="soc-full-width-section">
        <NetworkTrafficChart trafficData={trafficPoints} />
      </section>

      {/* Attack Story Correlation & Early Warning (Phase 8 & 9) */}
      <div className="soc-two-col-grid">
        <AttackStoryPreview storyData={analysisData?.attack_story} />
        <EarlyWarningCard warningData={analysisData?.early_warning} />
      </div>

      {/* Recommended Actions (Phase 10) */}
      <section className="soc-full-width-section">
        <RecommendedActionsCard recommendationsData={analysisData?.recommendations} />
      </section>
    </div>
  );
};

export default DashboardPage;

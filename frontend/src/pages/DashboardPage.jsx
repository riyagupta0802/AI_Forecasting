import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Globe, ShieldAlert, AlertTriangle, RefreshCw, CheckCircle2 } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import SummaryCard from '../components/dashboard/SummaryCard';
import SecurityPipeline from '../components/dashboard/SecurityPipeline';
import AttackForecastCard from '../components/dashboard/AttackForecastCard';
import NetworkTrafficChart from '../components/dashboard/NetworkTrafficChart';
import RiskOverviewCard from '../components/dashboard/RiskOverviewCard';
import AttackStoryPreview from '../components/dashboard/AttackStoryPreview';
import EarlyWarningCard from '../components/dashboard/EarlyWarningCard';
import RecommendedActionsCard from '../components/dashboard/RecommendedActionsCard';
import apiService from '../services/api';

export const DashboardPage = () => {
  const { t } = useLanguage();

  // Fallback demo values if backend is offline
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

  const fetchDashboardData = useCallback(async () => {
    setIsLoading(true);

    try {
      // Parallel fetch across all Phase 3 endpoints
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

      {/* 4 Primary Summary Cards (wired to backend /api/network/summary) */}
      <section className="summary-cards-grid" aria-label="Security Metrics Summary">
        <SummaryCard
          title={t('dashboard.networkStatus')}
          value={summaryData.network_status || t('dashboard.networkStatusVal')}
          subtitle={t('dashboard.trafficVolumeDesc')}
          icon={Globe}
          badgeType="demo"
          variant="green"
        />

        <SummaryCard
          title={t('dashboard.activeConnections')}
          value={summaryData.active_connections ? summaryData.active_connections.toLocaleString() : t('dashboard.activeConnectionsVal')}
          subtitle={t('traffic.liveFlowIndicator')}
          icon={Activity}
          badgeType="simulated"
          variant="cyan"
        />

        <SummaryCard
          title={t('dashboard.detectedAnomalies')}
          value={String(summaryData.detected_anomalies).padStart(2, '0')}
          subtitle={t('dashboard.anomalyChangeDesc')}
          icon={AlertTriangle}
          badgeType="demo"
          variant="amber"
        />

        <SummaryCard
          title={t('dashboard.activeWarnings')}
          value={String(summaryData.active_warnings).padStart(2, '0')}
          subtitle={t('dashboard.warningChangeDesc')}
          icon={ShieldAlert}
          badgeType="demo"
          variant="red"
        />
      </section>

      {/* Security Pipeline Flow (SIH Concept Anchor) */}
      <section className="pipeline-section-wrapper">
        <SecurityPipeline />
      </section>

      {/* Attack Forecast Major Card (wired to backend /api/forecast/status) & Risk Overview */}
      <div className="soc-two-col-grid">
        <AttackForecastCard forecastData={forecastData} />
        <RiskOverviewCard />
      </div>

      {/* Network Traffic Telemetry Chart (wired to backend /api/traffic/sample) */}
      <section className="soc-full-width-section">
        <NetworkTrafficChart trafficData={trafficPoints} />
      </section>

      {/* Attack Story Correlation & Early Warning */}
      <div className="soc-two-col-grid">
        <AttackStoryPreview />
        <EarlyWarningCard />
      </div>

      {/* Recommended Actions */}
      <section className="soc-full-width-section">
        <RecommendedActionsCard />
      </section>
    </div>
  );
};

export default DashboardPage;

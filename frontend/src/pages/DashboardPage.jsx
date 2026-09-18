import React from 'react';
import { Activity, Globe, ShieldAlert, AlertTriangle } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import SummaryCard from '../components/dashboard/SummaryCard';
import SecurityPipeline from '../components/dashboard/SecurityPipeline';
import AttackForecastCard from '../components/dashboard/AttackForecastCard';
import NetworkTrafficChart from '../components/dashboard/NetworkTrafficChart';
import RiskOverviewCard from '../components/dashboard/RiskOverviewCard';
import AttackStoryPreview from '../components/dashboard/AttackStoryPreview';
import EarlyWarningCard from '../components/dashboard/EarlyWarningCard';
import RecommendedActionsCard from '../components/dashboard/RecommendedActionsCard';

export const DashboardPage = () => {
  const { t } = useLanguage();

  return (
    <div className="soc-page dashboard-page">
      {/* 4 Primary Summary Cards */}
      <section className="summary-cards-grid" aria-label="Security Metrics Summary">
        <SummaryCard
          title={t('dashboard.networkStatus')}
          value={t('dashboard.networkStatusVal')}
          subtitle={t('dashboard.trafficVolumeDesc')}
          icon={Globe}
          badgeType="demo"
          variant="green"
        />

        <SummaryCard
          title={t('dashboard.activeConnections')}
          value={t('dashboard.activeConnectionsVal')}
          subtitle={t('traffic.liveFlowIndicator')}
          icon={Activity}
          badgeType="simulated"
          variant="cyan"
        />

        <SummaryCard
          title={t('dashboard.detectedAnomalies')}
          value={t('dashboard.detectedAnomaliesVal')}
          subtitle={t('dashboard.anomalyChangeDesc')}
          icon={AlertTriangle}
          badgeType="demo"
          variant="amber"
        />

        <SummaryCard
          title={t('dashboard.activeWarnings')}
          value={t('dashboard.activeWarningsVal')}
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

      {/* Attack Forecast Major Card & Risk Overview */}
      <div className="soc-two-col-grid">
        <AttackForecastCard />
        <RiskOverviewCard />
      </div>

      {/* Network Traffic Telemetry Chart */}
      <section className="soc-full-width-section">
        <NetworkTrafficChart />
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


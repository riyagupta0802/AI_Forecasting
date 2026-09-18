import React, { useState, useEffect, useCallback } from 'react';
import { Server, Cpu, Database, Layout, RefreshCw, CheckCircle2, XCircle, Info, Activity } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import StatusBadge from '../components/StatusBadge';
import DemoBadge from '../components/common/DemoBadge';
import apiService from '../services/api';

export const SystemStatusPage = () => {
  const { t } = useLanguage();
  const [backendHealth, setBackendHealth] = useState(null);
  const [systemData, setSystemData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const probeBackend = useCallback(async () => {
    setIsLoading(true);
    const [healthRes, sysRes] = await Promise.all([
      apiService.checkHealth(),
      apiService.getSystemStatus(),
    ]);
    setBackendHealth(healthRes);
    if (sysRes.ok && sysRes.data) {
      setSystemData(sysRes.data);
    }
    setIsLoading(false);
  }, []);

  useEffect(() => {
    probeBackend();
  }, [probeBackend]);

  const isBackendOk = backendHealth?.ok;

  const components = [
    {
      id: 'frontend',
      name: t('systemStatus.compFrontend'),
      status: t('systemStatus.compFrontendVal'),
      statusVariant: 'connected',
      desc: t('systemStatus.compFrontendDesc'),
      icon: Layout,
      metric: 'Port 5173 (Vite SPA)',
    },
    {
      id: 'backend',
      name: t('systemStatus.compBackend'),
      status: isBackendOk ? t('systemStatus.compBackendConnected') : t('systemStatus.compBackendDisconnected'),
      statusVariant: isBackendOk ? 'connected' : 'disconnected',
      desc: t('systemStatus.compBackendDesc'),
      icon: Server,
      metric: backendHealth ? `Latency: ${backendHealth.latencyMs}ms (${apiService.getBaseUrl()}/health)` : 'Pinging...',
      isLive: true,
    },
    {
      id: 'mlEngine',
      name: t('systemStatus.compMlEngine'),
      status: t('systemStatus.compMlEngineVal'),
      statusVariant: 'phase',
      desc: t('systemStatus.compMlEngineDesc'),
      icon: Cpu,
      metric: 'PyTorch / XGBoost (Phase 3)',
    },
    {
      id: 'database',
      name: t('systemStatus.compDatabase'),
      status: t('systemStatus.compDatabaseVal'),
      statusVariant: 'phase',
      desc: t('systemStatus.compDatabaseDesc'),
      icon: Database,
      metric: 'Async Motor Client (Phase 5)',
    },
    {
      id: 'forecasting',
      name: t('systemStatus.compForecasting'),
      status: t('systemStatus.compForecastingVal'),
      statusVariant: 'phase',
      desc: t('systemStatus.compForecastingDesc'),
      icon: Activity,
      metric: 'Temporal LSTM Attention (Phase 4)',
    },
  ];

  return (
    <div className="soc-page system-status-page">
      {/* Prototype Disclosure Banner */}
      <div className="soc-card system-status-banner">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Info size={20} className="accent-cyan-icon" />
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            {t('systemStatus.prototypeDisclosure')}
          </p>
        </div>
        <button
          type="button"
          className="btn-recheck"
          onClick={probeBackend}
          disabled={isLoading}
        >
          <RefreshCw size={14} className={isLoading ? 'pulse-dot' : ''} />
          {isLoading ? t('status.checking') : t('systemStatus.recheckButton')}
        </button>
      </div>

      {/* Component Status Cards Grid */}
      <div className="system-components-grid">
        {components.map((comp) => {
          const Icon = comp.icon;
          return (
            <div key={comp.id} className="soc-card system-component-card">
              <div className="comp-card-top">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div className="comp-icon-box">
                    <Icon size={20} />
                  </div>
                  <div>
                    <h4 className="comp-name">{comp.name}</h4>
                    <span className="comp-metric">{comp.metric}</span>
                  </div>
                </div>

                <StatusBadge
                  variant={comp.statusVariant}
                  text={comp.status}
                  icon={comp.isLive ? (isBackendOk ? CheckCircle2 : XCircle) : undefined}
                />
              </div>

              <p className="comp-desc">{comp.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SystemStatusPage;


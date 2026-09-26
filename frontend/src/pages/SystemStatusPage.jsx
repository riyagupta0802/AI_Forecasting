import React, { useState, useEffect, useCallback } from 'react';
import {
  Server,
  Cpu,
  Database,
  Layout,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Info,
  Activity,
  Layers,
  ShieldCheck,
  TrendingUp,
  Clock,
  FileText,
  AlertTriangle,
  ShieldAlert,
  Brain,
} from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import StatusBadge from '../components/StatusBadge';
import apiService from '../services/api';

const COMPONENT_ICONS = {
  frontend: Layout,
  backend: Server,
  preprocessing: Layers,
  phase5_attack_detection: ShieldCheck,
  phase6_forecasting: TrendingUp,
  phase7_escalation: Clock,
  phase8_attack_story: FileText,
  phase9_early_warning: AlertTriangle,
  phase10_recommendations: ShieldAlert,
  phase11_xai: Brain,
  database: Database,
};

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

  // Build dynamic components list from live backend response or fallback
  let displayComponents = [];
  if (systemData?.components && Object.keys(systemData.components).length > 0) {
    displayComponents = Object.values(systemData.components).map((comp) => {
      let variant = 'disconnected';
      if (comp.status === 'ONLINE' || comp.status === 'READY') {
        variant = 'connected';
      } else if (comp.status === 'PREPARED') {
        variant = 'phase';
      }

      return {
        id: comp.id,
        name: comp.name,
        status: comp.status,
        statusVariant: variant,
        desc: comp.details,
        icon: COMPONENT_ICONS[comp.id] || Cpu,
        metric: comp.metric,
        phase: comp.phase,
        isLive: comp.id === 'backend',
      };
    });
  } else {
    // Graceful offline fallback
    displayComponents = [
      {
        id: 'frontend',
        name: t('systemStatus.compFrontend'),
        status: 'ONLINE',
        statusVariant: 'connected',
        desc: t('systemStatus.compFrontendDesc'),
        icon: Layout,
        metric: 'Port 5173 (Vite Proxy)',
        phase: 'Phase 2',
      },
      {
        id: 'backend',
        name: t('systemStatus.compBackend'),
        status: isBackendOk ? 'ONLINE' : 'DISCONNECTED',
        statusVariant: isBackendOk ? 'connected' : 'disconnected',
        desc: isBackendOk ? 'FastAPI Gateway active on port 8000' : 'Backend offline — start uvicorn on port 8000',
        icon: Server,
        metric: backendHealth ? `Latency: ${backendHealth.latencyMs}ms (/api/health)` : 'Pinging port 8000...',
        phase: 'Phase 3',
        isLive: true,
      },
      {
        id: 'preprocessing',
        name: 'Phase 4 Preprocessing Pipeline',
        status: isBackendOk ? 'READY' : 'NOT AVAILABLE',
        statusVariant: isBackendOk ? 'connected' : 'disconnected',
        desc: 'StandardScaler feature normalization and 78-feature matrix alignment',
        icon: Layers,
        metric: '78 Features Normalization Vector',
        phase: 'Phase 4',
      },
      {
        id: 'phase5_attack_detection',
        name: 'Phase 5 AI Attack Classifier',
        status: isBackendOk ? 'ONLINE' : 'NOT AVAILABLE',
        statusVariant: isBackendOk ? 'connected' : 'disconnected',
        desc: 'Random Forest binary classifier for attack anomaly detection',
        icon: ShieldCheck,
        metric: 'Random Forest (100 Trees, 99.0% Accuracy)',
        phase: 'Phase 5',
      },
      {
        id: 'phase6_forecasting',
        name: 'Phase 6 Attack Forecasting Engine',
        status: isBackendOk ? 'ONLINE' : 'NOT AVAILABLE',
        statusVariant: isBackendOk ? 'connected' : 'disconnected',
        desc: 'Multi-Class Stage Classifier + Empirical Kill Chain Transition Dynamics',
        icon: TrendingUp,
        metric: 'Stage Classifier (98.0% Accuracy)',
        phase: 'Phase 6',
      },
      {
        id: 'phase7_escalation',
        name: 'Phase 7 Time-to-Escalation Engine',
        status: isBackendOk ? 'ONLINE' : 'NOT AVAILABLE',
        statusVariant: isBackendOk ? 'connected' : 'disconnected',
        desc: 'Velocity-calibrated regression model estimating threat window duration',
        icon: Clock,
        metric: 'Random Forest Regressor (MAE: 8.38s, R²: 0.9566)',
        phase: 'Phase 7',
      },
      {
        id: 'phase8_attack_story',
        name: 'Phase 8 Attack Story Engine',
        status: isBackendOk ? 'ONLINE' : 'NOT AVAILABLE',
        statusVariant: isBackendOk ? 'connected' : 'disconnected',
        desc: 'Event correlation engine answering 5 SOC incident questions',
        icon: FileText,
        metric: 'Event Correlation & Timeline',
        phase: 'Phase 8',
      },
      {
        id: 'phase9_early_warning',
        name: 'Phase 9 Early Warning Engine',
        status: isBackendOk ? 'ONLINE' : 'NOT AVAILABLE',
        statusVariant: isBackendOk ? 'connected' : 'disconnected',
        desc: 'Multi-source evidence rule engine with deterministic decision matrix',
        icon: AlertTriangle,
        metric: 'Evidence Rule Matrix',
        phase: 'Phase 9',
      },
      {
        id: 'phase10_recommendations',
        name: 'Phase 10 Recommendation Engine',
        status: isBackendOk ? 'ONLINE' : 'NOT AVAILABLE',
        statusVariant: isBackendOk ? 'connected' : 'disconnected',
        desc: 'Prescriptive mitigation playbooks with operator lifecycle management',
        icon: ShieldAlert,
        metric: 'Defensive Playbooks Engine',
        phase: 'Phase 10',
      },
      {
        id: 'phase11_xai',
        name: 'Phase 11 Explainable AI (SHAP)',
        status: isBackendOk ? 'ONLINE' : 'NOT AVAILABLE',
        statusVariant: isBackendOk ? 'connected' : 'disconnected',
        desc: 'TreeExplainer mathematical feature attribution calculating Shapley values',
        icon: Brain,
        metric: 'SHAP TreeExplainer',
        phase: 'Phase 11',
      },
      {
        id: 'database',
        name: 'MongoDB Telemetry Store',
        status: 'PREPARED',
        statusVariant: 'phase',
        desc: 'MongoDB driver configured in local in-memory/stub mode; persistent DB optional for local prototype',
        icon: Database,
        metric: 'In-Memory Stub Mode',
        phase: 'Phase 1',
      },
    ];
  }

  return (
    <div className="soc-page system-status-page">
      {/* Verification Disclosure Banner */}
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
        {displayComponents.map((comp) => {
          const Icon = comp.icon;
          return (
            <div key={comp.id} className="soc-card system-component-card">
              <div className="comp-card-top">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div className="comp-icon-box">
                    <Icon size={20} />
                  </div>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <h4 className="comp-name">{comp.name}</h4>
                      {comp.phase && (
                        <span
                          style={{
                            fontSize: '0.68rem',
                            fontWeight: 600,
                            padding: '0.1rem 0.4rem',
                            borderRadius: '4px',
                            background: 'rgba(255, 255, 255, 0.06)',
                            color: 'var(--text-muted)',
                          }}
                        >
                          {comp.phase}
                        </span>
                      )}
                    </div>
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

import React from 'react';
import { Activity, ShieldCheck, AlertTriangle, ArrowUpDown, Filter } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import NetworkTrafficChart from '../components/dashboard/NetworkTrafficChart';
import DatasetStatusCard from '../components/dashboard/DatasetStatusCard';
import DemoBadge from '../components/common/DemoBadge';

export const NetworkTrafficPage = () => {
  const { t } = useLanguage();

  const recentFlows = [
    {
      id: 1,
      time: '10:24:12',
      src: '192.168.1.104',
      dst: '10.0.0.5',
      proto: 'TCP',
      port: '443',
      flags: 'SYN, ACK',
      status: t('traffic.statusNormal'),
      isAnomaly: false,
    },
    {
      id: 2,
      time: '10:24:08',
      src: '45.134.20.12',
      dst: '10.0.0.82',
      proto: 'TCP',
      port: '3306',
      flags: 'SYN',
      status: t('traffic.statusSuspicious'),
      isAnomaly: true,
    },
    {
      id: 3,
      time: '10:23:59',
      src: '192.168.1.45',
      dst: '10.0.0.12',
      proto: 'UDP',
      port: '53',
      flags: '—',
      status: t('traffic.statusNormal'),
      isAnomaly: false,
    },
    {
      id: 4,
      time: '10:23:45',
      src: '185.220.101.5',
      dst: '10.0.0.1',
      proto: 'TCP',
      port: '22',
      flags: 'SYN, FIN',
      status: t('traffic.statusAnomaly'),
      isAnomaly: true,
    },
    {
      id: 5,
      time: '10:23:30',
      src: '192.168.1.200',
      dst: '10.0.0.24',
      proto: 'TCP',
      port: '8080',
      flags: 'ACK, PSH',
      status: t('traffic.statusNormal'),
      isAnomaly: false,
    },
  ];

  const protocols = [
    { name: 'TCP', percent: 64, color: 'var(--accent-cyan)' },
    { name: 'UDP', percent: 26, color: 'var(--accent-blue)' },
    { name: 'ICMP', percent: 7, color: 'var(--accent-indigo)' },
    { name: 'Other', percent: 3, color: 'var(--text-muted)' },
  ];

  return (
    <div className="soc-page network-traffic-page">
      {/* Benchmark Dataset & Preprocessing Pipeline Status (Phase 4) */}
      <DatasetStatusCard />

      {/* Primary Telemetry Chart with Demo Labels */}
      <NetworkTrafficChart showControls={true} />

      {/* Protocol Breakdown & Traffic Distributions */}
      <div className="soc-card protocol-distribution-card">
        <div className="soc-card-header">
          <div className="soc-card-title-group">
            <h3 className="soc-card-title">{t('traffic.protocols')}</h3>
            <p className="soc-card-sub">{t('traffic.liveFlowIndicator')}</p>
          </div>
          <DemoBadge type="simulated" />
        </div>

        <div className="protocol-stacked-bar">
          {protocols.map((p) => (
            <div
              key={p.name}
              className="protocol-segment"
              style={{ width: `${p.percent}%`, backgroundColor: p.color }}
              title={`${p.name}: ${p.percent}%`}
            />
          ))}
        </div>

        <div className="protocol-legend-row">
          {protocols.map((p) => (
            <div key={p.name} className="proto-legend-item">
              <span className="proto-dot" style={{ backgroundColor: p.color }} />
              <span className="proto-name">{p.name}</span>
              <span className="proto-pct">{p.percent}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity Table */}
      <div className="soc-card table-card">
        <div className="soc-card-header">
          <div className="soc-card-title-group">
            <h3 className="soc-card-title">{t('traffic.recentActivity')}</h3>
            <p className="soc-card-sub">{t('traffic.demoData')}</p>
          </div>
          <DemoBadge type="demo" />
        </div>

        <div className="table-responsive-wrapper">
          <table className="soc-data-table">
            <thead>
              <tr>
                <th>{t('traffic.colTimestamp')}</th>
                <th>{t('traffic.colSource')}</th>
                <th>{t('traffic.colDest')}</th>
                <th>{t('traffic.colProtocol')}</th>
                <th>{t('traffic.colPort')}</th>
                <th>{t('traffic.colFlags')}</th>
                <th>{t('traffic.colStatus')}</th>
              </tr>
            </thead>
            <tbody>
              {recentFlows.map((flow) => (
                <tr key={flow.id} className={flow.isAnomaly ? 'row-anomaly' : ''}>
                  <td className="font-mono">{flow.time}</td>
                  <td className="font-mono text-cyan">{flow.src}</td>
                  <td className="font-mono">{flow.dst}</td>
                  <td>
                    <span className="proto-badge">{flow.proto}</span>
                  </td>
                  <td className="font-mono">{flow.port}</td>
                  <td className="font-mono text-muted">{flow.flags}</td>
                  <td>
                    <span className={`status-pill ${flow.isAnomaly ? 'pill-anomaly' : 'pill-normal'}`}>
                      {flow.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default NetworkTrafficPage;


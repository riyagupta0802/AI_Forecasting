import React from 'react';
import { GitMerge, Clock, ArrowRight, Share2, ShieldAlert } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import AttackStoryPreview from '../components/dashboard/AttackStoryPreview';
import DemoBadge from '../components/common/DemoBadge';

export const AttackStoryPage = () => {
  const { t } = useLanguage();

  const correlationNodes = [
    {
      id: 'N1',
      label: t('story.node1'),
      time: '10:14 UTC',
      severity: 'Low',
      proto: 'TCP 80/443',
      color: 'var(--accent-blue)',
    },
    {
      id: 'N2',
      label: t('story.node2'),
      time: '10:18 UTC',
      severity: 'Medium',
      proto: 'TCP 3306, 5432',
      color: 'var(--accent-cyan)',
    },
    {
      id: 'N3',
      label: t('story.node3'),
      time: '10:21 UTC',
      severity: 'High',
      proto: 'POST /auth/login',
      color: 'var(--accent-amber)',
    },
    {
      id: 'N4',
      label: t('story.node4'),
      time: '~10:32 UTC (Est.)',
      severity: 'Forecast',
      proto: 'SMB/RPC Internal',
      color: 'var(--accent-red)',
      isForecast: true,
    },
  ];

  return (
    <div className="soc-page attack-story-page">
      {/* Primary Timeline View */}
      <AttackStoryPreview showCorrelationGraph={false} />

      {/* Deep Event Graph Correlation Diagram */}
      <div className="soc-card graph-correlation-card">
        <div className="soc-card-header">
          <div className="soc-card-title-group">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <Share2 size={20} className="accent-indigo-icon" />
              <h3 className="soc-card-title">{t('story.correlationGraph')}</h3>
            </div>
            <p className="soc-card-sub">{t('story.pageSubtitle')}</p>
          </div>
          <DemoBadge type="conceptPreview" />
        </div>

        <div className="graph-nodes-flow-container">
          {correlationNodes.map((node, idx) => (
            <React.Fragment key={node.id}>
              <div className={`correlation-node-card ${node.isForecast ? 'node-forecast-glow' : ''}`}>
                <div className="cnode-top">
                  <span className="cnode-id">{node.id}</span>
                  <span className={`cnode-severity ${node.isForecast ? 'sev-forecast' : ''}`}>
                    {node.severity}
                  </span>
                </div>
                <h4 className="cnode-label">{node.label}</h4>
                <div className="cnode-meta">
                  <span className="cnode-proto">{node.proto}</span>
                  <span className="cnode-time">
                    <Clock size={12} />
                    {node.time}
                  </span>
                </div>
              </div>

              {idx < correlationNodes.length - 1 && (
                <div className="cnode-link" aria-label="Causality link">
                  <span className="clink-label">{t('story.relationshipLabel')}</span>
                  <div className="clink-arrow-line">
                    <ArrowRight size={18} />
                  </div>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>

        <div className="graph-footer-banner">
          <ShieldAlert size={16} />
          <span>{t('story.correlationDisclaimer')}</span>
        </div>
      </div>
    </div>
  );
};

export default AttackStoryPage;


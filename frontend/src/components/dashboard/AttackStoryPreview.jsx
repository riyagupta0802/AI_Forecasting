import React from 'react';
import { GitMerge, Clock, ArrowDown, ShieldAlert, Cpu } from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';
import DemoBadge from '../common/DemoBadge';

export const AttackStoryPreview = ({ showCorrelationGraph = true }) => {
  const { t } = useLanguage();

  const events = [
    {
      id: 1,
      title: t('story.event1Title'),
      desc: t('story.event1Desc'),
      time: t('story.event1Time'),
      severity: 'Low',
      badgeClass: 'badge-low',
    },
    {
      id: 2,
      title: t('story.event2Title'),
      desc: t('story.event2Desc'),
      time: t('story.event2Time'),
      severity: 'Medium',
      badgeClass: 'badge-med',
    },
    {
      id: 3,
      title: t('story.event3Title'),
      desc: t('story.event3Desc'),
      time: t('story.event3Time'),
      severity: 'High',
      badgeClass: 'badge-high',
    },
    {
      id: 4,
      title: t('story.event4Title'),
      desc: t('story.event4Desc'),
      time: t('story.event4Time'),
      severity: 'Forecast',
      badgeClass: 'badge-forecast',
      isForecast: true,
    },
  ];

  return (
    <div className="soc-card attack-story-card">
      <div className="soc-card-header">
        <div className="soc-card-title-group">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <GitMerge size={20} className="accent-indigo-icon" />
            <h3 className="soc-card-title">{t('story.title')}</h3>
          </div>
          <p className="soc-card-sub">{t('story.conceptPreview')}</p>
        </div>
        <DemoBadge type="conceptPreview" />
      </div>

      <div className="story-disclaimer-banner">
        <Cpu size={16} />
        <span>{t('story.correlationDisclaimer')}</span>
      </div>

      {/* Timeline sequence */}
      <div className="story-timeline-container">
        {events.map((event, idx) => (
          <div key={event.id} className="story-timeline-item">
            <div className="story-timeline-rail">
              <span className={`story-rail-node ${event.isForecast ? 'rail-node-forecast' : ''}`}>
                0{event.id}
              </span>
              {idx < events.length - 1 && <span className="story-rail-line" />}
            </div>

            <div className={`story-event-card ${event.isForecast ? 'event-forecast-card' : ''}`}>
              <div className="story-event-top">
                <h4 className="story-event-title">{event.title}</h4>
                <div className="story-event-meta">
                  <span className={`story-severity-tag ${event.badgeClass}`}>{event.severity}</span>
                  <span className="story-event-time">
                    <Clock size={12} />
                    {event.time}
                  </span>
                </div>
              </div>
              <p className="story-event-desc">{event.desc}</p>
            </div>
          </div>
        ))}
      </div>

      {showCorrelationGraph && (
        <div className="story-graph-preview">
          <span className="graph-preview-title">{t('story.correlationGraph')}</span>
          <div className="graph-nodes-row">
            <span className="graph-node-chip chip-observed">{t('story.node1')}</span>
            <span className="graph-chip-arrow">→</span>
            <span className="graph-node-chip chip-observed">{t('story.node2')}</span>
            <span className="graph-chip-arrow">→</span>
            <span className="graph-node-chip chip-warning">{t('story.node3')}</span>
            <span className="graph-chip-arrow">→</span>
            <span className="graph-node-chip chip-forecast">{t('story.node4')}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AttackStoryPreview;


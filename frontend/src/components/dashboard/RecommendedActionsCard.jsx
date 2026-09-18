import React from 'react';
import { ShieldCheck, Eye, Search, Lock, Network, Info } from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';
import DemoBadge from '../common/DemoBadge';

export const RecommendedActionsCard = () => {
  const { t } = useLanguage();

  const actions = [
    {
      id: 1,
      title: t('recommendations.act1Title'),
      desc: t('recommendations.act1Desc'),
      category: t('recommendations.categoryMonitor'),
      priority: t('recommendations.act1Priority'),
      asset: t('recommendations.act1Asset'),
      icon: Eye,
      priorityClass: 'priority-high',
    },
    {
      id: 2,
      title: t('recommendations.act2Title'),
      desc: t('recommendations.act2Desc'),
      category: t('recommendations.categoryInvestigate'),
      priority: t('recommendations.act2Priority'),
      asset: t('recommendations.act2Asset'),
      icon: Search,
      priorityClass: 'priority-med',
    },
    {
      id: 3,
      title: t('recommendations.act3Title'),
      desc: t('recommendations.act3Desc'),
      category: t('recommendations.categoryContain'),
      priority: t('recommendations.act3Priority'),
      asset: t('recommendations.act3Asset'),
      icon: Lock,
      priorityClass: 'priority-critical',
    },
    {
      id: 4,
      title: t('recommendations.act4Title'),
      desc: t('recommendations.act4Desc'),
      category: t('recommendations.categoryInvestigate'),
      priority: t('recommendations.act4Priority'),
      asset: t('recommendations.act4Asset'),
      icon: Network,
      priorityClass: 'priority-med',
    },
  ];

  return (
    <div className="soc-card recommended-actions-card">
      <div className="soc-card-header">
        <div className="soc-card-title-group">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <ShieldCheck size={20} className="accent-green-icon" />
            <h3 className="soc-card-title">{t('recommendations.title')}</h3>
          </div>
          <p className="soc-card-sub">{t('recommendations.pageSubtitle')}</p>
        </div>
        <DemoBadge type="prototype" />
      </div>

      <div className="recommendations-banner">
        <Info size={16} />
        <span>{t('recommendations.futureNotice')}</span>
      </div>

      <div className="recommendations-grid">
        {actions.map((act) => {
          const Icon = act.icon;
          return (
            <div key={act.id} className="rec-item-card">
              <div className="rec-item-top">
                <div className="rec-icon-wrap">
                  <Icon size={16} />
                </div>
                <div className="rec-badge-group">
                  <span className={`rec-priority-badge ${act.priorityClass}`}>{act.priority}</span>
                  <span className="rec-category-chip">{act.category}</span>
                </div>
              </div>

              <h4 className="rec-item-title">{act.title}</h4>
              <p className="rec-item-desc">{act.desc}</p>

              <div className="rec-item-footer">
                <span className="rec-target-asset">Asset: {act.asset}</span>
                <span className="rec-simulated-tag">{t('badges.simulated')}</span>
              </div>
            </div>
          );
        })}
      </div>

      <p className="rec-auto-disclaimer">
        {t('recommendations.noAutoActionNotice')}
      </p>
    </div>
  );
};

export default RecommendedActionsCard;


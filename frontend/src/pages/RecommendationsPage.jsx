import React, { useState } from 'react';
import { ShieldCheck, Eye, Search, Lock, AlertOctagon, Info } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import DemoBadge from '../components/common/DemoBadge';

export const RecommendationsPage = () => {
  const { t } = useLanguage();
  const [selectedCategory, setSelectedCategory] = useState('all');

  const recommendationList = [
    {
      id: 1,
      title: t('recommendations.act1Title'),
      desc: t('recommendations.act1Desc'),
      category: 'Monitor',
      categoryLabel: t('recommendations.categoryMonitor'),
      priority: t('recommendations.act1Priority'),
      asset: t('recommendations.act1Asset'),
      icon: Eye,
      priorityClass: 'priority-high',
    },
    {
      id: 2,
      title: t('recommendations.act2Title'),
      desc: t('recommendations.act2Desc'),
      category: 'Investigate',
      categoryLabel: t('recommendations.categoryInvestigate'),
      priority: t('recommendations.act2Priority'),
      asset: t('recommendations.act2Asset'),
      icon: Search,
      priorityClass: 'priority-med',
    },
    {
      id: 3,
      title: t('recommendations.act3Title'),
      desc: t('recommendations.act3Desc'),
      category: 'Contain',
      categoryLabel: t('recommendations.categoryContain'),
      priority: t('recommendations.act3Priority'),
      asset: t('recommendations.act3Asset'),
      icon: Lock,
      priorityClass: 'priority-critical',
    },
    {
      id: 4,
      title: t('recommendations.act4Title'),
      desc: t('recommendations.act4Desc'),
      category: 'Escalate',
      categoryLabel: t('recommendations.categoryEscalate'),
      priority: 'Critical',
      asset: 'SOC-Incident-Bridge',
      icon: AlertOctagon,
      priorityClass: 'priority-critical',
    },
  ];

  const filteredRecs = recommendationList.filter((r) => {
    if (selectedCategory === 'all') return true;
    return r.category.toLowerCase() === selectedCategory.toLowerCase();
  });

  return (
    <div className="soc-page recommendations-page">
      {/* Category Navigation Bar */}
      <div className="soc-card recommendations-filter-bar">
        <div className="rec-cat-pills">
          {[
            { id: 'all', label: 'All Actions' },
            { id: 'monitor', label: t('recommendations.categoryMonitor') },
            { id: 'investigate', label: t('recommendations.categoryInvestigate') },
            { id: 'contain', label: t('recommendations.categoryContain') },
            { id: 'escalate', label: t('recommendations.categoryEscalate') },
          ].map((cat) => (
            <button
              key={cat.id}
              type="button"
              className={`rec-cat-btn ${selectedCategory === cat.id ? 'active' : ''}`}
              onClick={() => setSelectedCategory(cat.id)}
            >
              {cat.label}
            </button>
          ))}
        </div>
        <DemoBadge type="prototype" />
      </div>

      {/* Recommendations Cards Grid */}
      <div className="recommendations-detailed-grid">
        {filteredRecs.map((rec) => {
          const Icon = rec.icon;
          return (
            <div key={rec.id} className="soc-card rec-detail-card">
              <div className="rec-detail-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div className="rec-icon-box">
                    <Icon size={18} />
                  </div>
                  <div>
                    <h4 className="rec-detail-title">{rec.title}</h4>
                    <span className="rec-detail-asset">Target: {rec.asset}</span>
                  </div>
                </div>
                <span className={`rec-priority-badge ${rec.priorityClass}`}>{rec.priority}</span>
              </div>

              <p className="rec-detail-desc">{rec.desc}</p>

              <div className="rec-detail-footer">
                <span className="rec-category-tag">{rec.categoryLabel}</span>
                <span className="rec-demo-disclaimer">{t('badges.simulated')}</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="rec-page-footer-banner">
        <Info size={16} />
        <div>
          <strong>{t('recommendations.futureNotice')}</strong>
          <p>{t('recommendations.noAutoActionNotice')}</p>
        </div>
      </div>
    </div>
  );
};

export default RecommendationsPage;


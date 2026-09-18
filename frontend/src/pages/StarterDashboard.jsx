import React from 'react';
import { ShieldCheck, Zap, Activity, ArrowRight } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import StatusBadge from '../components/StatusBadge';
import BackendStatusCard from '../components/BackendStatusCard';

export const StarterDashboard = () => {
  const { t } = useLanguage();

  const pipelineSteps = [
    {
      number: '01',
      title: t('pipeline.step1Title'),
      desc: t('pipeline.step1Desc'),
    },
    {
      number: '02',
      title: t('pipeline.step2Title'),
      desc: t('pipeline.step2Desc'),
    },
    {
      number: '03',
      title: t('pipeline.step3Title'),
      desc: t('pipeline.step3Desc'),
    },
    {
      number: '04',
      title: t('pipeline.step4Title'),
      desc: t('pipeline.step4Desc'),
    },
    {
      number: '05',
      title: t('pipeline.step5Title'),
      desc: t('pipeline.step5Desc'),
    },
    {
      number: '06',
      title: t('pipeline.step6Title'),
      desc: t('pipeline.step6Desc'),
    },
  ];

  return (
    <div className="starter-dashboard">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-tag-wrap">
          <StatusBadge variant="phase" text={t('brand.hackathonTag')} icon={Zap} />
          <StatusBadge variant="connected" text={t('status.operational')} icon={ShieldCheck} />
        </div>

        <h2 className="hero-title">
          {t('brand.projectName')}
        </h2>

        <p className="hero-subtitle">
          {t('brand.tagline')}
        </p>

        <div className="hero-pills">
          <span className="hero-pill">
            <Activity size={14} />
            {t('hero.networkAttackForecast')}
          </span>
          <span className="hero-pill">
            <Zap size={14} />
            {t('hero.earlyWarning')}
          </span>
          <span className="hero-pill">
            <ShieldCheck size={14} />
            {t('hero.dashboard')}
          </span>
        </div>
      </section>

      {/* Gateway Status Cards */}
      <BackendStatusCard />

      {/* Architecture System Flow Preview */}
      <section className="pipeline-section">
        <div className="section-header">
          <h2>{t('pipeline.title')}</h2>
          <p>{t('pipeline.subtitle')}</p>
        </div>

        <div className="pipeline-flow">
          {pipelineSteps.map((step, idx) => (
            <div key={idx} className="pipeline-step">
              <div className="pipeline-step-num">{step.number}</div>
              <h4>{step.title}</h4>
              <p>{step.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default StarterDashboard;


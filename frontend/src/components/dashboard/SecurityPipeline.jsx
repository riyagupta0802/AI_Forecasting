import React from 'react';
import {
  Radio,
  Activity,
  Layers,
  Cpu,
  Crosshair,
  Clock,
  AlertTriangle,
  ShieldCheck,
  ChevronRight,
} from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';

export const SecurityPipeline = () => {
  const { t } = useLanguage();

  const pipelineSteps = [
    {
      id: 1,
      name: t('pipeline.step1'),
      desc: t('pipeline.step1Desc'),
      icon: Radio,
      accent: '#00F0FF',
    },
    {
      id: 2,
      name: t('pipeline.step2'),
      desc: t('pipeline.step2Desc'),
      icon: Activity,
      accent: '#38BDF8',
    },
    {
      id: 3,
      name: t('pipeline.step3'),
      desc: t('pipeline.step3Desc'),
      icon: Layers,
      accent: '#60A5FA',
    },
    {
      id: 4,
      name: t('pipeline.step4'),
      desc: t('pipeline.step4Desc'),
      icon: Cpu,
      accent: '#818CF8',
    },
    {
      id: 5,
      name: t('pipeline.step5'),
      desc: t('pipeline.step5Desc'),
      icon: Crosshair,
      accent: '#F59E0B',
    },
    {
      id: 6,
      name: t('pipeline.step6'),
      desc: t('pipeline.step6Desc'),
      icon: Clock,
      accent: '#FB923C',
    },
    {
      id: 7,
      name: t('pipeline.step7'),
      desc: t('pipeline.step7Desc'),
      icon: AlertTriangle,
      accent: '#F87171',
    },
    {
      id: 8,
      name: t('pipeline.step8'),
      desc: t('pipeline.step8Desc'),
      icon: ShieldCheck,
      accent: '#34D399',
    },
  ];

  return (
    <div className="soc-pipeline-container" aria-label="AI Forecasting Pipeline">
      <div className="soc-pipeline-header">
        <div className="soc-pipeline-title-wrap">
          <span className="soc-pipeline-badge">SIH26153 FLOW</span>
          <h3 className="soc-pipeline-heading">{t('pipeline.title')}</h3>
          <p className="soc-pipeline-sub">{t('pipeline.subtitle')}</p>
        </div>
      </div>

      <div className="soc-pipeline-track">
        {pipelineSteps.map((step, index) => {
          const Icon = step.icon;
          const isLast = index === pipelineSteps.length - 1;

          return (
            <React.Fragment key={step.id}>
              <div className="soc-pipeline-node" style={{ '--node-accent': step.accent }}>
                <div className="soc-pipeline-icon-circle">
                  <Icon size={18} />
                  <span className="soc-pipeline-step-num">0{step.id}</span>
                </div>
                <div className="soc-pipeline-node-info">
                  <h4 className="soc-pipeline-node-name">{step.name}</h4>
                  <p className="soc-pipeline-node-desc">{step.desc}</p>
                </div>
              </div>

              {!isLast && (
                <div className="soc-pipeline-connector" aria-hidden="true">
                  <ChevronRight size={16} className="connector-arrow" />
                  <span className="connector-line" />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

export default SecurityPipeline;


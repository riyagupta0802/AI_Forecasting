import React, { useState } from 'react';
import { Activity, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';
import DemoBadge from '../common/DemoBadge';

export const NetworkTrafficChart = ({ showControls = true, trafficData = null }) => {
  const { t } = useLanguage();
  const [timeRange, setTimeRange] = useState('1h');

  // If trafficData is provided from API (/api/traffic/sample), dynamically construct points
  let normalPoints = "0,140 25,135 50,145 75,120 100,125 125,110 150,115 175,130 200,105 225,100 250,110 275,120 300,95 325,105 350,90 375,100 400,115 425,110 450,125 475,120 500,105 525,115 550,110 575,120 600,115";
  let normalArea = "0,140 25,135 50,145 75,120 100,125 125,110 150,115 175,130 200,105 225,100 250,110 275,120 300,95 325,105 350,90 375,100 400,115 425,110 450,125 475,120 500,105 525,115 550,110 575,120 600,115 600,200 0,200";

  if (Array.isArray(trafficData) && trafficData.length > 1) {
    const maxVal = Math.max(...trafficData.map(d => d.traffic), 350);
    const minVal = Math.min(...trafficData.map(d => d.traffic), 80);
    const range = Math.max(maxVal - minVal, 1);

    const pts = trafficData.map((d, i) => {
      const x = Math.round((i / (trafficData.length - 1)) * 600);
      const normalized = (d.traffic - minVal) / range;
      const y = Math.round(165 - normalized * 110);
      return `${x},${y}`;
    });

    normalPoints = pts.join(' ');
    normalArea = `${pts.join(' ')} 600,200 0,200`;
  }

  // Suspicious anomaly spikes (Demo Overlay)
  const anomalyPoints = "0,170 120,165 150,155 200,75 225,35 250,120 320,160 375,55 400,140 480,160 520,60 550,135 600,170";

  return (
    <div className="soc-card network-traffic-chart-card">
      <div className="soc-card-header">
        <div className="soc-card-title-group">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Activity size={20} className="accent-blue-icon" />
            <h3 className="soc-card-title">{t('traffic.title')}</h3>
          </div>
          <p className="soc-card-sub">{t('traffic.pageSubtitle')}</p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <DemoBadge type="demo" />
          {showControls && (
            <div className="chart-time-selector" role="group" aria-label="Time Range">
              {['1h', '6h', '24h'].map((range) => (
                <button
                  key={range}
                  type="button"
                  className={`chart-time-btn ${timeRange === range ? 'active' : ''}`}
                  onClick={() => setTimeRange(range)}
                >
                  {range === '1h' ? t('traffic.time1h') : range === '6h' ? t('traffic.time6h') : t('traffic.time24h')}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Metrics Bar */}
      <div className="traffic-quick-metrics">
        <div className="tq-item">
          <span className="tq-label">{t('traffic.packetsPerSec')}</span>
          <span className="tq-val">12,480 / s</span>
          <DemoBadge type="simulated" size="small" />
        </div>
        <div className="tq-item">
          <span className="tq-label">{t('traffic.throughput')}</span>
          <span className="tq-val">42.6 MB/s</span>
          <DemoBadge type="simulated" size="small" />
        </div>
        <div className="tq-item">
          <span className="tq-label">{t('traffic.inboundOutbound')}</span>
          <span className="tq-val">68% / 32%</span>
          <DemoBadge type="simulated" size="small" />
        </div>
        <div className="tq-item">
          <span className="tq-label">{t('traffic.activeFlows')}</span>
          <span className="tq-val">1,248</span>
          <DemoBadge type="simulated" size="small" />
        </div>
      </div>

      {/* SVG Telemetry Chart */}
      <div className="traffic-svg-wrapper">
        <svg viewBox="0 0 600 200" className="traffic-svg-chart" preserveAspectRatio="none">
          <defs>
            <linearGradient id="normalFillGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="#00F0FF" stopOpacity="0.25" />
              <stop offset="100%" stopColor="#00F0FF" stopOpacity="0.0" />
            </linearGradient>
            <linearGradient id="normalLineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#00F0FF" />
              <stop offset="50%" stopColor="#38BDF8" />
              <stop offset="100%" stopColor="#6366F1" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          <line x1="0" y1="50" x2="600" y2="50" stroke="#1E2E4E" strokeDasharray="4 4" strokeWidth="1" />
          <line x1="0" y1="100" x2="600" y2="100" stroke="#1E2E4E" strokeDasharray="4 4" strokeWidth="1" />
          <line x1="0" y1="150" x2="600" y2="150" stroke="#1E2E4E" strokeDasharray="4 4" strokeWidth="1" />

          {/* Normal traffic area fill */}
          <polygon points={normalArea} fill="url(#normalFillGrad)" />

          {/* Normal traffic baseline stroke */}
          <polyline
            points={normalPoints}
            fill="none"
            stroke="url(#normalLineGrad)"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Suspicious spike polyline */}
          <polyline
            points={anomalyPoints}
            fill="none"
            stroke="#EF4444"
            strokeWidth="2"
            strokeDasharray="6 3"
            strokeLinecap="round"
            opacity="0.85"
          />

          {/* Spike markers */}
          <circle cx="225" cy="35" r="4" fill="#EF4444" stroke="#070B14" strokeWidth="2" />
          <circle cx="375" cy="55" r="4" fill="#EF4444" stroke="#070B14" strokeWidth="2" />
          <circle cx="520" cy="60" r="4" fill="#EF4444" stroke="#070B14" strokeWidth="2" />
        </svg>

        {/* Legend */}
        <div className="chart-legend-row">
          <div className="legend-item">
            <span className="legend-marker marker-normal" />
            <span>{t('traffic.normalBehavior')}</span>
          </div>
          <div className="legend-item">
            <span className="legend-marker marker-anomaly" />
            <span>{t('traffic.suspiciousBehavior')}</span>
          </div>
          <div className="legend-item legend-demo-tag">
            <DemoBadge type="demo" size="small" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default NetworkTrafficChart;


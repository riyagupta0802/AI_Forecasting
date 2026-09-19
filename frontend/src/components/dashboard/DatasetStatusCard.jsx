import React, { useState, useEffect } from 'react';
import { Database, RefreshCw, Layers, CheckCircle, AlertCircle, Info, Sparkles } from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';
import DemoBadge from '../common/DemoBadge';
import apiService from '../../services/api';

/**
 * DatasetStatusCard - Phase 4 Component
 * Displays benchmark dataset status, cleaning & preprocessing pipeline results,
 * and maintains explicit distinction between benchmark training data and live telemetry.
 */
export const DatasetStatusCard = () => {
  const { t } = useLanguage();
  const [dataStatus, setDataStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [isLiveApi, setIsLiveApi] = useState(false);

  const fetchStatus = async () => {
    setRefreshing(true);
    try {
      const res = await apiService.getDataStatus();
      if (res.ok && res.data) {
        setDataStatus(res.data);
        setIsLiveApi(true);
      } else {
        // Safe offline demo fallback
        setDataStatus({
          status: 'ready',
          dataset: 'CICIDS2017',
          mode: 'demo',
          records_available: 500,
          preprocessing: 'ready',
          processed_records: 500,
          classes_detected: ['BENIGN', 'Bot', 'DDoS', 'PortScan'],
        });
        setIsLiveApi(false);
      }
    } catch (err) {
      setDataStatus({
        status: 'ready',
        dataset: 'CICIDS2017',
        mode: 'demo',
        records_available: 500,
        preprocessing: 'ready',
        processed_records: 500,
        classes_detected: ['BENIGN', 'Bot', 'DDoS', 'PortScan'],
      });
      setIsLiveApi(false);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const rawCount = dataStatus?.records_available ?? 500;
  const processedCount = dataStatus?.processed_records ?? 500;
  const classes = dataStatus?.classes_detected?.length
    ? dataStatus.classes_detected
    : ['BENIGN', 'Bot', 'DDoS', 'PortScan'];

  return (
    <div className="soc-card dataset-status-card" style={{ marginBottom: '1.25rem' }}>
      <div className="soc-card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div className="soc-card-title-group">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Database size={20} className="accent-cyan-icon" />
            <h3 className="soc-card-title">{t('dataset.title')}</h3>
          </div>
          <p className="soc-card-sub">{t('dataset.subtitle')}</p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <DemoBadge type="sample" />
          <button
            onClick={fetchStatus}
            disabled={refreshing}
            className="soc-btn-secondary"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.35rem',
              padding: '0.35rem 0.75rem',
              fontSize: '0.78rem',
              borderRadius: '6px',
              cursor: refreshing ? 'not-allowed' : 'pointer',
              border: '1px solid var(--border-color)',
              background: 'var(--bg-card)',
              color: 'var(--text-primary)',
            }}
            title={t('dataset.refreshButton')}
          >
            <RefreshCw size={13} className={refreshing ? 'spin-icon' : ''} />
            <span>{refreshing ? t('status.checking') : t('dataset.refreshButton')}</span>
          </button>
        </div>
      </div>

      {/* Dataset Metrics Overview Grid */}
      <div
        className="dataset-metrics-grid"
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
          gap: '0.85rem',
          marginTop: '1rem',
          marginBottom: '1rem',
        }}
      >
        <div className="forecast-metric-box">
          <span className="forecast-metric-label">{t('dataset.datasetName')}</span>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.4rem', marginTop: '0.2rem' }}>
            <span className="forecast-metric-val font-mono" style={{ color: 'var(--accent-cyan)' }}>
              {dataStatus?.dataset || 'CICIDS2017'}
            </span>
          </div>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Flow Benchmark</span>
        </div>

        <div className="forecast-metric-box">
          <span className="forecast-metric-label">{t('dataset.datasetStatus')}</span>
          <div style={{ marginTop: '0.35rem' }}>
            <span className="status-pill pill-normal" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
              <CheckCircle size={12} />
              {t('dataset.statusReady')}
            </span>
          </div>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            {t('dataset.demoTag')}
          </span>
        </div>

        <div className="forecast-metric-box">
          <span className="forecast-metric-label">{t('dataset.processingStatus')}</span>
          <div style={{ marginTop: '0.35rem' }}>
            <span className="status-pill pill-normal" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}>
              <Sparkles size={12} />
              {t('dataset.processingReady')}
            </span>
          </div>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            StandardScaler + LabelEncoder
          </span>
        </div>

        <div className="forecast-metric-box">
          <span className="forecast-metric-label">{t('dataset.mode')}</span>
          <div style={{ marginTop: '0.35rem' }}>
            <DemoBadge type="demo" size="small" />
          </div>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            Isolated from Live Telemetry
          </span>
        </div>

        <div className="forecast-metric-box">
          <span className="forecast-metric-label">{t('dataset.recordsAvailable')}</span>
          <span className="forecast-metric-val font-mono" style={{ marginTop: '0.2rem' }}>
            {rawCount.toLocaleString()}
          </span>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Raw flow records</span>
        </div>

        <div className="forecast-metric-box highlight-box">
          <span className="forecast-metric-label">{t('dataset.processedRecords')}</span>
          <span className="forecast-metric-val font-mono text-cyan" style={{ marginTop: '0.2rem' }}>
            {processedCount.toLocaleString()}
          </span>
          <span style={{ fontSize: '0.72rem', color: 'var(--accent-cyan)' }}>
            78 Clean Features
          </span>
        </div>
      </div>

      {/* Detected Attack Classes Breakdown */}
      <div
        style={{
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '0.75rem 1rem',
          marginBottom: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <span style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {t('dataset.classesDetected')}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {classes.length} distinct traffic classes
          </span>
        </div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {classes.map((clsName) => {
            const isBenign = clsName.toUpperCase() === 'BENIGN';
            return (
              <span
                key={clsName}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  padding: '0.25rem 0.65rem',
                  borderRadius: '4px',
                  fontSize: '0.78rem',
                  fontFamily: 'monospace',
                  background: isBenign ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                  color: isBenign ? 'var(--accent-emerald, #10b981)' : 'var(--accent-rose, #f43f5e)',
                  border: `1px solid ${isBenign ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                }}
              >
                <span
                  style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: isBenign ? '#10b981' : '#f43f5e',
                  }}
                />
                {clsName}
              </span>
            );
          })}
        </div>
      </div>

      {/* Explicit Distinction Notice */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: '0.65rem',
          padding: '0.75rem 1rem',
          borderRadius: '6px',
          background: 'rgba(56, 189, 248, 0.06)',
          border: '1px solid rgba(56, 189, 248, 0.2)',
          fontSize: '0.8rem',
          color: 'var(--text-secondary)',
          lineHeight: 1.45,
        }}
      >
        <Info size={16} style={{ color: 'var(--accent-cyan)', flexShrink: 0, marginTop: '2px' }} />
        <span>{t('dataset.distinctionNotice')}</span>
      </div>
    </div>
  );
};

export default DatasetStatusCard;


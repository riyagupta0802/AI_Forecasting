import React, { useState, useEffect, useCallback } from 'react';
import { Server, Activity, CheckCircle2, XCircle, RefreshCw, Cpu } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import StatusBadge from './StatusBadge';
import apiService from '../services/api';

export const BackendStatusCard = () => {
  const { t } = useLanguage();
  const [healthData, setHealthData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const checkStatus = useCallback(async () => {
    setIsLoading(true);
    const result = await apiService.checkHealth();
    setHealthData(result);
    setIsLoading(false);
  }, []);

  useEffect(() => {
    checkStatus();
  }, [checkStatus]);

  const isConnected = healthData?.ok;

  return (
    <div className="cards-grid">
      {/* Backend Status Card */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h3>{t('connectionCard.title')}</h3>
            <p>{t('connectionCard.subtitle')}</p>
          </div>
          <div className="card-icon-wrap">
            <Server size={20} />
          </div>
        </div>

        <div className="data-rows">
          <div className="data-row">
            <span className="data-row-label">{t('connectionCard.endpoint')}</span>
            <span className="data-row-value">{apiService.getBaseUrl()}/health</span>
          </div>

          <div className="data-row">
            <span className="data-row-label">{t('connectionCard.statusLabel')}</span>
            <span>
              {isLoading ? (
                <StatusBadge variant="checking" text={t('status.checking')} icon={RefreshCw} />
              ) : isConnected ? (
                <StatusBadge variant="connected" text={`${healthData?.status} OK`} icon={CheckCircle2} />
              ) : (
                <StatusBadge variant="disconnected" text={t('status.disconnected')} icon={XCircle} />
              )}
            </span>
          </div>

          <div className="data-row">
            <span className="data-row-label">{t('connectionCard.projectLabel')}</span>
            <span className="data-row-value">
              {healthData?.data?.project || '—'}
            </span>
          </div>

          <div className="data-row">
            <span className="data-row-label">{t('connectionCard.latencyLabel')}</span>
            <span className="data-row-value">
              {healthData ? `${healthData.latencyMs} ms` : '—'}
            </span>
          </div>
        </div>

        <p style={{
          fontSize: '0.8rem',
          color: isConnected ? 'var(--accent-green)' : 'var(--accent-amber)',
          marginBottom: '1rem',
          minHeight: '1.2rem'
        }}>
          {isLoading
            ? t('status.checking')
            : isConnected
              ? t('connectionCard.connectedNote')
              : t('connectionCard.disconnectedNote')}
        </p>

        <button
          type="button"
          className="btn-primary"
          onClick={checkStatus}
          disabled={isLoading}
        >
          <RefreshCw size={15} className={isLoading ? 'pulse-dot' : ''} />
          {isLoading ? t('connectionCard.checkingConnection') : t('connectionCard.testConnection')}
        </button>
      </div>

      {/* Frontend Status Card */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h3>{t('connectionCard.frontendCardTitle')}</h3>
            <p>{t('connectionCard.frontendRunning')}</p>
          </div>
          <div className="card-icon-wrap" style={{ background: 'rgba(56, 189, 248, 0.1)', color: 'var(--accent-blue)' }}>
            <Cpu size={20} />
          </div>
        </div>

        <div className="data-rows">
          <div className="data-row">
            <span className="data-row-label">{t('hero.dashboard')}</span>
            <span className="data-row-value"><StatusBadge variant="connected" text={t('status.operational')} icon={Activity} /></span>
          </div>
          <div className="data-row">
            <span className="data-row-label">{t('languageSwitcher.label')}</span>
            <span className="data-row-value">{t('connectionCard.i18nActive')}</span>
          </div>
          <div className="data-row">
            <span className="data-row-label">{t('status.standby')}</span>
            <span className="data-row-value">{t('brand.phaseBadge')}</span>
          </div>
        </div>

        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
          {t('connectionCard.persistenceActive')}
        </p>
      </div>
    </div>
  );
};

export default BackendStatusCard;


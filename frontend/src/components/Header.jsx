import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';
import LanguageSwitcher from './LanguageSwitcher';
import StatusBadge from './StatusBadge';
import hiveLogo from '../assets/hive-logo.svg';

export const Header = () => {
  const { t } = useLanguage();

  return (
    <header className="app-header">
      <div className="app-container">
        <div className="header-inner">
          <div className="brand-section">
            <div className="brand-logo-wrap">
              <img src={hiveLogo} alt="NETORACLE Logo" className="brand-logo" />
            </div>
            <div className="brand-title-wrap">
              <h1>{t('brand.projectName')}</h1>
              <p>{t('brand.tagline')}</p>
            </div>
          </div>

          <div className="header-controls">
            <StatusBadge variant="phase" text={t('brand.phaseBadge')} icon={ShieldAlert} />
            <LanguageSwitcher />
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;


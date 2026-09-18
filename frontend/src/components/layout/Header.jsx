import React from 'react';
import { Bell, Menu, ShieldCheck, User } from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';
import LanguageSwitcher from '../LanguageSwitcher';
import StatusBadge from '../StatusBadge';

export const Header = ({ pageTitle, pageSubtitle, onToggleMobile }) => {
  const { t } = useLanguage();

  return (
    <header className="dashboard-top-header" role="banner">
      <div className="header-left">
        {/* Mobile menu button */}
        <button
          type="button"
          className="mobile-menu-trigger"
          onClick={onToggleMobile}
          aria-label={t('header.openMenu')}
        >
          <Menu size={22} />
        </button>

        {/* Page Context */}
        <div className="header-context">
          <h1 className="header-page-title">{pageTitle}</h1>
          {pageSubtitle && <p className="header-page-sub">{pageSubtitle}</p>}
        </div>
      </div>

      <div className="header-right">
        {/* System Online Status Badge */}
        <div className="header-system-status">
          <StatusBadge
            variant="connected"
            text={t('header.systemOnline')}
            icon={ShieldCheck}
          />
        </div>

        {/* Language selector in top header */}
        <div className="header-lang-wrapper">
          <LanguageSwitcher />
        </div>

        {/* Notification Bell with Simulated Alert Counter */}
        <div className="header-action-btn-wrap">
          <button
            type="button"
            className="header-icon-btn"
            title={t('header.simulatedAlerts')}
            aria-label={t('header.notifications')}
          >
            <Bell size={18} />
            <span className="notification-dot" aria-hidden="true">3</span>
          </button>
        </div>

        {/* User Profile Avatar */}
        <div className="header-profile-avatar" title={t('header.profile')}>
          <User size={18} />
        </div>
      </div>
    </header>
  );
};

export default Header;


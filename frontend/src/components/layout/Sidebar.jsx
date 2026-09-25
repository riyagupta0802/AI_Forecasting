import React from 'react';
import {
  LayoutDashboard,
  Activity,
  TrendingUp,
  GitMerge,
  AlertTriangle,
  ShieldAlert,
  Server,
  Settings,
  User,
  ExternalLink,
} from 'lucide-react';
import { useLanguage } from '../../hooks/useLanguage';
import LanguageSwitcher from '../LanguageSwitcher';
import hiveLogo from '../../assets/hive-logo.svg';

export const Sidebar = ({ activePage, onNavigate, isMobile = false, onCloseMobile }) => {
  const { t } = useLanguage();

  const navItems = [
    { id: 'dashboard', label: t('sidebar.dashboard'), icon: LayoutDashboard },
    { id: 'traffic', label: t('sidebar.networkTraffic'), icon: Activity },
    { id: 'forecast', label: t('sidebar.attackForecast'), icon: TrendingUp },
    { id: 'story', label: t('sidebar.attackStory'), icon: GitMerge },
    { id: 'warnings', label: t('sidebar.earlyWarnings'), icon: AlertTriangle },
    { id: 'recommendations', label: t('sidebar.recommendations'), icon: ShieldAlert },
    { id: 'status', label: t('sidebar.systemStatus'), icon: Server },
  ];

  const handleItemClick = (id) => {
    onNavigate(id);
    if (isMobile && onCloseMobile) {
      onCloseMobile();
    }
  };

  return (
    <aside className={`dashboard-sidebar ${isMobile ? 'mobile-sidebar' : ''}`} aria-label="Main Navigation">
      {/* Brand Header */}
      <div className="sidebar-brand">
        <div className="sidebar-logo-wrap">
          <img src={hiveLogo} alt="NETORACLE Logo" className="sidebar-logo" />
        </div>
        <div className="sidebar-brand-text">
          <span className="sidebar-brand-name">{t('brand.projectName')}</span>
          <span className="sidebar-brand-sub">{t('brand.socLabel')}</span>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="sidebar-nav">
        <div className="sidebar-section-title">{t('sidebar.title')}</div>
        <ul className="sidebar-menu">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <li key={item.id}>
                <button
                  type="button"
                  className={`sidebar-nav-link ${isActive ? 'active' : ''}`}
                  onClick={() => handleItemClick(item.id)}
                  aria-current={isActive ? 'page' : undefined}
                >
                  <Icon size={18} className="sidebar-nav-icon" />
                  <span className="sidebar-nav-label">{item.label}</span>
                  {isActive && <span className="sidebar-active-indicator" />}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Bottom Controls */}
      <div className="sidebar-footer">
        {/* Language selector in sidebar */}
        <div className="sidebar-footer-lang">
          <span className="sidebar-lang-label">{t('languageSwitcher.label')}</span>
          <LanguageSwitcher />
        </div>

        {/* Settings Button */}
        <button
          type="button"
          className={`sidebar-nav-link sidebar-settings-btn ${activePage === 'status' ? 'active' : ''}`}
          onClick={() => handleItemClick('status')}
          title="System & Settings"
        >
          <Settings size={18} className="sidebar-nav-icon" />
          <span className="sidebar-nav-label">{t('sidebar.settings')}</span>
        </button>

        {/* Profile Card Placeholder */}
        <div className="sidebar-profile-card">
          <div className="sidebar-profile-avatar" title="SOC Analyst">
            <User size={18} />
          </div>
          <div className="sidebar-profile-info">
            <span className="sidebar-profile-name">{t('sidebar.profileTitle')}</span>
            <span className="sidebar-profile-role">{t('sidebar.profileRole')}</span>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;


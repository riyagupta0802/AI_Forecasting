import React, { useState } from 'react';
import Sidebar from '../components/layout/Sidebar';
import Header from '../components/layout/Header';
import MobileDrawer from '../components/layout/MobileDrawer';
import { useLanguage } from '../hooks/useLanguage';

export const MainLayout = ({
  activePage,
  onNavigate,
  pageTitle,
  pageSubtitle,
  children,
}) => {
  const { t } = useLanguage();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="soc-dashboard-layout">
      {/* Desktop Persistent Sidebar */}
      <Sidebar
        activePage={activePage}
        onNavigate={onNavigate}
      />

      {/* Mobile Drawer */}
      <MobileDrawer
        isOpen={mobileOpen}
        onClose={() => setMobileOpen(false)}
        activePage={activePage}
        onNavigate={onNavigate}
      />

      {/* Main Viewport Container */}
      <div className="soc-main-viewport">
        <Header
          pageTitle={pageTitle}
          pageSubtitle={pageSubtitle}
          onToggleMobile={() => setMobileOpen(true)}
        />

        <main className="soc-content-area" role="main">
          {children}
        </main>

        <footer className="soc-dashboard-footer">
          <div className="soc-footer-inner">
            <span>{t('footer.copyright')}</span>
            <span>{t('footer.phaseNote')}</span>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default MainLayout;

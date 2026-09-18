import React from 'react';
import Header from '../components/Header';
import { useLanguage } from '../hooks/useLanguage';

export const MainLayout = ({ children }) => {
  const { t } = useLanguage();

  return (
    <div className="app-shell" style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <main style={{ flex: 1 }}>
        <div className="app-container">
          {children}
        </div>
      </main>
      <footer className="app-footer">
        <div className="app-container">
          <div className="footer-inner">
            <span>{t('footer.copyright')}</span>
            <span>{t('footer.phaseNote')}</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default MainLayout;


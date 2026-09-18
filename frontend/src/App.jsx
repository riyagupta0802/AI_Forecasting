import React, { useState } from 'react';
import { LanguageProvider, useLanguage } from './hooks/useLanguage';
import MainLayout from './layouts/MainLayout';
import DashboardPage from './pages/DashboardPage';
import NetworkTrafficPage from './pages/NetworkTrafficPage';
import AttackForecastPage from './pages/AttackForecastPage';
import AttackStoryPage from './pages/AttackStoryPage';
import EarlyWarningsPage from './pages/EarlyWarningsPage';
import RecommendationsPage from './pages/RecommendationsPage';
import SystemStatusPage from './pages/SystemStatusPage';

const AppContent = () => {
  const { t } = useLanguage();
  const [currentPage, setCurrentPage] = useState('dashboard');

  const pageMeta = {
    dashboard: {
      title: t('dashboard.title'),
      subtitle: t('dashboard.subtitle'),
      component: <DashboardPage />,
    },
    traffic: {
      title: t('traffic.pageTitle'),
      subtitle: t('traffic.pageSubtitle'),
      component: <NetworkTrafficPage />,
    },
    forecast: {
      title: t('forecast.pageTitle'),
      subtitle: t('forecast.pageSubtitle'),
      component: <AttackForecastPage />,
    },
    story: {
      title: t('story.pageTitle'),
      subtitle: t('story.pageSubtitle'),
      component: <AttackStoryPage />,
    },
    warnings: {
      title: t('earlyWarnings.pageTitle'),
      subtitle: t('earlyWarnings.pageSubtitle'),
      component: <EarlyWarningsPage />,
    },
    recommendations: {
      title: t('recommendations.pageTitle'),
      subtitle: t('recommendations.pageSubtitle'),
      component: <RecommendationsPage />,
    },
    status: {
      title: t('systemStatus.pageTitle'),
      subtitle: t('systemStatus.pageSubtitle'),
      component: <SystemStatusPage />,
    },
  };

  const activeMeta = pageMeta[currentPage] || pageMeta.dashboard;

  return (
    <MainLayout
      activePage={currentPage}
      onNavigate={(pageId) => setCurrentPage(pageId)}
      pageTitle={activeMeta.title}
      pageSubtitle={activeMeta.subtitle}
    >
      {activeMeta.component}
    </MainLayout>
  );
};

export const App = () => {
  return (
    <LanguageProvider>
      <AppContent />
    </LanguageProvider>
  );
};

export default App;

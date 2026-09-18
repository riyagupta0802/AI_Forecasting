import React from 'react';
import { LanguageProvider } from './hooks/useLanguage';
import MainLayout from './layouts/MainLayout';
import StarterDashboard from './pages/StarterDashboard';

export const App = () => {
  return (
    <LanguageProvider>
      <MainLayout>
        <StarterDashboard />
      </MainLayout>
    </LanguageProvider>
  );
};

export default App;


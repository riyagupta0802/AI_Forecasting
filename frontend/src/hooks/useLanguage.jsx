import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  SUPPORTED_LANGUAGES,
  DEFAULT_LANGUAGE,
  STORAGE_KEY,
  translate,
} from '../i18n/index.js';

const LanguageContext = createContext(null);

export const LanguageProvider = ({ children }) => {
  const [language, setLanguageState] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved && SUPPORTED_LANGUAGES[saved]) {
        return saved;
      }
    } catch (e) {
      console.warn('Unable to access localStorage for language preference:', e);
    }
    return DEFAULT_LANGUAGE;
  });

  const setLanguage = useCallback((newLang) => {
    if (!SUPPORTED_LANGUAGES[newLang]) {
      console.warn(`Unsupported language requested: ${newLang}`);
      return;
    }
    setLanguageState(newLang);
    try {
      localStorage.setItem(STORAGE_KEY, newLang);
    } catch (e) {
      console.warn('Unable to save language preference to localStorage:', e);
    }
  }, []);

  const t = useCallback(
    (keyPath, fallback) => translate(language, keyPath, fallback),
    [language]
  );

  useEffect(() => {
    // Update document lang attribute dynamically
    document.documentElement.lang = language;
  }, [language]);

  const value = {
    language,
    setLanguage,
    t,
    languages: SUPPORTED_LANGUAGES,
    currentLanguageMeta: SUPPORTED_LANGUAGES[language],
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};


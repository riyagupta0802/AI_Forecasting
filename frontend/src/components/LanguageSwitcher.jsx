import React from 'react';
import { Globe } from 'lucide-react';
import { useLanguage } from '../hooks/useLanguage';

/**
 * Reusable Language Switcher component supporting English and Hindi.
 * Saves preferences to localStorage and updates UI instantly.
 */
export const LanguageSwitcher = () => {
  const { language, setLanguage, languages } = useLanguage();

  return (
    <div className="lang-switcher-container" role="group" aria-label="Language Selector">
      <div style={{ paddingLeft: '0.4rem', display: 'flex', alignItems: 'center', color: 'var(--text-muted)' }}>
        <Globe size={15} />
      </div>
      {Object.values(languages).map((lang) => {
        const isActive = language === lang.code;
        return (
          <button
            key={lang.code}
            type="button"
            className={`lang-btn ${isActive ? 'active' : ''}`}
            onClick={() => setLanguage(lang.code)}
            aria-pressed={isActive}
            title={`Switch to ${lang.name}`}
          >
            {lang.nativeName}
          </button>
        );
      })}
    </div>
  );
};

export default LanguageSwitcher;


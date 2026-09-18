import en from './en.js';
import hi from './hi.js';

export const SUPPORTED_LANGUAGES = {
  en: { code: 'en', name: 'English', nativeName: 'English' },
  hi: { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी' },
};

export const DEFAULT_LANGUAGE = 'en';
export const STORAGE_KEY = 'hexhive_language';

export const translations = {
  en,
  hi,
};

/**
 * Resolves a nested key in a translation object.
 * e.g., getTranslationValue(en, 'brand.projectName') -> 'HEX HIVE'
 */
export function getTranslationValue(dictionary, keyPath) {
  if (!dictionary || !keyPath) return keyPath;
  const parts = keyPath.split('.');
  let current = dictionary;
  for (const part of parts) {
    if (current && typeof current === 'object' && part in current) {
      current = current[part];
    } else {
      return null;
    }
  }
  return current;
}

/**
 * Translate helper with fallback to default language (English).
 */
export function translate(lang, keyPath, fallback = '') {
  const selectedDict = translations[lang] || translations[DEFAULT_LANGUAGE];
  const value = getTranslationValue(selectedDict, keyPath);

  if (value !== null && value !== undefined) {
    return value;
  }

  // Fallback to English
  const defaultValue = getTranslationValue(translations[DEFAULT_LANGUAGE], keyPath);
  if (defaultValue !== null && defaultValue !== undefined) {
    return defaultValue;
  }

  return fallback || keyPath;
}

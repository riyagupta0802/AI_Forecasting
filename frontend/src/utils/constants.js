/**
 * Application Constants
 */
const envApiUrl = typeof import.meta !== 'undefined' && import.meta.env ? import.meta.env.VITE_API_URL : null;
export const API_BASE_URL = envApiUrl || 'http://localhost:8000/api';

export const PROJECT_METADATA = {
  name: 'HEX HIVE',
  hackathon: 'Smart India Hackathon 2026',
  problemId: 'SIH26153',
  theme: 'Blockchain & Cybersecurity',
  category: 'Software',
  phase: 'Phase 1 - Foundation & Architecture',
};


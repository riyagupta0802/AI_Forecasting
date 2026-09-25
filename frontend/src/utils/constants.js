/**
 * Application Constants
 */
const envApiUrl = typeof import.meta !== 'undefined' && import.meta.env ? import.meta.env.VITE_API_URL : null;
export const API_BASE_URL = envApiUrl || '/api';

export const PROJECT_METADATA = {
  name: 'NETORACLE',
  description: 'AI based Network Attack Forecasting from Network Traffic Data',
  theme: 'Cybersecurity Intelligence',
  category: 'Software',
  phase: 'Phase 5 - AI Attack Detection',
};



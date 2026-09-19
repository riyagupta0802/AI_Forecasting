import { API_BASE_URL } from '../utils/constants.js';

/**
 * HEX HIVE API Service Layer
 * Centralized HTTP client communicating with FastAPI backend
 */
class ApiService {
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  /**
   * Generic safe fetch with timeout and error resilience
   */
  async request(endpoint, options = {}) {
    const startTime = performance.now();
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), options.timeout || 4000);

      const url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          ...(options.headers || {}),
        },
        signal: controller.signal,
        ...options,
      });

      clearTimeout(timeoutId);
      const latencyMs = Math.round(performance.now() - startTime);

      if (!response.ok) {
        return {
          ok: false,
          status: response.status,
          latencyMs,
          error: `HTTP ${response.status} ${response.statusText}`,
          data: null,
        };
      }

      const data = await response.json();
      return {
        ok: true,
        status: response.status,
        latencyMs,
        data,
        error: null,
      };
    } catch (err) {
      const latencyMs = Math.round(performance.now() - startTime);
      return {
        ok: false,
        status: 0,
        latencyMs,
        error: err.name === 'AbortError' ? 'Request timed out' : (err.message || 'Network unreachable'),
        data: null,
      };
    }
  }

  /**
   * Health status check: GET /api/health
   */
  async checkHealth() {
    return this.request('/health');
  }

  /**
   * System status check: GET /api/system/status
   */
  async getSystemStatus() {
    return this.request('/system/status');
  }

  /**
   * Network security summary metrics (Demo data): GET /api/network/summary
   */
  async getNetworkSummary() {
    return this.request('/network/summary');
  }

  /**
   * Attack forecast status placeholder: GET /api/forecast/status
   */
  async getForecastStatus() {
    return this.request('/forecast/status');
  }

  /**
   * Sample network traffic time-series: GET /api/traffic/sample
   */
  async getTrafficSample() {
    return this.request('/traffic/sample');
  }

  /**
   * Dataset and preprocessing pipeline status (Phase 4): GET /api/data/status
   */
  async getDataStatus() {
    return this.request('/data/status');
  }

  getBaseUrl() {
    return this.baseUrl;
  }
}

export const apiService = new ApiService();
export default apiService;

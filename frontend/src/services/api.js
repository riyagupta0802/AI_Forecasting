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
   * Attack forecast status and real transition projection (Phase 6): GET /api/forecast/status
   */
  async getForecastStatus() {
    return this.request('/forecast/status');
  }

  /**
   * Real evaluated forecasting test-set metrics (Phase 6): GET /api/forecast/metrics
   */
  async getForecastMetrics() {
    return this.request('/forecast/metrics');
  }

  /**
   * Live attack detection -> stage -> forecast transition (Phase 6): POST /api/forecast/predict
   */
  async predictForecast(payload = {}) {
    return this.request('/forecast/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
  }

  /**
   * Threat escalation status and estimated window (Phase 7): GET /api/escalation/status
   */
  async getEscalationStatus() {
    return this.request('/escalation/status');
  }

  /**
   * Real evaluated escalation regression metrics (Phase 7): GET /api/escalation/metrics
   */
  async getEscalationMetrics() {
    return this.request('/escalation/metrics');
  }

  /**
   * Live Detection -> Forecasting -> Time-to-Escalation (Phase 7): POST /api/escalation/predict
   */
  async predictEscalation(payload = {}) {
    return this.request('/escalation/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
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

  /**
   * Machine Learning classifier status (Phase 5): GET /api/ml/status
   */
  async getMlStatus() {
    return this.request('/ml/status');
  }

  /**
   * Real evaluated ML test-set metrics (Phase 5): GET /api/ml/metrics
   */
  async getMlMetrics() {
    return this.request('/ml/metrics');
  }

  /**
   * Real Random Forest attack prediction (Phase 5): POST /api/ml/predict
   */
  async predictAttack(payload = {}) {
    return this.request('/ml/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
  }

  /**
   * Attack Story Engine status & inventory (Phase 8): GET /api/attack-story/status
   */
  async getAttackStoryStatus() {
    return this.request('/attack-story/status');
  }

  /**
   * Filtered Chronological Attack Story & Timeline (Phase 8): GET /api/attack-story
   */
  async getAttackStory(params = {}) {
    const query = new URLSearchParams();
    if (params.category) query.append('category', params.category);
    if (params.severity) query.append('severity', params.severity);
    if (params.context) query.append('context', params.context);
    if (params.limit) query.append('limit', params.limit);
    const queryString = query.toString();
    const endpoint = queryString ? `/attack-story?${queryString}` : '/attack-story';
    return this.request(endpoint);
  }

  /**
   * On-demand Context Attack Story Generation (Phase 8): POST /api/attack-story/generate
   */
  async generateAttackStory(payload = {}) {
    return this.request('/attack-story/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
  }

  getBaseUrl() {
    return this.baseUrl;
  }
}

export const apiService = new ApiService();
export default apiService;

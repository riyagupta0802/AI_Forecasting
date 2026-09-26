import { API_BASE_URL } from '../utils/constants.js';

/**
 * NETORACLE API Service Layer
 * Centralized HTTP client communicating with FastAPI backend
 */
class ApiService {
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    this._cachedAnalysis = null;
  }

  /**
   * Generic safe fetch with timeout and error resilience
   */
  async request(endpoint, options = {}) {
    const startTime = performance.now();
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), options.timeout || 10000);

      const url = `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
      const headers = {
        'Accept': 'application/json',
        ...(options.headers || {}),
      };

      // Let browser set multipart boundary when using FormData
      if (options.body instanceof FormData) {
        delete headers['Content-Type'];
      }

      const response = await fetch(url, {
        method: 'GET',
        headers,
        signal: controller.signal,
        ...options,
      });

      clearTimeout(timeoutId);
      const latencyMs = Math.round(performance.now() - startTime);

      if (!response.ok) {
        let errorDetail = `HTTP ${response.status} ${response.statusText}`;
        try {
          const errJson = await response.json();
          if (errJson && errJson.detail) {
            errorDetail = errJson.detail;
          }
        } catch (_) {}

        return {
          ok: false,
          status: response.status,
          latencyMs,
          error: errorDetail,
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

  /**
   * Early Warning Engine status & inventory (Phase 9): GET /api/warnings/status
   */
  async getWarningsStatus() {
    return this.request('/warnings/status');
  }

  /**
   * Active Early Warnings & History (Phase 9): GET /api/warnings
   */
  async getWarnings(params = {}) {
    const query = new URLSearchParams();
    if (params.severity) query.append('severity', params.severity);
    if (params.warning_type) query.append('warning_type', params.warning_type);
    if (params.status) query.append('status', params.status);
    if (params.context) query.append('context', params.context);
    if (params.limit) query.append('limit', params.limit);
    const queryString = query.toString();
    const endpoint = queryString ? `/warnings?${queryString}` : '/warnings';
    return this.request(endpoint);
  }

  /**
   * Evaluate Threat Context for Early Warnings (Phase 9): POST /api/warnings/evaluate
   */
  async evaluateWarnings(payload = {}) {
    return this.request('/warnings/evaluate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
  }

  /**
   * Recommendation Engine status & statistical summary (Phase 10): GET /api/recommendations/status
   */
  async getRecommendationsStatus() {
    return this.request('/recommendations/status');
  }

  /**
   * Defensive Security Recommendations (Phase 10): GET /api/recommendations
   */
  async getRecommendations(params = {}) {
    const query = new URLSearchParams();
    if (params.priority) query.append('priority', params.priority);
    if (params.category) query.append('category', params.category);
    if (params.status) query.append('status', params.status);
    if (params.context) query.append('context', params.context);
    if (params.limit) query.append('limit', params.limit);
    const queryString = query.toString();
    const endpoint = queryString ? `/recommendations?${queryString}` : '/recommendations';
    return this.request(endpoint);
  }

  /**
   * Generate Contextual Recommendations On-Demand (Phase 10): POST /api/recommendations/generate
   */
  async generateRecommendations(payload = {}) {
    return this.request('/recommendations/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
  }

  /**
   * Update Recommendation Operator Status (Phase 10): PATCH /api/recommendations/{id}/status
   */
  async updateRecommendationStatus(recommendationId, newStatus) {
    return this.request(`/recommendations/${encodeURIComponent(recommendationId)}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status: newStatus }),
    });
  }

  /**
   * Explainable AI (XAI) Status (Phase 11): GET /api/explainability/status
   */
  async getExplainabilityStatus() {
    return this.request('/explainability/status');
  }

  /**
   * Local SHAP Explanation for Detection Prediction (Phase 11): POST /api/explainability/explain
   */
  async explainPrediction(payload = {}) {
    return this.request('/explainability/explain', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
  }

  /**
   * Global Feature Importance via Mean Absolute SHAP (Phase 11): GET /api/explainability/global
   */
  async getGlobalExplainability(topN = 10) {
    return this.request(`/explainability/global?top_n=${encodeURIComponent(topN)}`);
  }

  /**
   * Validate dataset column headers against Phase 5 78-feature schema: POST /api/analyze/validate
   */
  async validateDataset(formData) {
    return this.request('/analyze/validate', {
      method: 'POST',
      body: formData,
      timeout: 15000,
    });
  }

  /**
   * Run full Phase 5–11 multi-phase analysis on uploaded dataset: POST /api/analyze
   */
  async analyzeDataset(formData) {
    const res = await this.request('/analyze', {
      method: 'POST',
      body: formData,
      timeout: 60000,
    });
    if (res.ok && res.data) {
      this.setLastAnalysis(res.data);
    }
    return res;
  }

  /**
   * Run analysis via raw JSON/text: POST /api/analyze/json
   */
  async analyzeDatasetJson(payload = {}) {
    const res = await this.request('/analyze/json', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      timeout: 60000,
    });
    if (res.ok && res.data) {
      this.setLastAnalysis(res.data);
    }
    return res;
  }

  /**
   * Get direct download URL for sample test dataset CSV
   */
  getSampleCsvUrl() {
    return `${this.baseUrl}/analyze/sample-csv`;
  }

  /**
   * Retrieve cached last analysis from memory or sessionStorage
   */
  getLastAnalysis() {
    if (this._cachedAnalysis) {
      return this._cachedAnalysis;
    }
    try {
      const stored = sessionStorage.getItem('netoracle_last_analysis');
      if (stored) {
        this._cachedAnalysis = JSON.parse(stored);
        return this._cachedAnalysis;
      }
    } catch (_) {}
    return null;
  }

  /**
   * Cache analysis in memory & sessionStorage, and dispatch update event
   */
  setLastAnalysis(data) {
    this._cachedAnalysis = data;
    try {
      sessionStorage.setItem('netoracle_last_analysis', JSON.stringify(data));
      window.dispatchEvent(new CustomEvent('netoracle-analysis-updated', { detail: data }));
    } catch (_) {}
  }

  /**
   * Clear cached analysis
   */
  clearLastAnalysis() {
    this._cachedAnalysis = null;
    try {
      sessionStorage.removeItem('netoracle_last_analysis');
      window.dispatchEvent(new CustomEvent('netoracle-analysis-updated', { detail: null }));
    } catch (_) {}
  }

  getBaseUrl() {
    return this.baseUrl;
  }
}


export const apiService = new ApiService();
export default apiService;


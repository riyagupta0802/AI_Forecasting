import { API_BASE_URL } from '../utils/constants';

/**
 * HEX HIVE API Service Layer
 */
class ApiService {
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  /**
   * Health status check against GET /api/health
   */
  async checkHealth() {
    const startTime = performance.now();
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        signal: controller.signal,
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
        error: err.name === 'AbortError' ? 'Request timed out' : (err.message || 'Network error'),
        data: null,
      };
    }
  }

  getBaseUrl() {
    return this.baseUrl;
  }
}

export const apiService = new ApiService();
export default apiService;


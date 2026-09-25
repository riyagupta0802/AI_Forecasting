import React from 'react';
import { ShieldAlert, RefreshCw, RotateCcw } from 'lucide-react';

/**
 * ErrorBoundary - Protects the HEX HIVE SOC Dashboard against uncaught component crashes.
 * Intercepts JavaScript rendering errors and prevents white/black screen cascade unmounts.
 */
export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[NETORACLE ErrorBoundary] Caught component error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      const errorMessage = this.state.error?.message || 'An unexpected rendering error occurred.';

      return (
        <div
          className="soc-card error-boundary-card"
          style={{
            margin: '1.5rem',
            padding: '1.5rem',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            background: 'linear-gradient(180deg, rgba(239, 68, 68, 0.08) 0%, rgba(17, 29, 53, 0.95) 100%)',
            borderRadius: '10px',
            color: 'var(--text-primary)',
          }}
          role="alert"
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: '8px',
                background: 'rgba(239, 68, 68, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '1px solid rgba(239, 68, 68, 0.5)',
              }}
            >
              <ShieldAlert size={22} color="#EF4444" />
            </div>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#F8FAFC', margin: 0 }}>
                SOC Dashboard Telemetry Guard
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', margin: 0 }}>
                A dashboard rendering error was intercepted. The application was kept alive.
              </p>
            </div>
          </div>

          <div
            style={{
              padding: '0.75rem 1rem',
              background: 'rgba(0, 0, 0, 0.35)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              fontFamily: 'var(--font-mono, monospace)',
              fontSize: '0.78rem',
              color: '#FCA5A5',
              marginBottom: '1rem',
              wordBreak: 'break-word',
            }}
          >
            {errorMessage}
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={this.handleReset}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.45rem 0.9rem',
                background: 'rgba(0, 240, 255, 0.15)',
                border: '1px solid rgba(0, 240, 255, 0.4)',
                color: 'var(--accent-cyan)',
                borderRadius: '6px',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <RotateCcw size={14} />
              Reset Component
            </button>

            <button
              type="button"
              onClick={this.handleReload}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.45rem 0.9rem',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--border-subtle)',
                color: 'var(--text-secondary)',
                borderRadius: '6px',
                fontSize: '0.78rem',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              <RefreshCw size={14} />
              Reload Application
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;


import React from 'react';

/**
 * HealthStatus widget displaying real-time backend operational status.
 */
export default function HealthStatus({ health, loading, onRefresh }) {
  const isHealthy = health?.status === 'healthy';

  return (
    <div className="health-status-widget" id="health-status-widget">
      <div className="health-status-header">
        <span className={`status-badge ${isHealthy ? 'badge-online' : 'badge-offline'}`}>
          {loading ? 'Checking...' : isHealthy ? 'Backend Online' : 'Backend Offline'}
        </span>
        {onRefresh && (
          <button onClick={onRefresh} className="btn-refresh" title="Refresh health status">
            Refresh
          </button>
        )}
      </div>
      <div className="health-status-meta">
        <small>Service: {health?.service || 'DataSense AI'}</small>
        <small>Env: {health?.environment || 'development'}</small>
      </div>
    </div>
  );
}

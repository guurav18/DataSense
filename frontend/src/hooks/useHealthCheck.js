import { useState, useEffect } from 'react';
import { checkBackendHealth } from '../services/api';

/**
 * Custom React hook to monitor backend health status.
 */
export function useHealthCheck(pollIntervalMs = 10000) {
  const [health, setHealth] = useState({
    status: 'checking',
    service: null,
    environment: null,
    database_configured: false,
    llm_configured: false,
  });
  const [loading, setLoading] = useState(true);

  const fetchHealth = async () => {
    try {
      const data = await checkBackendHealth();
      setHealth(data);
    } catch {
      setHealth({ status: 'offline' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, pollIntervalMs);
    return () => clearInterval(interval);
  }, [pollIntervalMs]);

  return { health, loading, refetch: fetchHealth };
}

/**
 * API service client for communicating with the DataSense AI backend.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Fetch backend health status.
 * @returns {Promise<{status: string, service?: string, environment?: string}>}
 */
export async function checkBackendHealth() {
  try {
    const response = await fetch(`${BASE_URL}/health`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    return {
      status: 'offline',
      error: error.message || 'Unable to connect to backend server',
    };
  }
}

/**
 * Upload dataset file (CSV/Excel) to the backend.
 * @param {File} file 
 * @returns {Promise<any>}
 */
export async function uploadDataset(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BASE_URL}/api/v1/datasets/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to upload dataset');
  }

  return response.json();
}

/**
 * Fetch dataset details by ID.
 * @param {string} datasetId 
 * @returns {Promise<any>}
 */
export async function getDataset(datasetId) {
  const response = await fetch(`${BASE_URL}/api/v1/datasets/${datasetId}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch dataset');
  }
  return response.json();
}

/**
 * Trigger automated dataset cleaning.
 * @param {string} datasetId 
 * @returns {Promise<any>}
 */
export async function cleanDataset(datasetId) {
  const response = await fetch(`${BASE_URL}/api/v1/datasets/${datasetId}/clean`, {
    method: 'POST',
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to clean dataset');
  }
  return response.json();
}

/**
 * Submit an analytical query to the DataSense Agent.
 * @param {string} query 
 * @param {string} [datasetId] 
 * @returns {Promise<any>}
 */
export async function queryAgent(query, datasetId) {
  const response = await fetch(`${BASE_URL}/api/v1/agent/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, dataset_id: datasetId }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Agent query failed');
  }

  return response.json();
}

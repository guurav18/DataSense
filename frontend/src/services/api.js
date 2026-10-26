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
 * Fetch backend status and feature matrix.
 * @returns {Promise<any>}
 */
export async function fetchApiStatus() {
  const response = await fetch(`${BASE_URL}/api/v1/status`);
  if (!response.ok) {
    throw new Error('Failed to retrieve API status');
  }
  return response.json();
}

/**
 * Upload dataset file (CSV/Excel) to the backend.
 * @param {File} file 
 * @param {boolean} autoClean
 * @returns {Promise<any>}
 */
export async function uploadDataset(file, autoClean = true) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BASE_URL}/api/v1/datasets/upload?auto_clean=${autoClean}`, {
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
 * Fetch pre-configured demo dataset for instant testing.
 * @returns {Promise<any>}
 */
export async function fetchDemoDataset() {
  const response = await fetch(`${BASE_URL}/api/v1/datasets/demo`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to load demo dataset');
  }
  return response.json();
}

/**
 * Fetch preview data for an uploaded dataset by ID.
 * @param {string} datasetId 
 * @returns {Promise<any>}
 */
export async function fetchDatasetPreview(datasetId) {
  const response = await fetch(`${BASE_URL}/api/v1/datasets/preview?dataset_id=${datasetId}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to preview dataset');
  }
  return response.json();
}

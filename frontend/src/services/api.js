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
 * @param {boolean} generateCharts
 * @returns {Promise<any>}
 */
export async function uploadDataset(file, autoClean = true, generateCharts = true) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(
    `${BASE_URL}/api/v1/datasets/upload?auto_clean=${autoClean}&generate_charts=${generateCharts}`,
    {
      method: 'POST',
      body: formData,
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to upload dataset');
  }

  return response.json();
}

/**
 * Fetch pre-configured demo dataset with starter charts for instant testing.
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

/**
 * Generates custom visualization on demand.
 * @param {string} datasetId
 * @param {'histogram' | 'heatmap' | 'scatter' | 'bar'} chartType
 * @param {Record<string, any>} params
 * @returns {Promise<any>}
 */
export async function generateCustomChart(datasetId, chartType, params = {}) {
  const response = await fetch(`${BASE_URL}/api/v1/charts/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      dataset_id: datasetId,
      chart_type: chartType,
      params,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to generate chart');
  }

  return response.json();
}

/**
 * Constructs absolute chart URL.
 * @param {string} relativeUrl 
 * @returns {string}
 */
export function getChartUrl(relativeUrl) {
  if (!relativeUrl) return '';
  if (relativeUrl.startsWith('http')) return relativeUrl;
  return `${BASE_URL}${relativeUrl}`;
}

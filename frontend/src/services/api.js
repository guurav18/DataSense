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

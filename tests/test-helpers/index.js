/**
 * Helper functions for Playwright API tests.
 */

/**
 * Makes an API request to the FastAPI server with authentication
 * @param {import('@playwright/test').APIRequestContext} request - Playwright request context
 * @param {string} endpoint - API endpoint to call
 * @param {Object} options - Request options
 * @param {string} [options.method='GET'] - HTTP method
 * @param {Object} [options.data=null] - Request body data
 * @param {string} [options.token=null] - JWT token for authentication
 * @returns {Promise<Object>} API response
 */
async function makeApiRequest(request, endpoint, { method = 'GET', data = null, token = null } = {}) {
  const headers = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const options = {
    headers,
    method,
  };

  if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
    options.data = data;
  }

  return request.fetch(endpoint, options);
}

/**
 * Gets the health check endpoint
 * @param {import('@playwright/test').APIRequestContext} request - Playwright request context
 * @returns {Promise<Object>} Health check response
 */
async function getHealthCheck(request) {
  return makeApiRequest(request, '/api/v1/health');
}

/**
 * Gets the current user info
 * @param {import('@playwright/test').APIRequestContext} request - Playwright request context
 * @param {string} token - JWT token for authentication
 * @returns {Promise<Object>} User info response
 */
async function getCurrentUserInfo(request, token) {
  return makeApiRequest(request, '/api/v1/users/me', { token });
}

/**
 * Gets the user settings
 * @param {import('@playwright/test').APIRequestContext} request - Playwright request context
 * @param {string} token - JWT token for authentication
 * @returns {Promise<Object>} User settings response
 */
async function getUserSettings(request, token) {
  return makeApiRequest(request, '/api/v1/users/me/settings', { token });
}

/**
 * Updates the user settings
 * @param {import('@playwright/test').APIRequestContext} request - Playwright request context
 * @param {string} token - JWT token for authentication
 * @param {Object} settings - New user settings
 * @returns {Promise<Object>} Updated user settings response
 */
async function updateUserSettings(request, token, settings) {
  return makeApiRequest(request, '/api/v1/users/me/settings', {
    method: 'PUT',
    token,
    data: settings,
  });
}

/**
 * Test JWT token for authentication
 * @returns {string} Test JWT token
 */
function getTestToken() {
  return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJlbWFpbCI6InRlc3RAdGVzdC5jb20iLCJyb2xlIjoidXNlciJ9.this_is_a_test_token';
}

module.exports = {
  makeApiRequest,
  getHealthCheck,
  getCurrentUserInfo,
  getUserSettings,
  updateUserSettings,
  getTestToken,
};

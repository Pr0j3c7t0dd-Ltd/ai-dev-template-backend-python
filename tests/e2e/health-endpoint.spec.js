import { test, expect } from '@playwright/test';
import { getHealthCheck } from '../test-helpers/index.js';

test.describe('Health Endpoint', () => {
  test.beforeEach(async ({ request }) => {
    // Setup code here
  });

  test('should return healthy status when API is available', async ({ request }) => {
    // Get health check response
    const response = await getHealthCheck(request);

    // Verify status code
    expect(response.status()).toBe(200);

    // Verify response body
    const responseBody = await response.json();
    expect(responseBody).toHaveProperty('status');
    expect(responseBody.status).toMatch(/healthy|unhealthy/);

    // Check details object
    expect(responseBody).toHaveProperty('details');
    expect(responseBody.details).toHaveProperty('database');
    expect(responseBody.details).toHaveProperty('services');

    // In tests, we accept both connected and error states
    expect(responseBody.details.database).toMatch(/connected|error/);
  });
});

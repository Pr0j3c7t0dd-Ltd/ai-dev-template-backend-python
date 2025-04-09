import { test, expect } from '@playwright/test';

test.describe('Root Endpoint', () => {
  test('should return API status', async ({ request }) => {
    // Get the root endpoint
    const response = await request.get('/');

    // Verify status code
    expect(response.status()).toBe(200);

    // Verify response body
    const responseBody = await response.json();
    expect(responseBody).toHaveProperty('status');
    expect(responseBody.status).toBe('online');
    expect(responseBody).toHaveProperty('version');
  });
});

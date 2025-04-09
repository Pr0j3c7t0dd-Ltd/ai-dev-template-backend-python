/**
 * Helper functions for interacting with GOV.UK Design System components in tests
 */

/**
 * Gets a GDS button by its text content
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} text - Button text to match
 * @returns {Promise<import('@playwright/test').Locator>} Button element
 */
async function getGdsButton(page, text) {
  return page.getByRole('button', { name: text });
}

/**
 * Gets an error summary component (validation errors at top of page)
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @returns {Promise<import('@playwright/test').Locator>} Error summary element
 */
async function getGdsErrorSummary(page) {
  return page.locator('.govuk-error-summary');
}

/**
 * Gets the text from an error summary component
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @returns {Promise<string>} Error summary text content
 */
async function getGdsErrorSummaryText(page) {
  const summary = await getGdsErrorSummary(page);
  return summary.textContent();
}

/**
 * Gets a specific error link from the error summary by its text
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} text - Error text to match
 * @returns {Promise<import('@playwright/test').Locator>} Error link element
 */
async function getGdsErrorLink(page, text) {
  const summary = await getGdsErrorSummary(page);
  return summary.getByRole('link', { name: text });
}

/**
 * Gets a GDS form input field by its label text
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} labelText - Label text to match
 * @returns {Promise<import('@playwright/test').Locator>} Input field element
 */
async function getGdsInputByLabel(page, labelText) {
  const label = page.getByText(labelText, { exact: true });
  const id = await label.getAttribute('for');
  return page.locator(`#${id}`);
}

/**
 * Fills a GDS form field with the specified value
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} labelText - Label text to match
 * @param {string} value - Value to fill
 * @returns {Promise<void>}
 */
async function fillGdsField(page, labelText, value) {
  const input = await getGdsInputByLabel(page, labelText);
  await input.fill(value);
}

/**
 * Gets text from a GDS banner component
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @returns {Promise<string>} Banner text content
 */
async function getGdsBannerText(page) {
  const banner = page.locator('.govuk-notification-banner');
  return banner.textContent();
}

/**
 * Checks if a GDS error message exists for a specific form field
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} labelText - Label text to match
 * @returns {Promise<boolean>} Whether an error message exists
 */
async function hasGdsFieldError(page, labelText) {
  const input = await getGdsInputByLabel(page, labelText);
  const formGroup = input.locator('xpath=ancestor::div[contains(@class, "govuk-form-group")]');
  const errorMessage = formGroup.locator('.govuk-error-message');
  return errorMessage.isVisible();
}

/**
 * Gets the error message text for a specific form field
 * @param {import('@playwright/test').Page} page - Playwright page object
 * @param {string} labelText - Label text to match
 * @returns {Promise<string>} Error message text
 */
async function getGdsFieldErrorText(page, labelText) {
  const input = await getGdsInputByLabel(page, labelText);
  const formGroup = input.locator('xpath=ancestor::div[contains(@class, "govuk-form-group")]');
  const errorMessage = formGroup.locator('.govuk-error-message');
  return errorMessage.textContent();
}

module.exports = {
  getGdsButton,
  getGdsErrorSummary,
  getGdsErrorSummaryText,
  getGdsErrorLink,
  getGdsInputByLabel,
  fillGdsField,
  getGdsBannerText,
  hasGdsFieldError,
  getGdsFieldErrorText,
};

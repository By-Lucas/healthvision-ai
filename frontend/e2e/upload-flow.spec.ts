import { test, expect } from '@playwright/test';

// 1x1 PNG, base64-decoded into a Buffer for an in-memory upload.
const PNG_1X1 = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
  'base64',
);

test('home → upload → submit → see analysis detail', async ({ page }) => {
  // Home
  await page.goto('/');
  await expect(
    page.getByRole('heading', { name: /chest x-ray analysis/i }),
  ).toBeVisible();
  await expect(page.getByText(/not a medical diagnosis tool/i).first()).toBeVisible();

  // Go to upload
  await page.getByRole('link', { name: /upload an exam/i }).click();
  await expect(page).toHaveURL(/\/upload/);

  // Select a file
  await page.getByTestId('file-input').setInputFiles({
    name: 'demo-xray.png',
    mimeType: 'image/png',
    buffer: PNG_1X1,
  });
  await expect(page.getByAltText(/exam preview/i)).toBeVisible();

  // Submit
  await page.getByTestId('submit-upload').click();

  // Lands on the detail page and shows the result panel.
  await expect(page).toHaveURL(/\/analysis\//);
  await expect(page.getByRole('heading', { name: /analysis detail/i })).toBeVisible();
  // Worker processes asynchronously; the page polls until completed.
  await expect(page.getByText(/COMPLETED|PROCESSING|PENDING/).first()).toBeVisible();
});

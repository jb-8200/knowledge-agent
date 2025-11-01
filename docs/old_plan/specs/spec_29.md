# Spec 29 – Write UI tests

This specification recommends using Playwright for end‑to‑end UI testing.  Playwright can automate browser interactions and verify DOM updates.

## Setup

1. Install Playwright and its browsers:

   ```bash
   npm install --save-dev playwright
   npx playwright install
   ```

2. Configure a test script in `package.json`:

   ```json
   {
     "scripts": {
       "test:ui": "playwright test"
     }
   }
   ```

## Test Scenarios

* **Basic search:** Navigate to the app, enter a query, submit and verify that an answer appears with citations.
* **Citations click:** Click internal and external citations and check that links open in new tabs.
* **Pinning:** Click the pin icon next to an answer; verify that the pinned note appears in the sidebar and that unpinning removes it.
* **Download as Markdown:** Click the download button and check that a file is downloaded with the correct filename and content.
* **Follow‑up questions:** Click a related question and verify that a new query is issued and a new answer is displayed.
* **Error handling:** Simulate a network error (mock API failure) and ensure that an error message is displayed.

## Writing Tests

Example Playwright test skeleton:

```javascript
const { test, expect } = require('@playwright/test');

test('basic search and pin', async ({ page }) => {
  await page.goto('http://localhost:5000');
  await page.fill('#query', 'What is LangChain?');
  await page.click('button[type="submit"]');
  await page.waitForSelector('#answer');
  expect(await page.locator('#answer').innerText()).not.toBe('');
  // Pin the answer
  await page.click('.pin-icon');
  expect(await page.locator('#pinned-list li').count()).toBe(1);
});
```

Add selectors (e.g., `.pin-icon`) and adjust the test code to match your actual DOM structure.  Use Playwright’s `fixtures` to start a mock backend if necessary.

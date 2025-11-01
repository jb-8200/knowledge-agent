# Acceptance Test for Task 25 – Configure Firebase Hosting

**Objective:** Validate that Firebase Hosting is configured correctly to serve the front‑end application.

**Test Steps:**

1. Check that a `firebase.json` configuration file exists with a `hosting` section specifying the `public` directory and rewrite rules to route all requests to `index.html` (for a Single Page Application).
2. Run the build script (e.g., `npm run build`) and confirm that the compiled assets (HTML, CSS, JS) are placed in the configured `public` directory.
3. Start a local hosting preview using `firebase serve` or `firebase emulators:start` and navigate to `http://localhost:5000`.
4. Verify that the application loads without errors and that all routes work via the rewrite configuration.
5. Ensure that the configuration includes placeholders for any future environment variables or authentication rules without breaking deployment.

**Expected Result:** Firebase Hosting serves the built front‑end locally with correct rewrites and placeholders for future enhancements.

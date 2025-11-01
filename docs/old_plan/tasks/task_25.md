# Task 25 – Configure Firebase Hosting

**Phase:** Deployment

**Description:**

Set up Firebase Hosting to serve the static front‑end assets.  Initialize a Firebase project (or use an existing one), configure `firebase.json` to define the hosting target, public directory, rewrite rules (if necessary) and caching headers.  Ensure that the build process (e.g., bundling or minification) outputs files to the `public/` directory.  Test the deployment locally using `firebase serve` and then deploy to Firebase Hosting.

**Acceptance Criteria:**

* A Firebase project is initialized and configured for hosting.
* `firebase.json` specifies the correct public directory and rewrites (if needed for a SPA).
* Running `firebase serve` serves the front‑end locally without backend interference.
* The front‑end is successfully deployed using `firebase deploy` and accessible over HTTPS.

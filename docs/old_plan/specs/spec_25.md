# Spec 25 – Configure Firebase Hosting

This specification covers the configuration of Firebase Hosting to serve the front‑end assets.

## Firebase Project Initialization

1. Install the Firebase CLI globally if not already installed:

   ```bash
   npm install -g firebase-tools
   ```

2. Log in to Firebase and initialize the project in the repository root:

   ```bash
   firebase login
   firebase init hosting
   ```

   * Select the existing Firebase project or create a new one.
   * Set the public directory to `frontend` or `dist` depending on your build output.
   * Configure the app as a single page application by choosing `Yes` for rewrites.
   * Do not overwrite existing `index.html` if present.

## firebase.json Configuration

Your `firebase.json` should include hosting configuration similar to:

```json
{
  "hosting": {
    "public": "frontend",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      { "source": "**", "destination": "/index.html" }
    ]
  }
}
```

Adjust the `public` directory to match your front‑end build output.  The rewrite ensures that all routes serve `index.html`, which is typical for single page applications.

## Local Testing and Deployment

Run `firebase serve` to test the hosting configuration locally:

```bash
firebase serve --only hosting
```

When ready, deploy to production:

```bash
firebase deploy --only hosting
```

Verify that the site is accessible via the provided Firebase hosting URL.

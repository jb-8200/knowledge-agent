# User Story: Deployment

## User Persona
**Name:** DevOps Engineer
**Description:** Responsible for deploying and maintaining production systems.

## Story
**As a** DevOps Engineer
**I want to** deploy the knowledge agent to production
**so that** end users can access it reliably

## Acceptance Criteria (EARS Format)
- WHEN I deploy the frontend THEN I SHALL see it hosted on Firebase Hosting
- WHEN I deploy the backend THEN I SHALL see it running on Cloud Run or ECS
- WHEN users access the app THEN I SHALL see no CORS errors
- WHEN the backend starts THEN I SHALL see environment variables loaded correctly

## Success Metrics
- ✅ Frontend deploys successfully
- ✅ Backend API is accessible
- ✅ CORS configured correctly
- ✅ Auth placeholders in place

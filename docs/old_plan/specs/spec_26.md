# Spec 26 – Deploy backend service

This specification describes how to deploy the Python backend to Firebase Functions, Cloud Run or AWS ECS.  Choose one platform or adapt as needed.

## Option A: Cloud Run (recommended for containerized FastAPI apps)

1. **Dockerfile:** Create a `Dockerfile` at the project root:

   ```Dockerfile
   FROM python:3.10-slim
   WORKDIR /app
   COPY requirements.txt ./
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
   ```

2. **Build and push:** Use Google Cloud Build to build and push the image:

   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/knowledge-agent-backend
   ```

3. **Deploy to Cloud Run:**

   ```bash
   gcloud run deploy knowledge-agent-backend \
     --image gcr.io/PROJECT_ID/knowledge-agent-backend \
     --platform managed \
     --region REGION \
     --set-env-vars MODEL_PROVIDER_API_KEY=secret:MODEL_API_KEY,SEARCH_API_KEY=secret:SEARCH_API_KEY,... \
     --allow-unauthenticated
   ```

   Use Secret Manager to store sensitive variables and reference them via `secret:` notation.

## Option B: Firebase Functions (Python)

Firebase currently offers experimental support for Python functions.  To deploy:

1. Install the Firebase Functions Python runtime preview.
2. Place your FastAPI app under `functions/` and create a `requirements.txt` there.
3. Configure `functions.yaml` to specify the entry point and environment variables.
4. Deploy using `firebase deploy --only functions`.

This option may involve more boilerplate; Cloud Run is generally simpler for containerized apps.

## Option C: AWS ECS/Fargate

1. Define a Docker image as above and push it to ECR.
2. Create an ECS task definition specifying CPU, memory and environment variables from Secrets Manager.
3. Set up an ECS service behind an Application Load Balancer.
4. Configure auto‑scaling based on CPU or queue metrics.

## Environment Variables

Use your platform’s secret management service (Secret Manager, Parameter Store, Secrets Manager) to inject environment variables into the container.  Do not include the `.env` file in the image.

## Health Checks

Implement a `/health` endpoint in FastAPI that returns a 200 status.  Configure the platform to call this endpoint for health checks to ensure the service is running.

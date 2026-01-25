# 🚀 GCP Deployment Guide

This guide will help you deploy the Coffee Agent application to Google Cloud Platform.

## 📋 Prerequisites

- Google Cloud SDK installed and configured
- Docker installed locally
- Access to Google Cloud Platform
- API keys configured

## 🌐 Production URL

**Live Application**: (Update with your Cloud Run URL after deployment)

## 🛠️ Deployment Options

### Option 1: Google Cloud Run (Recommended)

#### 1. Build and Push Docker Image

```bash
# Set your project ID
export PROJECT_ID=your-project-id

# Build the image
docker build -t gcr.io/$PROJECT_ID/chat-bot-app .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/chat-bot-app
```

#### 2. Deploy to Cloud Run

```bash
# Deploy the service
gcloud run deploy chat-bot-app \
  --image gcr.io/$PROJECT_ID/chat-bot-app \
  --platform managed \
  --region us-west1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars FLASK_ENV=production
```

#### 3. Set Environment Variables

```bash
# Set environment variables in Cloud Run
gcloud run services update chat-bot-app \
  --region us-west1 \
  --set-env-vars OPENAI_API_KEY=your_key,SCALEKIT_CLIENT_ID=your_id,SCALEKIT_CLIENT_SECRET=your_secret,SCALEKIT_ENV_URL=https://kindle-dev.scalekit.cloud
```

### Option 2: Google Kubernetes Engine (GKE)

#### 1. Create Cluster

```bash
# Create GKE cluster
gcloud container clusters create chat-bot-cluster \
  --zone us-west1-a \
  --num-nodes 3 \
  --machine-type e2-medium
```

#### 2. Deploy with kubectl

```bash
# Get credentials
gcloud container clusters get-credentials chat-bot-cluster --zone us-west1-a

# Apply deployment
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-service.yaml
```

### Option 3: Compute Engine

#### 1. Create VM Instance

```bash
# Create VM with Docker
gcloud compute instances create-with-container chat-bot-vm \
  --container-image gcr.io/$PROJECT_ID/chat-bot-app \
  --machine-type e2-medium \
  --zone us-west1-a \
  --tags http-server,https-server
```

## 🔧 Environment Configuration

### Production Environment Variables

Create a `.env` file with production values:

```bash
# Copy environment template
cp env.template .env

# Edit with your actual values
nano .env
```

Required variables:
- `OPENAI_API_KEY`
- `SCALEKIT_CLIENT_ID`
- `SCALEKIT_CLIENT_SECRET`
- `SCALEKIT_ENV_URL`
- `FLASK_ENV=production`

## 📊 Monitoring & Logging

### Cloud Run Logs

```bash
# View logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=chat-bot-app" --limit 50
```

### Health Checks

The application includes health checks at:
- `GET /api/health`
- `GET /` (root endpoint)

## 🔒 Security Considerations

1. **Environment Variables**: Store sensitive data in Cloud Run environment variables
2. **HTTPS**: Cloud Run automatically provides HTTPS
3. **Authentication**: Consider adding authentication for production use
4. **CORS**: Configure CORS settings if needed

## 🚀 Quick Deploy Script

Create a `deploy.sh` script:

```bash
#!/bin/bash

# Set variables
PROJECT_ID="your-project-id"
REGION="us-west1"
SERVICE_NAME="chat-bot-app"

# Build and push
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10

echo "✅ Deployed to: https://$SERVICE_NAME-$(gcloud config get-value project).$REGION.run.app"
```

## 🔍 Troubleshooting

### Common Issues

1. **Container won't start**: Check logs with `gcloud logs read`
2. **Environment variables not loading**: Verify in Cloud Run console
3. **API errors**: Check API key configuration
4. **Memory issues**: Increase memory allocation

### Debug Commands

```bash
# Check service status
gcloud run services describe chat-bot-app --region us-west1

# View recent logs
gcloud logs read "resource.type=cloud_run_revision" --limit 20

# Test health endpoint
curl https://YOUR-SERVICE-NAME-PROJECT-ID.REGION.run.app/api/health
```

## 📈 Scaling

### Cloud Run Auto-scaling

- **Min instances**: 0 (scale to zero)
- **Max instances**: 10 (adjust based on traffic)
- **CPU**: 1 vCPU
- **Memory**: 1GB

### Manual Scaling

```bash
# Scale to specific number of instances
gcloud run services update chat-bot-app \
  --region us-west1 \
  --min-instances 1 \
  --max-instances 20
```

## 🔄 Continuous Deployment

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Google Cloud SDK
      uses: google-github-actions/setup-gcloud@v0
      with:
        project_id: ${{ secrets.GCP_PROJECT_ID }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
    
    - name: Build and Deploy
      run: |
        docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/chat-bot-app .
        docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/chat-bot-app
        gcloud run deploy chat-bot-app --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/chat-bot-app --region us-west1 --platform managed --allow-unauthenticated
```

## 📞 Support

For deployment issues:
1. Check Cloud Run logs
2. Verify environment variables
3. Test locally with Docker first
4. Review GCP documentation

---

**Production URL**: (Update with your Cloud Run URL after deployment)

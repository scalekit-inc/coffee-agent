#!/bin/bash

# GCP Deployment Script for Coffee Agent
echo "🚀 Deploying Coffee Agent to Google Cloud Platform..."

# Configuration - UPDATE THESE VALUES
PROJECT_ID="YOUR_GCP_PROJECT_ID"  # Your GCP project ID
REGION="us-west1"  # Your preferred region
SERVICE_NAME="coffee-agent"  # Your Cloud Run service name
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Check if gcloud is configured
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: Google Cloud SDK not found!"
    echo "Please install and configure gcloud CLI"
    exit 1
fi

# Check if project is set
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo "🔧 Setting project to: $PROJECT_ID"
    gcloud config set project $PROJECT_ID
fi

# Build Docker image
echo "🔨 Building Docker image..."
docker build -t $IMAGE_NAME .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

# Push to Google Container Registry
echo "📤 Pushing image to Google Container Registry..."
docker push $IMAGE_NAME

if [ $? -ne 0 ]; then
    echo "❌ Failed to push image!"
    exit 1
fi

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 8000 \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars FLASK_ENV=production

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
    echo "🌐 Your app is live at: $SERVICE_URL"
    echo ""
    echo "📋 Next steps:"
    echo "1. Set environment variables in Cloud Run console"
    echo "2. Test the application"
    echo "3. Monitor logs: gcloud logs read --limit 20"
else
    echo "❌ Deployment failed!"
    exit 1
fi

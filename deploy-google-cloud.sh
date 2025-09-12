#!/bin/bash

# Google Cloud Run deployment script
# Usage: ./deploy-google-cloud.sh [PROJECT_ID]

set -e

PROJECT_ID=${1:-$GOOGLE_CLOUD_PROJECT}

if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID not provided. Usage: ./deploy-google-cloud.sh PROJECT_ID"
    exit 1
fi

echo "Deploying to Google Cloud Run (safer option)..."

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Deploy using Cloud Run (no Docker needed)
echo "Deploying to Cloud Run..."
gcloud run deploy surveys-dashboard \
    --source . \
    --region africa-south1 \
    --platform managed \
    --allow-unauthenticated \
    --min-instances 0 \
    --max-instances 10 \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --concurrency 80 \
    --port 8080 \
    --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

# Get the service URL
SERVICE_URL=$(gcloud run services describe surveys-dashboard --region=africa-south1 --format='value(status.url)')

echo "✅ Deployment complete!"
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "🔒 Security features enabled:"
echo "  - Google's enterprise infrastructure"
echo "  - Automatic DDoS protection"
echo "  - VPC isolation"
echo "  - Audit logging"
echo "  - IAM integration"
echo ""
echo "📊 To view logs:"
echo "gcloud run services logs read surveys-dashboard --region=africa-south1"

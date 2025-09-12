# 🚀 Google Cloud Run Deployment Guide

## Prerequisites

1. **Google Cloud Project**: `ansebmrsurveysv1` (you already have this)
2. **Google Cloud SDK**: Install from [cloud.google.com/sdk](https://cloud.google.com/sdk)
3. **Authentication**: Your service account credentials are already configured

## Step 1: Install Google Cloud SDK

### Windows:
```bash
# Download and install from:
# https://cloud.google.com/sdk/docs/install
```

### Or use PowerShell:
```powershell
# Install via PowerShell
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& "$env:Temp\GoogleCloudSDKInstaller.exe"
```

## Step 2: Authenticate with Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project ansebmrsurveysv1

# Verify you're authenticated
gcloud auth list
```

## Step 3: Deploy to Cloud Run

```bash
# Run the deployment script
./deploy-google-cloud.sh ansebmrsurveysv1
```

## Step 4: Access Your App

After deployment, you'll get a URL like:
```
https://surveys-dashboard-[hash]-uc.a.run.app
```

## 🔒 Security Features Enabled

- ✅ **Enterprise Infrastructure**: Google's global network
- ✅ **DDoS Protection**: Automatic attack protection
- ✅ **VPC Isolation**: Private network
- ✅ **Audit Logging**: All actions logged
- ✅ **SSL/TLS**: Automatic HTTPS
- ✅ **Authentication**: Login required
- ✅ **Service Account**: Limited BigQuery permissions

## 📊 Monitoring Your App

### View Logs:
```bash
# Real-time logs
gcloud run services logs tail surveys-dashboard --region=africa-south1

# Historical logs
gcloud run services logs read surveys-dashboard --region=africa-south1
```

### Monitor Performance:
```bash
# View service details
gcloud run services describe surveys-dashboard --region=africa-south1
```

## 💰 Cost Optimization

- **Min Instances**: 0 (scales to zero when not in use)
- **Free Tier**: 2 million requests/month
- **Pay-per-use**: Only pay when people use your app

## 🔧 Troubleshooting

### If deployment fails:
1. Check you're authenticated: `gcloud auth list`
2. Verify project: `gcloud config get-value project`
3. Check APIs are enabled: `gcloud services list --enabled`

### If app doesn't work:
1. Check logs: `gcloud run services logs read surveys-dashboard --region=africa-south1`
2. Verify BigQuery permissions
3. Test locally first: `streamlit run app.py`

## 🎯 Next Steps

1. **Deploy**: Run `./deploy-google-cloud.sh ansebmrsurveysv1`
2. **Test**: Visit your app URL
3. **Monitor**: Check logs and performance
4. **Share**: Give users the URL and login credentials

Your app will be live on Google's enterprise infrastructure! 🎉

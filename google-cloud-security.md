# Google Cloud Run Security Features

## 🔒 **Why Google Cloud Run is Safer:**

### **Infrastructure Security:**
- **Google's Global Network**: Same infrastructure as Gmail, YouTube, Google Search
- **Automatic Security Updates**: Google handles all security patches
- **DDoS Protection**: Built-in protection against attacks
- **VPC Isolation**: Your app runs in a private network
- **Encryption**: All data encrypted in transit and at rest

### **Access Control:**
- **IAM Integration**: Fine-grained permissions
- **Service Account**: Limited permissions (only BigQuery access)
- **Audit Logging**: All actions are logged
- **Compliance**: SOC 2, ISO 27001, HIPAA certified

### **Monitoring & Alerting:**
- **Cloud Monitoring**: Real-time performance monitoring
- **Security Alerts**: Automatic threat detection
- **Log Analysis**: Centralized logging
- **Performance Insights**: Automatic optimization

## 🚀 **Deployment Options:**

### **Option 1: Public Access (Current)**
```bash
./deploy-google-cloud.sh YOUR_PROJECT_ID
```
- ✅ Anyone can access (with login)
- ✅ Good for public dashboards
- ✅ Lower cost

### **Option 2: Private Access (Most Secure)**
```bash
# Deploy with authentication required
gcloud run deploy surveys-dashboard \
    --source . \
    --region africa-south1 \
    --no-allow-unauthenticated \
    --ingress=internal
```
- ✅ Only Google Cloud users can access
- ✅ Enterprise-grade security
- ✅ Higher cost

### **Option 3: Custom Domain + Cloudflare**
```bash
# Add custom domain with Cloudflare Access
gcloud run domain-mappings create \
    --service surveys-dashboard \
    --domain dashboard.yourcompany.com \
    --region africa-south1
```
- ✅ Custom domain
- ✅ Cloudflare security features
- ✅ Professional appearance

## 💰 **Cost Comparison:**

### **Google Cloud Run:**
- **Free tier**: 2 million requests/month
- **Pay-per-use**: $0.40 per million requests
- **Memory**: $0.0000025 per GB-second
- **CPU**: $0.000024 per vCPU-second

### **Streamlit Cloud:**
- **Free tier**: Limited
- **Pro**: $20/month per app
- **Enterprise**: Custom pricing

## 🔧 **Security Best Practices:**

### **1. Service Account Permissions:**
```bash
# Your service account only has BigQuery access
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:seb-research-dashboard@ansebmrsurveysv1.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer"
```

### **2. Network Security:**
- **VPC**: Private network isolation
- **Firewall**: Automatic protection
- **SSL/TLS**: Automatic HTTPS

### **3. Data Protection:**
- **Encryption**: All data encrypted
- **Backup**: Automatic backups
- **Retention**: Configurable data retention

## 📊 **Monitoring & Alerts:**

### **Set up monitoring:**
```bash
# Create alerting policy
gcloud alpha monitoring policies create --policy-from-file=alert-policy.yaml
```

### **View logs:**
```bash
# Real-time logs
gcloud run services logs tail surveys-dashboard --region=africa-south1

# Historical logs
gcloud run services logs read surveys-dashboard --region=africa-south1
```

## 🎯 **Recommendation:**

**For maximum security, use Google Cloud Run because:**
1. **Enterprise infrastructure** (same as Google's services)
2. **Automatic security updates**
3. **DDoS protection**
4. **Audit logging**
5. **Compliance certifications**
6. **Fine-grained access control**

**Deploy with:**
```bash
chmod +x deploy-google-cloud.sh
./deploy-google-cloud.sh YOUR_PROJECT_ID
```

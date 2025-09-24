# Streamlit Community Cloud Deployment

## 🚀 Deploy Your Travel Log Dashboard

### Steps to Deploy:

1. **Push to GitHub:**
   - Create a GitHub repository
   - Push this code to the repository

2. **Deploy on Streamlit Cloud:**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file: `dashboard.py`
   - Click "Deploy!"

3. **Add Secrets:**
   - In your Streamlit Cloud app settings
   - Go to "Secrets"
   - Add your Google Sheets credentials as secrets:

```toml
# Streamlit secrets format
GOOGLE_SHEET_NAME = "Travel Log"
WORKSHEET_NAME = "Raw Data" 
TIMEZONE = "UTC"

# Add your credentials.json content here:
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nyour-private-key\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account-email"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
universe_domain = "googleapis.com"
```

### Features:
- ✅ **Free hosting** (up to certain usage limits)
- ✅ **Automatic HTTPS**
- ✅ **Custom URLs** available
- ✅ **Auto-deploys** when you push to GitHub
- ✅ **Access from anywhere** with internet
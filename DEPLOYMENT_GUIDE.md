# 🚀 Deployment Guide

Complete guide for deploying the TabPFN Production Pipeline to various platforms.

---

## 📋 Pre-Deployment Checklist

- [ ] All tests passing (`python quick_test.py`)
- [ ] Submission generated (`python generate_submission.py`)
- [ ] Docker builds successfully (`docker build -t tabpfn-api .`)
- [ ] Environment variables configured
- [ ] GitHub repository created

---

## 🐙 GitHub Deployment

### Step 1: Initialize Git Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: TabPFN Production Pipeline

- Complete ML pipeline with shift detection
- Calibration and conformal prediction
- Cost-aware inference routing
- FastAPI REST API
- Docker deployment
- Prometheus + Grafana monitoring
- Comprehensive documentation"

# Create GitHub repository (via GitHub CLI or web interface)
gh repo create tabpfn-production-pipeline --public --source=. --remote=origin

# Or manually add remote
git remote add origin https://github.com/YOUR_USERNAME/tabpfn-production-pipeline.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 2: Add GitHub Actions CI/CD

Create `.github/workflows/ci.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python quick_test.py
```

### Step 3: Update README with Badges

Add to top of README.md:
```markdown
[![CI/CD](https://github.com/YOUR_USERNAME/tabpfn-production-pipeline/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/YOUR_USERNAME/tabpfn-production-pipeline/actions)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://hub.docker.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
```

---

## ☁️ Cloud Deployment Options

### Option 1: Render.com (Easiest - Free Tier Available)

**Pros**: Free tier, automatic HTTPS, easy setup  
**Cons**: Cold starts on free tier

#### Steps:

1. **Push to GitHub** (see above)

2. **Create Render Account**: https://render.com

3. **Create New Web Service**:
   - Connect GitHub repository
   - Name: `tabpfn-api`
   - Environment: `Docker`
   - Region: Choose closest to you
   - Branch: `main`
   - Build Command: (auto-detected from Dockerfile)
   - Start Command: (auto-detected)

4. **Environment Variables** (optional):
   ```
   PYTHONUNBUFFERED=1
   PORT=8000
   ```

5. **Deploy**: Click "Create Web Service"

6. **Your Live URL**: `https://tabpfn-api-XXXX.onrender.com`

#### Test Your Deployment:
```bash
curl https://tabpfn-api-XXXX.onrender.com/health
```

---

### Option 2: Railway.app (Easy - Free Trial)

**Pros**: Easy deployment, good free tier  
**Cons**: Limited free credits

#### Steps:

1. **Create Railway Account**: https://railway.app

2. **New Project** → **Deploy from GitHub**

3. **Select Repository**: `tabpfn-production-pipeline`

4. **Configure**:
   - Dockerfile detected automatically
   - Port: 8000
   - Health check: `/health`

5. **Generate Domain**: Railway provides `*.railway.app` domain

6. **Your Live URL**: `https://tabpfn-api-production.up.railway.app`

---

### Option 3: Fly.io (Recommended for Production)

**Pros**: Global edge deployment, good free tier  
**Cons**: Requires CLI installation

#### Steps:

1. **Install Fly CLI**:
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # Mac/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**:
   ```bash
   fly auth login
   ```

3. **Launch App**:
   ```bash
   fly launch
   # Follow prompts:
   # - App name: tabpfn-api
   # - Region: Choose closest
   # - PostgreSQL: No
   # - Redis: No
   ```

4. **Deploy**:
   ```bash
   fly deploy
   ```

5. **Your Live URL**: `https://tabpfn-api.fly.dev`

6. **Scale** (optional):
   ```bash
   fly scale count 2  # 2 instances
   fly scale vm shared-cpu-1x  # Upgrade VM
   ```

---

### Option 4: Google Cloud Run (Serverless)

**Pros**: Pay per use, auto-scaling, Google infrastructure  
**Cons**: Requires GCP account

#### Steps:

1. **Install Google Cloud SDK**:
   ```bash
   # Download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Authenticate**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Build and Push to Container Registry**:
   ```bash
   # Build
   docker build -t gcr.io/YOUR_PROJECT_ID/tabpfn-api .
   
   # Push
   docker push gcr.io/YOUR_PROJECT_ID/tabpfn-api
   ```

4. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy tabpfn-api \
     --image gcr.io/YOUR_PROJECT_ID/tabpfn-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8000
   ```

5. **Your Live URL**: Provided in output (e.g., `https://tabpfn-api-XXXX-uc.a.run.app`)

---

### Option 5: AWS ECS (Enterprise)

**Pros**: Full AWS ecosystem, highly scalable  
**Cons**: More complex setup, costs

#### Quick Setup with Copilot:

```bash
# Install AWS Copilot
curl -Lo copilot https://github.com/aws/copilot-cli/releases/latest/download/copilot-linux
chmod +x copilot

# Initialize
copilot init

# Deploy
copilot deploy
```

---

### Option 6: Heroku (Classic)

**Pros**: Simple, well-documented  
**Cons**: No free tier anymore

#### Steps:

1. **Install Heroku CLI**:
   ```bash
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login**:
   ```bash
   heroku login
   ```

3. **Create App**:
   ```bash
   heroku create tabpfn-api
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

5. **Your Live URL**: `https://tabpfn-api.herokuapp.com`

---

## 🌐 Frontend Deployment (GitHub Pages)

Deploy the interactive frontend for free:

### Steps:

1. **Create `docs/` folder**:
   ```bash
   mkdir docs
   cp frontend/index.html docs/
   ```

2. **Update API URL in `docs/index.html`**:
   ```javascript
   const API_URL = 'https://YOUR-API-URL.com';  // Update this
   ```

3. **Commit and Push**:
   ```bash
   git add docs/
   git commit -m "Add frontend for GitHub Pages"
   git push
   ```

4. **Enable GitHub Pages**:
   - Go to repository Settings
   - Pages section
   - Source: `main` branch, `/docs` folder
   - Save

5. **Your Live Frontend**: `https://YOUR_USERNAME.github.io/tabpfn-production-pipeline/`

---

## 🔧 Environment Variables

For production deployment, set these environment variables:

```bash
# Required
PORT=8000
PYTHONUNBUFFERED=1

# Optional
LOG_LEVEL=INFO
MAX_WORKERS=4
TIMEOUT=300

# For monitoring (if using external services)
PROMETHEUS_MULTIPROC_DIR=/tmp
```

---

## 📊 Monitoring Setup

### Option 1: Grafana Cloud (Free Tier)

1. **Sign up**: https://grafana.com/products/cloud/
2. **Get Prometheus endpoint**
3. **Configure remote write** in `monitoring/prometheus.yml`:
   ```yaml
   remote_write:
     - url: https://prometheus-prod-XX.grafana.net/api/prom/push
       basic_auth:
         username: YOUR_USERNAME
         password: YOUR_API_KEY
   ```

### Option 2: Self-Hosted with Docker Compose

Already configured! Just run:
```bash
docker-compose up -d
```

Access:
- Prometheus: `http://YOUR_DOMAIN:9090`
- Grafana: `http://YOUR_DOMAIN:3000`

---

## 🧪 Testing Your Deployment

### Health Check:
```bash
curl https://YOUR_API_URL/health
```

### Make Prediction:
```bash
curl -X POST "https://YOUR_API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [[2.42, 0.15, 0.0, 0.13, 49.32, 31.41, 3.66, -0.37, 1.42, 0.0, 0.05, 0.13, 1.05, 0.01, 0.19, -33.07, 22.83, 6.09, 0.76, 0.01, 0.39, 0.65, 0.63, 0.63, 0.80, 3.30, 0.50, 0.0, 0.0, 0.0, 1.14, 1.16, 0.05, 0.02, 0.01, 0.04, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 7.52, 0.0, 0.43, 0.56, 0.0, 0.58, 0.91, 254.72]],
    "use_calibration": true
  }'
```

### Check Metrics:
```bash
curl https://YOUR_API_URL/metrics
```

---

## 🔒 Security Considerations

### For Production:

1. **Add Authentication**:
   ```python
   # In src/api.py
   from fastapi.security import HTTPBearer
   
   security = HTTPBearer()
   
   @app.post("/predict")
   async def predict(request: PredictionRequest, token: str = Depends(security)):
       # Verify token
       pass
   ```

2. **Rate Limiting**:
   ```python
   from slowapi import Limiter
   
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/predict")
   @limiter.limit("100/minute")
   async def predict(...):
       pass
   ```

3. **CORS Configuration**:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       allow_methods=["GET", "POST"],
   )
   ```

4. **HTTPS Only**: Most platforms provide this automatically

---

## 📈 Scaling Recommendations

### For High Traffic:

1. **Horizontal Scaling**:
   - Multiple instances behind load balancer
   - Use platform's auto-scaling features

2. **Caching**:
   - Add Redis for prediction caching
   - Cache model in memory

3. **Async Processing**:
   - Use Celery for batch predictions
   - Queue system for high-volume requests

4. **Database**:
   - Add PostgreSQL for prediction logging
   - Store metrics for analysis

---

## 🎯 Recommended Deployment Path

**For Demo/Testing**: Render.com or Railway.app (Free)  
**For Production**: Fly.io or Google Cloud Run  
**For Enterprise**: AWS ECS or GCP with Kubernetes

---

## 📞 Support & Troubleshooting

### Common Issues:

1. **Port Binding Error**:
   - Ensure `PORT` environment variable is set
   - Check Dockerfile exposes correct port

2. **Memory Issues**:
   - Increase container memory limit
   - Use smaller model or batch size

3. **Cold Starts**:
   - Use paid tier for always-on instances
   - Implement health check pinging

4. **CORS Errors**:
   - Configure CORS middleware
   - Check allowed origins

---

## ✅ Post-Deployment Checklist

- [ ] API health check returns 200
- [ ] Prediction endpoint works
- [ ] Metrics endpoint accessible
- [ ] Frontend deployed and connected
- [ ] Monitoring configured
- [ ] Documentation updated with live URLs
- [ ] README badges updated
- [ ] Security measures in place
- [ ] Backup strategy defined
- [ ] Scaling plan documented

---

## 🔗 Quick Links Template

Update your README with:

```markdown
## 🌐 Live Demo

- **API**: https://YOUR_API_URL.com
- **API Docs**: https://YOUR_API_URL.com/docs
- **Frontend**: https://YOUR_USERNAME.github.io/tabpfn-production-pipeline/
- **Monitoring**: https://YOUR_GRAFANA_URL.com

## 🧪 Try It Out

```bash
curl https://YOUR_API_URL.com/health
```
```

---

**Ready to deploy!** Choose your platform and follow the steps above.

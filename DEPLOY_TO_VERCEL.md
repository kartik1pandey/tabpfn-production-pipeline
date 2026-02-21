# 🚀 Deploy to GitHub + Vercel (Free)

Complete guide to deploy your TabPFN Production Pipeline for free!

---

## 📋 What You'll Get

- ✅ **GitHub Repository**: Public repo with your code
- ✅ **Vercel API**: Free serverless API deployment
- ✅ **GitHub Pages**: Free frontend hosting
- ✅ **Live Demo**: Shareable links to show off your work

**Total Cost**: $0 (100% Free!)

---

## 🐙 Step 1: Push to GitHub

### Option A: Using GitHub CLI (Recommended)

```bash
# Install GitHub CLI if needed
# Windows: winget install GitHub.cli
# Mac: brew install gh

# Login
gh auth login

# Initialize and push
git init
git add .
git commit -m "feat: TabPFN Production Pipeline

Complete ML pipeline with:
- Shift detection (99% AUC)
- Calibration (100% ECE improvement)  
- Conformal prediction (90% coverage)
- FastAPI REST API
- Real dataset (1442 samples, 53 features)
- Comprehensive documentation"

# Create repo and push
gh repo create tabpfn-production-pipeline --public --source=. --remote=origin --push
```

### Option B: Manual Setup

```bash
# 1. Create repo at https://github.com/new
#    Name: tabpfn-production-pipeline
#    Public, no README

# 2. Initialize git
git init
git add .
git commit -m "feat: TabPFN Production Pipeline"

# 3. Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/tabpfn-production-pipeline.git

# 4. Push
git branch -M main
git push -u origin main
```

---

## ☁️ Step 2: Deploy API to Vercel

### Quick Deploy (3 clicks!)

1. **Go to**: https://vercel.com/new

2. **Import Git Repository**:
   - Click "Import Git Repository"
   - Select your `tabpfn-production-pipeline` repo
   - Click "Import"

3. **Configure Project**:
   - Framework Preset: **Other**
   - Root Directory: `./`
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: `pip install -r requirements-vercel.txt`

4. **Deploy**:
   - Click "Deploy"
   - Wait ~2 minutes

5. **Your API is Live!**
   - URL: `https://tabpfn-production-pipeline.vercel.app`
   - Or custom: `https://YOUR_PROJECT.vercel.app`

### Test Your API

```bash
# Health check
curl https://YOUR_PROJECT.vercel.app/health

# API docs
open https://YOUR_PROJECT.vercel.app/docs
```

---

## 🎨 Step 3: Deploy Frontend to GitHub Pages

### Setup

```bash
# 1. Create docs folder
mkdir docs
cp frontend/index.html docs/

# 2. Update API URL in docs/index.html
# Find this line:
#   const API_URL = window.location.hostname === 'localhost' 
#       ? 'http://localhost:8000'
#       : 'https://tabpfn-api.fly.dev';
# 
# Change to:
#   const API_URL = 'https://YOUR_PROJECT.vercel.app';

# 3. Commit and push
git add docs/
git commit -m "feat: add frontend for GitHub Pages"
git push
```

### Enable GitHub Pages

1. Go to your repo on GitHub
2. **Settings** → **Pages**
3. **Source**: Deploy from a branch
4. **Branch**: `main`, folder: `/docs`
5. **Save**
6. Wait ~1 minute

**Your Frontend**: `https://YOUR_USERNAME.github.io/tabpfn-production-pipeline/`

---

## 🔧 Step 4: Update README with Live Links

Add this to the top of your `README.md`:

```markdown
# TabPFN Production Pipeline

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/YOUR_USERNAME/tabpfn-production-pipeline)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-success)](https://YOUR_PROJECT.vercel.app)
[![Demo](https://img.shields.io/badge/Demo-Live-brightgreen)](https://YOUR_USERNAME.github.io/tabpfn-production-pipeline/)

## 🌐 Live Demo

- **🎨 Interactive Frontend**: https://YOUR_USERNAME.github.io/tabpfn-production-pipeline/
- **🔌 API Endpoint**: https://YOUR_PROJECT.vercel.app
- **📚 API Documentation**: https://YOUR_PROJECT.vercel.app/docs
- **📊 Health Check**: https://YOUR_PROJECT.vercel.app/health

## 🧪 Try It Now

```bash
# Health check
curl https://YOUR_PROJECT.vercel.app/health

# Make prediction
curl -X POST "https://YOUR_PROJECT.vercel.app/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": [[2.42, 0.15, ...]], "use_calibration": true}'
```
```

Commit and push:
```bash
git add README.md
git commit -m "docs: add live demo links"
git push
```

---

## 🧪 Step 5: Test Everything

### Test API Endpoints

```bash
# Set your URL
export API_URL="https://YOUR_PROJECT.vercel.app"

# Health check
curl $API_URL/health

# Prediction
curl -X POST "$API_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "features": [[2.42, 0.15, 0.0, 0.13, 49.32, 31.41, 3.66, -0.37, 1.42, 0.0, 0.05, 0.13, 1.05, 0.01, 0.19, -33.07, 22.83, 6.09, 0.76, 0.01, 0.39, 0.65, 0.63, 0.63, 0.80, 3.30, 0.50, 0.0, 0.0, 0.0, 1.14, 1.16, 0.05, 0.02, 0.01, 0.04, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 7.52, 0.0, 0.43, 0.56, 0.0, 0.58, 0.91, 254.72]],
    "use_calibration": true
  }'

# Metrics
curl $API_URL/metrics
```

### Test Frontend

1. Open: `https://YOUR_USERNAME.github.io/tabpfn-production-pipeline/`
2. Click "Refresh Status" - should show "Online"
3. Click "Make Prediction" - should return results

---

## 📊 What's Deployed

### Repository Structure (Clean)

```
tabpfn-production-pipeline/
├── src/                    # Core pipeline code
│   ├── data_loader.py
│   ├── shift_detector.py
│   ├── calibration.py
│   ├── conformal.py
│   ├── predictors.py
│   └── api.py
├── api/                    # Vercel entry point
│   └── index.py
├── docs/                   # GitHub Pages frontend
│   └── index.html
├── dataset/                # Real data
│   ├── train.csv
│   ├── test.csv
│   └── sample_submission.csv
├── results/                # Outputs
│   └── submission.csv
├── requirements.txt        # Full dependencies
├── requirements-vercel.txt # Vercel dependencies
├── vercel.json            # Vercel config
├── README.md              # Documentation
└── .gitignore             # Git ignore rules
```

### What's NOT Pushed (Clean Repo)

- ❌ `venv/` - Virtual environment
- ❌ `__pycache__/` - Python cache
- ❌ `.vscode/` - IDE settings
- ❌ `results/*.json` - Experiment outputs
- ❌ Large model files

---

## 🎯 Vercel Limits (Free Tier)

- ✅ **Bandwidth**: 100 GB/month
- ✅ **Invocations**: 100,000/month
- ✅ **Execution Time**: 10 seconds max
- ✅ **Memory**: 1024 MB
- ✅ **Custom Domain**: Yes (free)

**Perfect for demos and portfolios!**

---

## 🔄 Continuous Deployment

### Automatic Updates

Vercel automatically redeploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "feat: add new feature"
git push

# Vercel automatically deploys!
# Check: https://vercel.com/dashboard
```

### GitHub Pages Updates

```bash
# Update frontend
git add docs/
git commit -m "feat: update frontend"
git push

# GitHub Pages automatically updates!
```

---

## 🎨 Customize Your Deployment

### Add Custom Domain (Optional)

1. Go to Vercel Dashboard
2. Select your project
3. **Settings** → **Domains**
4. Add your domain
5. Update DNS records

### Environment Variables

1. Vercel Dashboard → Your Project
2. **Settings** → **Environment Variables**
3. Add variables:
   - `PYTHONUNBUFFERED=1`
   - `LOG_LEVEL=INFO`

---

## 📱 Share Your Project

### Social Media Post Template

```
🚀 Just deployed my ML pipeline!

✨ Features:
- Distribution shift detection (99% AUC)
- Calibration & conformal prediction
- Cost-aware inference routing
- FastAPI + Vercel deployment

🔗 Try it: https://YOUR_USERNAME.github.io/tabpfn-production-pipeline/
📦 Code: https://github.com/YOUR_USERNAME/tabpfn-production-pipeline

#MachineLearning #MLOps #Python #FastAPI #Vercel
```

### Add to Portfolio

```markdown
## TabPFN Production Pipeline

A production-ready ML pipeline for financial default prediction with distribution 
shift detection, calibration, and conformal prediction.

**Tech Stack**: Python, FastAPI, LightGBM, Docker, Vercel  
**Live Demo**: [Try it here](https://YOUR_USERNAME.github.io/tabpfn-production-pipeline/)  
**Source Code**: [GitHub](https://github.com/YOUR_USERNAME/tabpfn-production-pipeline)

**Key Features**:
- 99% AUC on shift detection
- 100% ECE improvement with calibration
- 90% conformal prediction coverage
- Production-ready API with monitoring
```

---

## 🐛 Troubleshooting

### Vercel Build Fails

**Issue**: Dependencies too large  
**Solution**: Use `requirements-vercel.txt` (already configured)

**Issue**: Import errors  
**Solution**: Check `api/index.py` path configuration

### Frontend Can't Connect to API

**Issue**: CORS errors  
**Solution**: API already has CORS configured in `src/api.py`

**Issue**: Wrong API URL  
**Solution**: Update `docs/index.html` with your Vercel URL

### GitHub Pages Not Working

**Issue**: 404 error  
**Solution**: Check Settings → Pages → Source is set to `/docs`

**Issue**: Old version showing  
**Solution**: Clear browser cache or wait 1-2 minutes

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Vercel project created and deployed
- [ ] API health check returns 200
- [ ] Frontend deployed to GitHub Pages
- [ ] Frontend connects to API successfully
- [ ] README updated with live URLs
- [ ] Badges added to README
- [ ] All endpoints tested
- [ ] Project shared (optional)

---

## 🎉 You're Live!

Your TabPFN Production Pipeline is now:
- ✅ On GitHub (public repository)
- ✅ API deployed on Vercel (free)
- ✅ Frontend on GitHub Pages (free)
- ✅ Fully functional and shareable!

**Total Time**: ~10 minutes  
**Total Cost**: $0

---

## 📞 Need Help?

- **Vercel Docs**: https://vercel.com/docs
- **GitHub Pages**: https://pages.github.com/
- **Issues**: Open an issue on your GitHub repo

---

**Ready to deploy?** Follow the steps above and you'll be live in 10 minutes! 🚀

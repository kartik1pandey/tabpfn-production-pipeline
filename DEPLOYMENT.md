# 🚀 Deployment Guide

## Quick Deploy to Vercel (2 minutes)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "fix: ultra-lightweight Vercel deployment"
git push origin main
```

### Step 2: Deploy on Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "Add New" → "Project"
3. Import: `kartik1pandey/tabpfn-production-pipeline`
4. Click "Deploy"
5. Wait 2-3 minutes

### Step 3: Test Your API
Your API will be at: `https://tabpfn-production-pipeline.vercel.app`

Test endpoints:
- Health: `https://your-url.vercel.app/health`
- Docs: `https://your-url.vercel.app/docs`
- Predict: POST to `https://your-url.vercel.app/predict`

---

## What's Deployed on Vercel?

✅ **Working:**
- FastAPI endpoints (/health, /predict, /detect_shift, /metrics)
- Interactive API docs (/docs)
- CORS enabled for frontend
- Demo predictions using simple heuristics

⚠️ **Limitations:**
- No trained ML models (Vercel 50 MB limit)
- Demo predictions only (not using LightGBM/TabPFN)
- Simplified shift detection

---

## For Full Functionality

Use Docker deployment locally or on container platforms:

```bash
# Run locally with Docker
docker-compose up

# Access at http://localhost:8000
```

Deploy to platforms that support Docker:
- **Fly.io** (free tier)
- **Render.com** (free tier)
- **Railway** (free tier)

---

## Enable GitHub Pages (Frontend)

1. Go to GitHub repo → Settings → Pages
2. Source: Deploy from branch
3. Branch: `main`, Folder: `/frontend`
4. Save

Frontend URL: `https://kartik1pandey.github.io/tabpfn-production-pipeline/`

---

## Files Changed for Vercel

| File | Change | Why |
|------|--------|-----|
| `requirements.txt` | Only 3 packages | Reduce bundle size from 8237 MB to ~50 MB |
| `api/index.py` | Import from `api_vercel.py` | Avoid loading heavy models |
| `src/api_vercel.py` | Lightweight demo API | Works within Vercel limits |

---

## Troubleshooting

**Deployment still fails?**
1. Check Vercel build logs
2. Verify `requirements.txt` has only 3 packages
3. Ensure `api/index.py` imports from `api_vercel.py`
4. Try redeploying from Vercel dashboard

**Need full model predictions?**
- Use Docker: `docker-compose up`
- Deploy to Render.com or Railway
- Run locally: `uvicorn src.api:app --reload`

---

## Summary

- ✅ Vercel = Quick demo (no models, fast deployment)
- ✅ Docker = Full functionality (all models, local/cloud)
- ✅ GitHub Pages = Frontend hosting (free)

**Ready to deploy!** Follow Step 1 above to push and deploy.

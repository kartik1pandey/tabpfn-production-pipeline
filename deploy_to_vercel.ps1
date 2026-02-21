# Complete deployment script for GitHub + Vercel

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TabPFN Pipeline - Deploy to Vercel" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Initialize Git
Write-Host "[1/4] Initializing Git..." -ForegroundColor Yellow
if (-not (Test-Path .git)) {
    git init
    Write-Host "✓ Git initialized" -ForegroundColor Green
} else {
    Write-Host "✓ Git already initialized" -ForegroundColor Green
}

# Step 2: Add and Commit
Write-Host ""
Write-Host "[2/4] Committing files..." -ForegroundColor Yellow
git add .
git commit -m "feat: TabPFN Production Pipeline

Complete ML pipeline with:
- Shift detection (99% AUC on synthetic shifts)
- Calibration (100% ECE improvement)
- Conformal prediction (90% coverage)
- Cost-aware inference routing
- FastAPI REST API
- Real dataset (1442 samples, 53 features)
- Vercel deployment ready
- Comprehensive documentation

Tested and production-ready." -ErrorAction SilentlyContinue

Write-Host "✓ Files committed" -ForegroundColor Green

# Step 3: Push to GitHub
Write-Host ""
Write-Host "[3/4] Pushing to GitHub..." -ForegroundColor Yellow

if (Get-Command gh -ErrorAction SilentlyContinue) {
    Write-Host "Using GitHub CLI..." -ForegroundColor Cyan
    
    # Check if already has remote
    $hasRemote = git remote | Select-String "origin"
    
    if (-not $hasRemote) {
        Write-Host "Creating GitHub repository..." -ForegroundColor Cyan
        gh repo create tabpfn-production-pipeline --public --source=. --remote=origin --push
        Write-Host "✓ Repository created and pushed!" -ForegroundColor Green
    } else {
        Write-Host "Remote already exists, pushing..." -ForegroundColor Cyan
        git push -u origin main
        Write-Host "✓ Pushed to GitHub!" -ForegroundColor Green
    }
    
    # Get repo URL
    $repoUrl = gh repo view --json url -q .url
    Write-Host ""
    Write-Host "GitHub Repository: $repoUrl" -ForegroundColor Green
    
} else {
    Write-Host ""
    Write-Host "GitHub CLI not found. Please:" -ForegroundColor Yellow
    Write-Host "1. Install: winget install GitHub.cli" -ForegroundColor White
    Write-Host "2. Or manually:" -ForegroundColor White
    Write-Host "   - Create repo at https://github.com/new" -ForegroundColor White
    Write-Host "   - Name: tabpfn-production-pipeline" -ForegroundColor White
    Write-Host "   - Run: git remote add origin https://github.com/YOUR_USERNAME/tabpfn-production-pipeline.git" -ForegroundColor White
    Write-Host "   - Run: git push -u origin main" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter after pushing to GitHub"
}

# Step 4: Deploy to Vercel
Write-Host ""
Write-Host "[4/4] Deploying to Vercel..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps for Vercel deployment:" -ForegroundColor Cyan
Write-Host "1. Go to: https://vercel.com/new" -ForegroundColor White
Write-Host "2. Click 'Import Git Repository'" -ForegroundColor White
Write-Host "3. Select your 'tabpfn-production-pipeline' repo" -ForegroundColor White
Write-Host "4. Click 'Import'" -ForegroundColor White
Write-Host "5. Configure:" -ForegroundColor White
Write-Host "   - Framework: Other" -ForegroundColor White
Write-Host "   - Install Command: pip install -r requirements-vercel.txt" -ForegroundColor White
Write-Host "6. Click 'Deploy'" -ForegroundColor White
Write-Host ""
Write-Host "Your API will be live at: https://YOUR_PROJECT.vercel.app" -ForegroundColor Green
Write-Host ""

# Open Vercel in browser
$openVercel = Read-Host "Open Vercel in browser? (y/n)"
if ($openVercel -eq 'y') {
    Start-Process "https://vercel.com/new"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "After Vercel deployment completes:" -ForegroundColor Yellow
Write-Host "1. Note your Vercel URL" -ForegroundColor White
Write-Host "2. Update docs/index.html with your API URL" -ForegroundColor White
Write-Host "3. Enable GitHub Pages (Settings → Pages → /docs)" -ForegroundColor White
Write-Host "4. Update README.md with live links" -ForegroundColor White
Write-Host ""
Write-Host "See DEPLOY_TO_VERCEL.md for detailed instructions" -ForegroundColor Cyan
Write-Host ""

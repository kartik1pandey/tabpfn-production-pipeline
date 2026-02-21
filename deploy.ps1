# TabPFN Production Pipeline - Quick Deploy Script (PowerShell)
# This script helps you deploy to various platforms

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "TabPFN Pipeline - Quick Deploy" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
    git add .
    git commit -m "Initial commit: TabPFN Production Pipeline"
}

# Menu
Write-Host "Choose deployment platform:" -ForegroundColor Green
Write-Host "1) GitHub only (push code)"
Write-Host "2) Fly.io (recommended)"
Write-Host "3) Render.com"
Write-Host "4) Railway.app"
Write-Host "5) All of the above"
Write-Host ""
$choice = Read-Host "Enter choice [1-5]"

switch ($choice) {
    {$_ -in 1,5} {
        Write-Host ""
        Write-Host "=== Pushing to GitHub ===" -ForegroundColor Cyan
        if (Get-Command gh -ErrorAction SilentlyContinue) {
            Write-Host "Using GitHub CLI..." -ForegroundColor Yellow
            gh repo create tabpfn-production-pipeline --public --source=. --remote=origin --push
        } else {
            Write-Host "GitHub CLI not found. Please:" -ForegroundColor Yellow
            Write-Host "1. Create repo at https://github.com/new"
            Write-Host "2. Run: git remote add origin https://github.com/YOUR_USERNAME/tabpfn-production-pipeline.git"
            Write-Host "3. Run: git push -u origin main"
        }
    }
}

switch ($choice) {
    {$_ -in 2,5} {
        Write-Host ""
        Write-Host "=== Deploying to Fly.io ===" -ForegroundColor Cyan
        if (Get-Command fly -ErrorAction SilentlyContinue) {
            fly launch --now
            Write-Host ""
            Write-Host "✅ Deployed to Fly.io!" -ForegroundColor Green
            $hostname = (fly info --json | ConvertFrom-Json).Hostname
            Write-Host "Your API: https://$hostname" -ForegroundColor Green
        } else {
            Write-Host "Fly CLI not found." -ForegroundColor Yellow
            Write-Host "Install with: iwr https://fly.io/install.ps1 -useb | iex" -ForegroundColor Yellow
        }
    }
}

switch ($choice) {
    {$_ -in 3,5} {
        Write-Host ""
        Write-Host "=== Render.com Deployment ===" -ForegroundColor Cyan
        Write-Host "1. Go to https://render.com"
        Write-Host "2. New → Web Service"
        Write-Host "3. Connect your GitHub repo"
        Write-Host "4. Deploy!"
    }
}

switch ($choice) {
    {$_ -in 4,5} {
        Write-Host ""
        Write-Host "=== Railway.app Deployment ===" -ForegroundColor Cyan
        Write-Host "1. Go to https://railway.app"
        Write-Host "2. New Project → Deploy from GitHub"
        Write-Host "3. Select your repo"
        Write-Host "4. Deploy!"
    }
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update README.md with your live URLs"
Write-Host "2. Deploy frontend to GitHub Pages"
Write-Host "3. Test your API"
Write-Host ""
Write-Host "See GITHUB_SETUP.md for detailed instructions" -ForegroundColor Cyan

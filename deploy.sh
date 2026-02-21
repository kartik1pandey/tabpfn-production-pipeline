#!/bin/bash

# TabPFN Production Pipeline - Quick Deploy Script
# This script helps you deploy to various platforms

set -e

echo "=================================="
echo "TabPFN Pipeline - Quick Deploy"
echo "=================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: TabPFN Production Pipeline"
fi

# Menu
echo "Choose deployment platform:"
echo "1) GitHub only (push code)"
echo "2) Fly.io (recommended)"
echo "3) Render.com"
echo "4) Railway.app"
echo "5) All of the above"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
    1|5)
        echo ""
        echo "=== Pushing to GitHub ==="
        if command -v gh &> /dev/null; then
            echo "Using GitHub CLI..."
            gh repo create tabpfn-production-pipeline --public --source=. --remote=origin --push || true
        else
            echo "GitHub CLI not found. Please:"
            echo "1. Create repo at https://github.com/new"
            echo "2. Run: git remote add origin https://github.com/YOUR_USERNAME/tabpfn-production-pipeline.git"
            echo "3. Run: git push -u origin main"
        fi
        ;;
esac

case $choice in
    2|5)
        echo ""
        echo "=== Deploying to Fly.io ==="
        if command -v fly &> /dev/null; then
            fly launch --now
            echo ""
            echo "✅ Deployed to Fly.io!"
            echo "Your API: https://$(fly info --json | jq -r '.Hostname')"
        else
            echo "Fly CLI not found. Install from: https://fly.io/docs/hands-on/install-flyctl/"
        fi
        ;;
esac

case $choice in
    3|5)
        echo ""
        echo "=== Render.com Deployment ==="
        echo "1. Go to https://render.com"
        echo "2. New → Web Service"
        echo "3. Connect your GitHub repo"
        echo "4. Deploy!"
        ;;
esac

case $choice in
    4|5)
        echo ""
        echo "=== Railway.app Deployment ==="
        echo "1. Go to https://railway.app"
        echo "2. New Project → Deploy from GitHub"
        echo "3. Select your repo"
        echo "4. Deploy!"
        ;;
esac

echo ""
echo "=================================="
echo "Deployment Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Update README.md with your live URLs"
echo "2. Deploy frontend to GitHub Pages"
echo "3. Test your API"
echo ""
echo "See GITHUB_SETUP.md for detailed instructions"

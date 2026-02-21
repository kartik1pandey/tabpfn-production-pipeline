# Prepare repository for GitHub - Clean and organized

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Preparing for GitHub" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "✓ Initializing git repository..." -ForegroundColor Green
    git init
} else {
    Write-Host "✓ Git already initialized" -ForegroundColor Green
}

# Clean up unnecessary files
Write-Host ""
Write-Host "Cleaning up..." -ForegroundColor Yellow

# Remove large/unnecessary files if they exist
$filesToRemove = @(
    "*.pyc",
    "__pycache__",
    ".pytest_cache",
    "*.log"
)

foreach ($pattern in $filesToRemove) {
    Get-ChildItem -Path . -Filter $pattern -Recurse -ErrorAction SilentlyContinue | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
}

Write-Host "✓ Cleaned up temporary files" -ForegroundColor Green

# Show what will be committed
Write-Host ""
Write-Host "Files to be committed:" -ForegroundColor Cyan
Write-Host "  ✓ src/ - Core pipeline code" -ForegroundColor White
Write-Host "  ✓ api/ - Vercel entry point" -ForegroundColor White
Write-Host "  ✓ frontend/ - Web interface" -ForegroundColor White
Write-Host "  ✓ dataset/ - Real data" -ForegroundColor White
Write-Host "  ✓ results/ - Submission file" -ForegroundColor White
Write-Host "  ✓ Documentation files" -ForegroundColor White
Write-Host "  ✓ Configuration files" -ForegroundColor White

Write-Host ""
Write-Host "Files excluded (via .gitignore):" -ForegroundColor Cyan
Write-Host "  ✗ venv/ - Virtual environment" -ForegroundColor DarkGray
Write-Host "  ✗ __pycache__/ - Python cache" -ForegroundColor DarkGray
Write-Host "  ✗ .vscode/ - IDE settings" -ForegroundColor DarkGray
Write-Host "  ✗ results/*.json - Experiment outputs" -ForegroundColor DarkGray

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Ready to commit!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Review files: git status"
Write-Host "2. Add files: git add ."
Write-Host "3. Commit: git commit -m 'feat: TabPFN Production Pipeline'"
Write-Host "4. Push to GitHub: See DEPLOY_TO_VERCEL.md"
Write-Host ""
Write-Host "Or run the full deployment:" -ForegroundColor Yellow
Write-Host "  .\deploy_to_vercel.ps1"
Write-Host ""

"""Vercel serverless function entry point."""
import sys
import os
from pathlib import Path

# Add parent directory to path
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import the lightweight FastAPI app for Vercel
from src.api_vercel import app

# Export for Vercel
handler = app

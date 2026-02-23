"""
Shared configuration for loader and main app
"""
import os

# Backend URL (used by loader)
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Callback port (used by loader)
CALLBACK_PORT = int(os.getenv("CALLBACK_PORT", "8080"))

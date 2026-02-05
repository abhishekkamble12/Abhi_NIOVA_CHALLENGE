#!/usr/bin/env python3
"""
Racing Demo Backend - Development Server
"""

import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
        reload_dirs=["app"],
        log_level="info",
        access_log=True,
        use_colors=True,
    )
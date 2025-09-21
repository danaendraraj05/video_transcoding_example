"""
FastAPI entry point for transcode_video_example.

This file serves as the entry point for running the FastAPI application.
Run with: uvicorn api:app --reload
"""

from app.api.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
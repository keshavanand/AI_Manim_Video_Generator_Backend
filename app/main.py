# FastAPI app entry point
from fastapi import FastAPI
from app.api.routes import router as api_router
from app.db import lifespan
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging_config import log_startup_shutdown_events

app = FastAPI(
    title="Manim Dashboard API",
    version="1.0.0",
    lifespan=lifespan
    )

log_startup_shutdown_events(app)

origins = [
     "http://localhost:5173",
     "https://ai-manim-video-generator-frontend-i6z2vjfhs.vercel.app/",
     "https://manim.keshavanandsingh.co",
     "https://ai-manim-video-generator-frontend.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


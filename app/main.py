 # FastAPI app entry point
from fastapi import FastAPI
from app.api.routes import router as api_router
from app.db import lifespan
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Manim Dashboard API",
    version="1.0.0",
    lifespan=lifespan
    )

origins = [
     "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
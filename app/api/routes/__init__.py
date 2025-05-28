from fastapi import APIRouter
from .manim import router as manim_router
from .auth import router as auth_router

router = APIRouter()
router.include_router(manim_router)
router.include_router(auth_router)
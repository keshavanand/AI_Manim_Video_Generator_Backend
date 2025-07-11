import logging
import sys

# Central logging configuration for the FastAPI app
LOG_FORMAT = '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
LOG_LEVEL = logging.INFO  # Use INFO or WARNING in production
LOG_FILE = 'manim_backend.log'

handlers = [
    logging.StreamHandler(sys.stdout),
    #logging.FileHandler(LOG_FILE, encoding='utf-8')
]

logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=handlers
)

logger = logging.getLogger("manim_backend")

def log_startup_shutdown_events(app):
    """
    Attach startup and shutdown event handlers to the FastAPI app for logging.
    Usage: from app.core.logging_config import log_startup_shutdown_events; log_startup_shutdown_events(app)
    """
    @app.on_event("startup")
    async def on_startup():
        logger.info("FastAPI application startup.")

    @app.on_event("shutdown")
    async def on_shutdown():
        logger.info("FastAPI application shutdown.")

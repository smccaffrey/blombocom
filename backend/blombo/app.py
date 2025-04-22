from fastapi import FastAPI

from blombo.api.router import root_router
from blombo.settings import get_settings

settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
    )
    
    # Add the root router
    app.include_router(root_router, prefix=settings.API_PREFIX)
    
    return app


app = create_app() 
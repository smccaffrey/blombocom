from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from blombo.api.router import router as api_router

app = FastAPI(
    title="Blombo API",
    description="API for Blombo application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Blombo API"} 
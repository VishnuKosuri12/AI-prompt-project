import os
import time
import logging
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from .routes import auth, user, preference, location, chemical, report
from .utils.api_security import ApiKeyMiddleware

# Setup logging
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create FastAPI app
app = FastAPI(title="ChemTrack Backend API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add API Key middleware
app.add_middleware(ApiKeyMiddleware)

# Add validation exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
    logging.error(f"{request}: {exc_str}")
    content = {'status_code': 10422, 'message': exc_str, 'data': None}
    return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    # For local development, just return healthy without checking the database
    if os.environ.get('LOCAL_DEV') == 'true':
        return {"status": "healthy", "mode": "local"}
    
    # Otherwise, try to connect to the database to verify health
    try:
        from .database import get_db_connection
        conn = get_db_connection()
        if conn:
            conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        # Don't fail the health check, but include the error
        return {"status": "healthy", "database": "error", "message": str(e)}

# Include routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(preference.router)
app.include_router(location.router)
app.include_router(chemical.router)
app.include_router(report.router)

# Run application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

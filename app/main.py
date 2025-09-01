from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.database import engine, Base
from app.routes.users import router as users_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Management Microservice",
    description="FastAPI microservice for user management with CRUD operations and HTTP Basic Auth",
    version="1.0.0"
)

# Include routers
app.include_router(users_router, tags=["users"])


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=422,
        content={
            "result": "error",
            "message": "Ошибка валидации данных",
            "details": exc.errors()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with custom format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "result": "error",
            "message": exc.detail
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "result": "ok",
        "message": "User Management Microservice is running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "result": "ok",
        "status": "healthy"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from src.api.v1 import router as api_v1_router
from src.config.settings import Settings
from src.utils.logger import logger

settings = Settings()
app = FastAPI(
    title="Modern FastAPI Server",
    description="A modern FastAPI server with Swagger documentation",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url="/redoc",
)

# Log CORS configuration
logger.info(f"CORS Origins: {settings.CORS_ORIGINS}")

# Parse CORS origins if they are in string format
cors_origins = settings.CORS_ORIGINS
if (
    len(cors_origins) == 1
    and isinstance(cors_origins[0], str)
    and cors_origins[0].startswith("[")
):
    try:
        import json

        cors_origins = json.loads(cors_origins[0].replace("'", '"'))
        logger.info(f"Parsed CORS Origins: {cors_origins}")
    except Exception as e:
        logger.error(f"Error parsing CORS origins: {e}")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_v1_router)


# Custom OpenAPI specification with security scheme
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add JWT Bearer security scheme
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token in the format: Bearer {token}",
        }
    }

    # Apply security to all operations except root and health endpoints
    for path_key, path_item in openapi_schema["paths"].items():
        # Skip security for root and health endpoints
        if path_key in ["/", "/api/v1/health"]:
            continue

        # Apply security to all other endpoints
        for operation in path_item.values():
            operation["security"] = operation.get("security", [])
            operation["security"].append({"Bearer": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Custom Swagger UI route with authentication
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


# Add request middleware for logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"Request: {request.method} {request.url.path}")

    # Log CORS details for OPTIONS requests
    if request.method == "OPTIONS":
        origin = request.headers.get("origin", "Unknown")
        logger.debug(f"CORS preflight request from origin: {origin}")
        logger.debug(f"CORS headers: {dict(request.headers.items())}")

    response = await call_next(request)

    logger.debug(
        f"Response: {request.method} {request.url.path} - Status: {response.status_code}"
    )

    # Log CORS response headers for OPTIONS requests
    if request.method == "OPTIONS":
        logger.debug(f"CORS response headers: {dict(response.headers.items())}")

    return response


# Add exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(
        f"Validation error for {request.method} {request.url.path}: {exc.errors()}"
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )


@app.exception_handler(status.HTTP_400_BAD_REQUEST)
async def bad_request_handler(request: Request, exc):
    logger.error(f"400 Bad Request for {request.method} {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.get("/")
async def root():
    """Root endpoint returning API status."""
    return {"status": "online", "version": app.version}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)

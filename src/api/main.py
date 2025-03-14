from fastapi import FastAPI, Request
from api.routes import router
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
from starlette.responses import Response
import logging
from api import models  # Ensure models are imported
from api.database import engine
import time
from api.telemetry import setup_telemetry, get_tracer
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Initialize Logging First
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Auto-create tables on startup
logger.info("Checking if database tables exist or need to be created...")
models.Base.metadata.create_all(bind=engine)
logger.info("✅ Database tables checked and initialized.")

# Register API routes
app.include_router(router)

# Initialize OpenTelemetry (will use OTEL_SERVICE_NAME environment variable)
setup_telemetry()

# Instrument FastAPI and SQLAlchemy AFTER routes are registered
FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument(engine=engine)

# Prometheus Metrics
#REQUEST_COUNT = Counter(
#    "http_requests_total", 
#    "Total HTTP Requests",
#    ["method", "endpoint", "status_code"]
#)

#REQUEST_DURATION = Histogram(
#    "http_request_duration_seconds",
#    "HTTP Request Duration in seconds",
#    ["method", "endpoint"],
#    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
#)

#ERROR_COUNT = Counter(
#    "http_request_errors_total",
#    "Total HTTP Request Errors",
#    ["method", "endpoint", "error_type"]
#)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    method = request.method
    endpoint = request.url.path
    
    try:
        response = await call_next(request)
        status_code = response.status_code
        
        # Record request count
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        # Record request duration
        duration = time.time() - start_time
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
        
        # Track HTTP errors (4xx, 5xx) separately
        if status_code >= 400:
            ERROR_COUNT.labels(
                method=method,
                endpoint=endpoint,
                error_type=f"http_{status_code}"
            ).inc()
        
        return response
        
    except Exception as e:
        # Record exceptions
        ERROR_COUNT.labels(
            method=method,
            endpoint=endpoint,
            error_type=type(e).__name__
        ).inc()
        
        # Re-raise the exception
        raise e


# @app.get("/metrics")
#async def metrics():
#    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
async def root():
    return {"message": "KodeKloud Record Store API is running!"}

@app.get("/trace-test")
async def trace_test():
    tracer = get_tracer(__name__)
    with tracer.start_as_current_span("test-span") as span:
        span.set_attribute("test.attribute", "test-value")
        logger.info("Creating test span for Jaeger")
        return {"message": "Test span created"}

logger.info("🚀 KodeKloud Record Store API started successfully and is ready to accept requests.")

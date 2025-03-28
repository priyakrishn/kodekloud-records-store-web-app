from fastapi import FastAPI, Request
from api.routes import router
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
from starlette.responses import Response
import logging
import json
import time
from api import models  # Ensure models are imported
from api.database import engine
from api.telemetry import setup_telemetry, get_tracer
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Initialize Logging First - Use JSON formatter
class JsonFormatter(logging.Formatter):
    def format(self, record):
        if isinstance(record.msg, dict):
            return json.dumps(record.msg)
        return json.dumps({"message": record.getMessage(), "level": record.levelname})

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
# Remove existing handlers
for handler in root_logger.handlers:
    root_logger.removeHandler(handler)
# Add JSON console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(JsonFormatter())
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)

# Create structured logger
class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
    
    def info(self, msg, **kwargs):
        # Add trace context
        span = trace.get_current_span()
        span_context = span.get_span_context()
        
        # Format as JSON directly
        log_data = {
            "message": msg,
            "level": "INFO",
            "trace_id": format(span_context.trace_id, "032x") if span_context.is_valid else None,
            "span_id": format(span_context.span_id, "016x") if span_context.is_valid else None,
            **kwargs
        }
        # Send as dict rather than string
        self.logger.info(log_data)
    
    def error(self, msg, **kwargs):
        # Add trace context
        span = trace.get_current_span()
        span_context = span.get_span_context()
        
        # Format as JSON directly
        log_data = {
            "message": msg,
            "level": "ERROR",
            "trace_id": format(span_context.trace_id, "032x") if span_context.is_valid else None,
            "span_id": format(span_context.span_id, "016x") if span_context.is_valid else None,
            **kwargs
        }
        # Send as dict rather than string
        self.logger.error(log_data)

# Replace logger with structured logger
structured_logger = StructuredLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Auto-create tables on startup
structured_logger.info("database_init", status="starting", action="check_tables")
models.Base.metadata.create_all(bind=engine)
structured_logger.info("database_init", status="complete", action="tables_created")

# Register API routes
app.include_router(router)

# Initialize OpenTelemetry (will use OTEL_SERVICE_NAME environment variable)
setup_telemetry()

# Instrument FastAPI and SQLAlchemy AFTER routes are registered
FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument(engine=engine)

# Prometheus metrics 
REQUEST_COUNT = Counter(
    "http_requests_total", 
    "Total HTTP Requests",
    ["method", "endpoint", "status_code"]
)
REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP Request Duration in seconds",
    ["method", "endpoint"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

ERROR_COUNT = Counter(
    "http_request_errors_total",
    "Total HTTP Request Errors",
    ["method", "endpoint", "error_type"]
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    method = request.method
    endpoint = request.url.path
    
    # Create explicit span for the request
    tracer = get_tracer(__name__)
    with tracer.start_as_current_span(
        f"{method} {endpoint}",
        attributes={
            "http.method": method,
            "http.url": str(request.url),
            "http.route": endpoint
        },
    ) as span:
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Add response attributes to span
            span.set_attribute("http.status_code", status_code)
            if status_code >= 400:
                span.set_status(trace.Status(trace.StatusCode.ERROR))
            
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
            
            # Get the current trace and span ID for logging
            span_context = span.get_span_context()
            trace_id = format(span_context.trace_id, "032x") if span_context.is_valid else None
            span_id = format(span_context.span_id, "016x") if span_context.is_valid else None
            
            # Structured logging for each request
            structured_logger.info(
                "request_processed",
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration_ms=round(duration * 1000, 2),
                trace_id=trace_id,
                span_id=span_id
            )
            
            # Track HTTP errors (4xx, 5xx) separately
            if status_code >= 400:
                ERROR_COUNT.labels(
                    method=method,
                    endpoint=endpoint,
                    error_type=f"http_{status_code}"
                ).inc()
                structured_logger.error(
                    "http_error",
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code,
                    duration_ms=round(duration * 1000, 2),
                    trace_id=trace_id,
                    span_id=span_id
                )
            
            return response
            
        except Exception as e:
            # Set span to error
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            span.record_exception(e)
            
            # Record exceptions
            ERROR_COUNT.labels(
                method=method,
                endpoint=endpoint,
                error_type=type(e).__name__
            ).inc()
            
            # Get the current trace and span ID for logging
            span_context = span.get_span_context()
            trace_id = format(span_context.trace_id, "032x") if span_context.is_valid else None
            span_id = format(span_context.span_id, "016x") if span_context.is_valid else None
            
            structured_logger.error(
                "request_failed",
                method=method,
                endpoint=endpoint,
                error=str(e),
                error_type=type(e).__name__,
                trace_id=trace_id,
                span_id=span_id
            )
            
            # Re-raise the exception
            raise e

@app.get("/")
async def root():
    return {"message": "KodeKloud Record Store API is running!"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/trace-test")
async def trace_test():
    tracer = get_tracer(__name__)
    with tracer.start_as_current_span("test-span") as span:
        span.set_attribute("test.attribute", "test-value")
        span.set_attribute("custom.operation", "trace-test")
        
        # Get the current trace and span ID for logging
        span_context = span.get_span_context()
        trace_id = format(span_context.trace_id, "032x") if span_context.is_valid else None
        span_id = format(span_context.span_id, "016x") if span_context.is_valid else None
        
        # Log with explicit trace context
        structured_logger.info(
            "trace_test_executed", 
            span_name="test-span", 
            service="api",
            trace_id=trace_id,
            span_id=span_id,
            test_attribute="test-value"
        )
        
        # Create a child span
        with tracer.start_as_current_span("child-span") as child_span:
            child_span.set_attribute("relationship", "child")
            time.sleep(0.1)  # Add a small delay
            
            # Log from child span
            child_context = child_span.get_span_context()
            child_trace_id = format(child_context.trace_id, "032x") if child_context.is_valid else None
            child_span_id = format(child_context.span_id, "016x") if child_context.is_valid else None
            
            structured_logger.info(
                "child_span_executed",
                span_name="child-span",
                service="api",
                trace_id=child_trace_id,
                span_id=child_span_id,
                parent_span_id=span_id
            )
        
        return {
            "message": "Test spans created",
            "trace_id": trace_id,
            "span_id": span_id
        }

@app.get("/error-test")
async def error_test():
    tracer = get_tracer(__name__)
    with tracer.start_as_current_span("error-span") as span:
        span.set_attribute("error", True)
        span.set_attribute("custom.operation", "error-simulation")
        
        # Set span status to error
        span.set_status(trace.Status(trace.StatusCode.ERROR, "Simulated error for testing"))
        
        # Get the current trace and span ID for logging
        span_context = span.get_span_context()
        trace_id = format(span_context.trace_id, "032x") if span_context.is_valid else None
        span_id = format(span_context.span_id, "016x") if span_context.is_valid else None
        
        structured_logger.error(
            "error_test_executed", 
            span_name="error-span", 
            service="api", 
            error_type="SimulatedError",
            error_reason="Testing error logging and tracing",
            trace_id=trace_id,
            span_id=span_id
        )
        
        # Simulate an HTTP 500 error
        return Response(
            content=json.dumps({
                "error": "Simulated error",
                "trace_id": trace_id,
                "span_id": span_id
            }), 
            status_code=500, 
            media_type="application/json"
        )

@app.on_event("startup")
async def generate_test_logs():
    # Generate some logs with trace contexts
    tracer = get_tracer(__name__)
    
    # Generate log with trace context
    with tracer.start_as_current_span("startup-span") as span:
        span.set_attribute("test.attribute", "test-value")
        span.set_attribute("custom.operation", "startup-test")
        structured_logger.info("Application started", 
                             operation="app_startup",
                             trace_id=format(span.get_span_context().trace_id, "032x"),
                             span_id=format(span.get_span_context().span_id, "016x"))
    
    # Generate error log with trace context
    with tracer.start_as_current_span("error-test-span") as span:
        span.set_attribute("error", True)
        span.set_attribute("custom.operation", "error-simulation")
        structured_logger.error("Test error log", 
                             error_type="SimulatedError",
                             operation="error_test",
                             trace_id=format(span.get_span_context().trace_id, "032x"),
                             span_id=format(span.get_span_context().span_id, "016x"))

structured_logger.info("api_startup", status="complete", version="1.0.0")

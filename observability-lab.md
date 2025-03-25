# Observability Lab: Logs, Metrics, and Traces

This lab will help you understand how logs, metrics, and traces work together to provide observability into your application.

## Prerequisites

Make sure your application is running with:

```bash
docker-compose up -d
```

## [INFO] The Three Pillars of Observability

Modern observability relies on three main types of telemetry data:

1. **Metrics**: Numerical measurements over time (request count, CPU usage)
2. **Logs**: Timestamped records of discrete events
3. **Traces**: End-to-end request flows across distributed services

KodeKloud Records Store uses:
- **Prometheus** for metrics collection
- **Loki** for log aggregation
- **Jaeger** for distributed tracing

These three data sources together provide complete visibility into application behavior.

## [MCQ] Understanding Logs vs. Traces

Question: Which statement best describes the relationship between logs and traces?

A. Logs contain more detailed information than traces
B. Traces are just collections of logs from different services
C. Logs record discrete events while traces show request flow across services
D. Traces are only used for performance monitoring while logs are for debugging

Correct Answer: C. Logs record discrete events while traces show request flow across services

Why? Logs capture point-in-time events with details, while traces connect related events across multiple services to show the complete journey of a request.

## [Config] Generate Test Data

Let's generate some test data for our observability tools:

1. First, run our comprehensive test data generator script:
```bash
./scripts/generate_logs.sh
```

This script will:
- Generate trace context data
- Create error logs
- Produce 404 errors
- Create products and orders
- Generate slow operations with nested spans
- Simulate traffic patterns

2. Or run individual tests as needed:

Generate some trace data by calling the trace test endpoint:
```bash
curl http://localhost:8000/trace-test
```

Generate some error data for our logs:
```bash
curl http://localhost:8000/error-test
```

Generate slow operation data with nested spans:
```bash
curl http://localhost:8000/slow-operation
```

## [INFO] Structured Logging with Trace Context

Our application uses structured logging with JSON format to make logs more queryable.

Each log entry includes:
- Message text
- Log level (INFO, ERROR)
- Timestamp
- Trace ID (for correlation with traces)
- Span ID (for specific part of the trace)
- Additional context (endpoint, duration, etc.)

This allows us to correlate logs with traces to get the full picture of what happened during a request.

## [MCQ] Exploring Logs in Loki

Question: Which LogQL query would you use to find all errors in the API service that also have trace IDs?

A. `{container_name="kodekloud-record-store-api"} |= "ERROR"`
B. `{container_name="kodekloud-record-store-api"} |= "ERROR" |= "trace_id"`
C. `{job="fluentbit"} | json | level="ERROR" and trace_id != ""`
D. `{job="kodekloud-record-store-api"} |= "error"`

Correct Answer: B. `{container_name="kodekloud-record-store-api"} |= "ERROR" |= "trace_id"`

Why? This query filters logs from the API container that contain both "ERROR" and "trace_id" strings, which will find error logs that include trace context.

## [Config] Find and Analyze a Trace

1. Open Jaeger UI at http://localhost:16686

2. From the Service dropdown, select "kodekloud-record-store-api"

3. Click "Find Traces"

4. Look for a trace for the "/slow-operation" endpoint

5. Click on one of these traces to view its details:
   - Notice the nested spans showing the call hierarchy
   - See the timing for each component
   - Look at span attributes like "operation.type" and custom attributes

## [MCQ] Trace Analysis

Question: In distributed tracing, what does a "span" represent?

A. The total duration of a request from start to finish
B. An operation with a start and end time within a trace
C. A log entry associated with a trace
D. The connection between two services

Correct Answer: B. An operation with a start and end time within a trace

Why? A span represents a unit of work or operation within a trace. Spans can be nested to show parent-child relationships between operations.

## [Config] Using the Observability Dashboard

1. Open Grafana at http://localhost:3000

2. Navigate to the "KodeKloud Records - Observability Dashboard" 

3. Examine the different panels:
   - System metrics (request rate, error rate)
   - Logs with trace context
   - User experience metrics (availability, response time)

4. Click on an error log and note the trace ID

5. Copy the trace ID and go to Jaeger UI

6. Paste the trace ID in the search box and click "Find Traces"

7. Analyze the trace to understand what caused the error

## [MCQ] Root Cause Analysis

Question: A user reports that the checkout process occasionally fails. Which combination of observability tools would give you the most complete picture of the issue?

A. Only Prometheus metrics to see the error rate
B. Only Loki logs to see error messages
C. Only Jaeger traces to see where it fails
D. All three: metrics for detection, logs for context, and traces for the execution path

Correct Answer: D. All three: metrics for detection, logs for context, and traces for the execution path

Why? A complete investigation uses metrics to identify when errors occur, logs to understand the error details, and traces to see the full context and execution path of the failed request.

## [Config] Create a Custom LogQL Query

Create a LogQL query to analyze checkout operations:

1. Go to Grafana's Explore view
2. Select Loki as the data source
3. Enter this query to find all checkout operations:
   ```
   {container_name="kodekloud-record-store-api"} |= "operation" |= "checkout"
   ```
4. Modify the query to focus on checkout errors:
   ```
   {container_name="kodekloud-record-store-api"} |= "ERROR" |= "operation" |= "checkout"
   ```
5. Find logs with trace context that you can correlate with Jaeger:
   ```
   {container_name="kodekloud-record-store-api"} |= "trace_id"
   ```
6. Look for slow operations (operations taking more than 1 second):
   ```
   {container_name="kodekloud-record-store-api"} |= "duration_ms" |= "operation"
   ```

Try running these queries after generating test data with the `/trace-test` and `/error-test` endpoints.

You can also create more complex queries to analyze specific patterns in your logs:

- Find all logs from a specific trace:
  ```
  {container_name="kodekloud-record-store-api"} |~ "trace_id\":\"[a-f0-9]+"
  ```
  (Copy a trace ID from one of your logs and replace the regex pattern)

- Count errors by operation type:
  ```
  sum by(operation) (count_over_time({container_name="kodekloud-record-store-api"} |= "ERROR" |= "operation" [5m]))
  ```

## [MCQ] Advanced Traces and Spans

Question: What is the main advantage of adding custom attributes to spans in your traces?

A. It makes traces look more colorful in the UI
B. It adds business context to technical traces to make them more useful
C. It automatically fixes performance issues in your code
D. It prevents traces from being recorded for failed requests

Correct Answer: B. It adds business context to technical traces to make them more useful

Why? Custom attributes like product IDs, order quantities, or operation names provide business context that makes traces more meaningful for debugging and analysis.

## Challenge Task

Complete this final challenge to demonstrate your understanding of observability:

1. Use the endpoint `/slow-operation` to generate some traces
2. Find these traces in Jaeger
3. Identify which part of the operation is the slowest (hint: look at span durations)
4. Find the corresponding logs in Loki for this slow operation
5. Determine if there's a correlation between operation duration and error rate

## Conclusion

You've now learned how metrics, logs, and traces work together to provide comprehensive observability for your application. This approach allows you to:

1. **Detect** issues with metrics
2. **Investigate** with logs
3. **Understand** with traces

This complete observability solution helps you maintain reliable services and quickly resolve issues when they occur. 
# KodeKloud Records Store

A comprehensive demo application for learning and practicing SRE, observability, and incident management concepts. This project simulates a record store e-commerce application with integrated observability tools for metrics, logs, and distributed tracing.

## Overview

The KodeKloud Records Store application demonstrates a complete observability solution built on modern best practices. It serves as a hands-on learning environment for:

- Setting up comprehensive monitoring and observability
- Implementing distributed tracing for microservices
- Designing effective alerting strategies
- Practicing incident response using real-world scenarios
- Learning SLO-based monitoring approaches

## Architecture

The application uses a microservice architecture with the following components:

- **Web API**: Python FastAPI service for the main application
- **Background Worker**: Celery worker for asynchronous tasks
- **Database**: PostgreSQL for data storage
- **Message Queue**: RabbitMQ for task distribution
- **Observability Stack**:
  - Prometheus for metrics collection
  - Grafana for visualization
  - Loki for log aggregation
  - Jaeger for distributed tracing
  - AlertManager for alert handling
  - Blackbox Exporter for synthetic monitoring
  - Fluent Bit for log collection

### Microservices Architecture Diagram

```mermaid
graph TD
    subgraph "User Interface"
        API[Web API<br>FastAPI<br>Port: 8000]
    end

    subgraph "Core Microservices"
        PS[Product Service]
        OS[Order Service]
        US[User Service]
        IS[Inventory Service]
        NS[Notification Service]
    end

    subgraph "Async Processing"
        MQ[RabbitMQ<br>Port: 5672]
        CW[Celery Workers]
    end

    subgraph "Storage"
        DB[PostgreSQL<br>Port: 5432]
    end

    subgraph "Observability"
        PR[Prometheus<br>Port: 9090]
        GF[Grafana<br>Port: 3000]
        JG[Jaeger<br>Port: 16686]
        LK[Loki<br>Port: 3100]
        AM[AlertManager<br>Port: 9093]
        BB[Blackbox Exporter<br>Port: 9115]
        FB[Fluent Bit]
    end

    %% Core service connections
    API --> PS
    API --> OS
    API --> US
    API --> IS
    API --> NS

    %% Service to database connections
    PS --> DB
    OS --> DB
    US --> DB
    IS --> DB
    NS --> DB

    %% Async processing connections
    API --> MQ
    OS --> MQ
    IS --> MQ
    NS --> MQ
    MQ --> CW
    CW --> DB
    CW --> NS

    %% Observability connections
    PR --> API
    PR --> PS
    PR --> OS
    PR --> US
    PR --> IS
    PR --> NS
    PR --> MQ
    PR --> CW
    PR --> DB
    PR --> BB
    
    FB --> API
    FB --> PS
    FB --> OS
    FB --> US
    FB --> IS
    FB --> NS
    FB --> CW
    FB --> LK
    
    API --> JG
    PS --> JG
    OS --> JG
    US --> JG
    IS --> JG
    NS --> JG
    
    GF --> PR
    GF --> LK
    GF --> JG
    PR --> AM

    %% External connections
    BB -.-> API
    
    classDef primary fill:#f9f,stroke:#333,stroke-width:2px;
    classDef secondary fill:#bbf,stroke:#333,stroke-width:1px;
    classDef storage fill:#bfb,stroke:#333,stroke-width:1px;
    classDef messaging fill:#fbb,stroke:#333,stroke-width:1px;
    classDef observability fill:#ffd,stroke:#333,stroke-width:1px;
    
    class API primary;
    class PS,OS,US,IS,NS secondary;
    class DB storage;
    class MQ,CW messaging;
    class PR,GF,JG,LK,AM,BB,FB observability;
```

### Data Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant A as Web API
    participant PS as Product Service
    participant OS as Order Service
    participant IS as Inventory Service
    participant NS as Notification Service
    participant MQ as RabbitMQ
    participant CW as Celery Workers
    participant DB as Database
    
    C->>A: Browse Product Catalog
    A->>PS: Get Products
    PS->>DB: Query Products
    DB-->>PS: Product Data
    PS-->>A: Product List
    A-->>C: Display Products
    
    C->>A: Place Order
    A->>OS: Create Order
    OS->>DB: Save Order
    DB-->>OS: Order ID
    OS->>MQ: Queue Inventory Update
    MQ->>CW: Process Inventory Task
    CW->>IS: Update Inventory
    IS->>DB: Update Stock
    CW->>MQ: Queue Notification
    MQ->>CW: Process Notification Task
    CW->>NS: Send Notification
    NS-->>C: Email Confirmation
    
    Note over A,DB: All operations are traced with Jaeger
    Note over A,NS: All components emit metrics to Prometheus
    Note over A,NS: All logs go to Loki via Fluent Bit
```

## Project Structure

```
.
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/kodekloud/records-store-web-app.git
   cd kodekloud-records-store-web-app
   ```

2. Start the application and monitoring stack:
   ```bash
   docker-compose up -d
   ```

3. Generate test data for observability:
   ```bash
   ./scripts/generate_logs.sh
   ```

4. Access the services:
   - **Application**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Grafana**: http://localhost:3000 (user: admin, password: admin)
   - **Prometheus**: http://localhost:9090
   - **Jaeger UI**: http://localhost:16686
   - **Loki**: http://localhost:3100
   - **Alert Manager**: http://localhost:9093
   - **RabbitMQ Management**: http://localhost:15672 (user: guest, password: guest)

## Working with the Application

### Testing and Exploring

1. The application provides several test endpoints to generate telemetry data:
   - `/health` - Health check endpoint
   - `/trace-test` - Generate a trace with multiple spans
   - `/error-test` - Generate error logs
   - `/slow-operation` - Generate a slow operation trace

2. Generate continuous test traffic:
   ```bash
   ./test_traffic.sh
   ```

3. Run simplified black-box monitoring (sends periodic health checks):
   ```bash
   ./black_box_monitor.sh
   ```

### Key Features

1. **Metrics Collection**:
   - Application metrics (request counts, latency, errors)
   - Service health metrics
   - Business metrics (orders, products)
   - SLO-based metrics for reliability measurement

2. **Log Management**:
   - Structured logging with trace context
   - Log correlation with metrics and traces
   - Log querying with LogQL in Grafana

3. **Distributed Tracing**:
   - Request flow visualization
   - Performance bottleneck identification
   - Error propagation analysis

4. **Alerting**:
   - SLO-based alerts
   - Symptom-based alerting
   - Multiple severity levels

## Observability Exercises

The application is designed for hands-on learning with the following exercises:

1. **Understanding Metrics, Logs, and Traces**:
   - View correlated telemetry data
   - Follow a request through the system

2. **Monitoring and Alerting**:
   - Explore the pre-configured dashboards
   - Understand alerting rules and thresholds
   - Create custom alerts

3. **SLO Implementation**:
   - Learn how SLIs are defined and measured
   - Understand error budget consumption
   - Practice SLO-based alerting

4. **Incident Response**:
   - Practice troubleshooting using telemetry data
   - Analyze performance issues
   - Debug error conditions

## Troubleshooting

- **Services not starting**: Check for port conflicts with `docker-compose ps` and `netstat -tulpn`
- **No data in Grafana**: Verify Prometheus is scraping targets at http://localhost:9090/targets
- **No logs in Loki**: Check Fluent Bit is running with `docker-compose logs fluent-bit`
- **No traces in Jaeger**: Verify OpenTelemetry export with `docker-compose logs jaeger`

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License.
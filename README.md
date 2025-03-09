# KodeKloud Record Store Web App

## Overview

A modern, microservices-based web application for a record store, featuring a FastAPI backend, Celery workers, and comprehensive monitoring. This application demonstrates best practices for building scalable, observable Python applications.

## Features

- **FastAPI Backend**: RESTful API for managing record store inventory and orders
- **Celery Workers**: Asynchronous task processing for order fulfillment
- **PostgreSQL Database**: Persistent storage for product and order data
- **RabbitMQ**: Message broker for task queue management
- **Comprehensive Monitoring**:
  - Prometheus for metrics collection
  - Grafana for visualization
  - Jaeger for distributed tracing
  - Structured logging

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   FastAPI   │────▶│   RabbitMQ  │────▶│    Celery   │
│     API     │     │   Message   │     │   Workers   │
└─────────────┘     │    Broker   │     └─────────────┘
       │            └─────────────┘            │
       │                                        │
       ▼                                        ▼
┌─────────────┐                        ┌─────────────┐
│  PostgreSQL │◀───────────────────────│  Prometheus │
│   Database  │                        │   Metrics   │
└─────────────┘                        └─────────────┘
                                              │
┌─────────────┐     ┌─────────────┐          │
│   Grafana   │◀────│    Jaeger   │◀─────────┘
│  Dashboards │     │   Tracing   │
└─────────────┘     └─────────────┘
```


## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+

### Running Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/kodekloud-records-store-web-app.git
   cd kodekloud-records-store-web-app
   ```

2. Start the application using Docker Compose:
   ```bash
   cd config
   docker-compose up -d
   ```

3. Access the services:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Grafana: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090
   - Jaeger UI: http://localhost:16686
   - RabbitMQ Management: http://localhost:15672 (guest/guest)

### Development Setup

1. Create a virtual environment:
   ```bash
   cd src
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the API locally:
   ```bash
   uvicorn api.main:app --reload
   ```

## API Endpoints

- `GET /products` - List all products
- `POST /products` - Add a new product
- `GET /products/{id}` - Get product details
- `GET /orders` - List all orders
- `POST /orders` - Create a new order
- `GET /orders/{id}` - Get order details
- `POST /orders/{id}/process` - Process a specific order
- `GET /metrics` - Prometheus metrics endpoint
- `GET /trace-test` - Test endpoint for Jaeger tracing

## Monitoring and Observability

- **Metrics**: Prometheus collects metrics from both the API and worker services
- **Dashboards**: Grafana provides pre-configured dashboards for monitoring
- **Tracing**: Jaeger collects distributed traces for request flows
- **Logging**: Structured logs are available in container logs

## Deployment

The application can be deployed using:

- Docker Compose for development/testing
- Kubernetes with Helm charts for production (see the `kodekloud-record-store-helm` repository)
- GitHub Actions workflow for CI/CD pipeline

## License

This project is licensed under the MIT License - see the LICENSE file for details.
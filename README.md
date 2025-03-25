# KodeKloud Records Store

This is a sample application for demonstrating observability concepts including metrics, logs, and traces.

## Project Structure

```
kodekloud-records-store-web-app/
├── src/                    # Application source code
│   ├── api/                # API implementation
│   └── ...
├── config/                 # Configuration files
│   ├── monitoring/         # Observability configuration
│   │   ├── grafana-provisioning/  # Grafana dashboards and datasources
│   │   ├── logging/        # Loki and Fluent Bit configs
│   │   ├── prometheus.yml  # Prometheus configuration
│   │   ├── alert_rules.yml # Prometheus alert rules
│   │   ├── sli_rules.yml   # Service Level Indicator definitions
│   │   └── ...
│   └── env/                # Environment-specific configs
├── scripts/                # Utility scripts
│   └── generate_logs.sh    # Script to generate test logs and traces
├── tracing/                # OpenTelemetry tracing configs
├── observability-lab.md    # Lab instructions and exercises
├── docker-compose.yaml     # Docker Compose configuration
└── Dockerfile              # Application Dockerfile
```

## Getting Started

1. Start the application:

```bash
docker-compose up -d
```

2. Generate test data for observability:

```bash
./scripts/generate_logs.sh
```

3. Access the applications:

- Application: http://localhost:8000
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Jaeger UI: http://localhost:16686

## Observability Components

This project demonstrates a complete observability solution with:

### Metrics
- **Prometheus** for metrics collection and alerting
- **Grafana** for visualization
- **Pushgateway** for batch job metrics
- **Blackbox Exporter** for synthetic monitoring

### Logs
- **Loki** for log aggregation
- **Fluent Bit** for log collection
- Structured logging with trace context

### Traces
- **Jaeger** for distributed tracing
- **OpenTelemetry** for instrumentation

## Lab Exercises

See `observability-lab.md` for hands-on exercises to learn about:
- Understanding metrics, logs, and traces
- Querying logs with LogQL
- Analyzing traces
- Correlating telemetry data
- Troubleshooting using observability tools

## Contributing

Feel free to submit issues and enhancement requests.

## License

This project is licensed under the MIT License.
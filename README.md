# Prometheus and Grafana demo

A compact Flask application instrumented with Prometheus, visualized with Grafana, and packaged with Docker Compose.

## Architecture

```text
Traffic generator --> Flask app (/ and /work) --> /metrics --> Prometheus --> Grafana
```

The application records request totals, in-progress requests, and request-duration histograms. Prometheus scrapes the application every five seconds; Grafana queries Prometheus using PromQL.

## Prerequisites

- Docker Desktop with Docker Compose
- PowerShell (Windows) or a compatible shell

## Start securely

1. Copy the example configuration:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` and replace `GRAFANA_ADMIN_PASSWORD` with a unique, long password. Never commit this file.

3. Start the stack:

   ```powershell
   docker compose up --build -d
   ```

4. Open the local-only services:

   - App: http://localhost:8000/
   - Prometheus: http://localhost:9090/
   - Grafana: http://localhost:3000/ (use the credentials in `.env`)

## Generate sample traffic

```powershell
.\test.ps1
```

## Prometheus checks

Visit http://localhost:9090/targets and confirm `demo-app` is **UP**. Then run:

```promql
demo_http_requests_total
```

```promql
sum(rate(demo_http_requests_total[1m]))
```

```promql
sum(rate(demo_http_requests_total{status="500"}[1m]))
```

```promql
histogram_quantile(0.95, sum by (le) (rate(demo_http_request_duration_seconds_bucket[5m])))
```

## Grafana dashboard

Add a Prometheus time-series panel for each of the three PromQL queries above. Use a 15-minute time range. The first panel shows request throughput, the second shows error rate, and the third shows p95 request latency.

## Run tests

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

## Security

Read [SECURITY.md](SECURITY.md) before deploying outside a local learning environment.

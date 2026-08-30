"""Demo HTTP service with Prometheus instrumentation.

Metrics are intentionally defined at module scope so every request handled by
this process updates the same Prometheus registry.
"""

import time

from flask import Flask, jsonify, request
from prometheus_client import Counter, Gauge, Histogram, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

# Keep labels bounded and predictable. Do not add user IDs, request IDs, or
# raw URLs: high-cardinality labels increase Prometheus storage and query cost.
REQUESTS = Counter(
    "demo_http_requests",
    "Total HTTP requests handled by the demo application.",
    ["endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "demo_http_request_duration_seconds",
    "Time spent handling HTTP requests in seconds.",
    ["endpoint"],
)

IN_PROGRESS = Gauge(
    "demo_http_requests_in_progress",
    "HTTP requests currently being processed by the demo application.",
)

@app.get("/healthz")
def healthz():
    """Return process liveness without checking downstream dependencies."""
    return jsonify(status="ok")


@app.get("/work")
def work():
    """Simulate bounded synchronous work and record successful latency."""
    try:
        seconds = float(request.args.get("seconds", 0.3))
    except ValueError:
        # Invalid client input is a 4xx response, not an application failure.
        return jsonify(error="seconds must be a number"), 400

    # Bound the demo workload so a request cannot monopolize the worker.
    seconds = min(max(seconds, 0), 5)

    with IN_PROGRESS.track_inprogress():
        with REQUEST_DURATION.labels(endpoint="/work").time():
            time.sleep(seconds)
            REQUESTS.labels(endpoint="/work", status="200").inc()
            return jsonify(
                message="Work completed successfully.",
                duration_seconds=seconds,
            )

@app.get("/fail")
def fail():
    """Provide a controlled 500 response for alert and error-rate testing."""
    with REQUEST_DURATION.labels(endpoint="/fail").time():
        REQUESTS.labels(endpoint="/fail", status="500").inc()
        return jsonify(error="Intentional error for testing purposes."), 500

@app.get("/")
def home():
    with IN_PROGRESS.track_inprogress():
        with REQUEST_DURATION.labels(endpoint="/").time():
            REQUESTS.labels(endpoint="/", status="200").inc()
            return jsonify(message="Hello from the monitored app!")

# Mount the Prometheus WSGI application separately from business routes. In a
# production deployment, restrict this endpoint to the monitoring network.
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

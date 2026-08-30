import time

from flask import Flask, jsonify, request
from prometheus_client import Counter, Gauge, Histogram, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

# Prometheus metrics use standard names, units, and low-cardinality labels.
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
    """Liveness endpoint for container orchestration."""
    return jsonify(status="ok")


@app.get("/work")
def work():
    """Simulate some work being done."""
    try:
        seconds = float(request.args.get("seconds", 0.3))
    except ValueError:
        return jsonify(error="seconds must be a number"), 400

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
    """Simulate a failure."""
    with REQUEST_DURATION.labels(endpoint="/fail").time():
        REQUESTS.labels(endpoint="/fail", status="500").inc()
        return jsonify(error="Intentional error for testing purposes."), 500

@app.get("/")
def home():
    with IN_PROGRESS.track_inprogress():
        with REQUEST_DURATION.labels(endpoint="/").time():
            REQUESTS.labels(endpoint="/", status="200").inc()
            return jsonify(message="Hello from the monitored app!")

# Prometheus scrapes this endpoint; it should be restricted at the network edge in production.
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

# Use an official Python runtime as a parent image
FROM python:3.13-slim

WORKDIR /app

# Install only the runtime dependency set before source code so dependency
# layers remain reusable when application code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Run the service without root privileges; the container needs no write access
# outside its temporary directory, which Compose supplies as tmpfs.
RUN addgroup --system app && adduser --system --ingroup app app
COPY --chown=app:app app.py .

USER app
EXPOSE 8000
# Metrics are process-local in this educational app. Keep one worker so each
# scrape observes a complete metric set; configure Prometheus multiprocess
# mode before increasing worker count in a real deployment.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "30", "app:app"]

# Basic Monitoring & Logging Setup

## Python Backend
- Use built-in logging (already present in utils/logger.py).
- For production, forward logs to a service like Papertrail, Loggly, or ELK stack.
- Add Prometheus exporter or use Flask-Prometheus for metrics if needed.

## Node.js Server
- Use PM2 for process management and log aggregation.
- Forward logs to a central service for production.

## Docker Compose
- Use `docker-compose logs` to view logs from all services.
- For advanced monitoring, add Prometheus/Grafana containers.

---

## Example: Add Prometheus Exporter to Flask

```bash
pip install prometheus_flask_exporter
```

In `api_server.py`:
```python
from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)
```

This exposes metrics at `/metrics` for Prometheus scraping.

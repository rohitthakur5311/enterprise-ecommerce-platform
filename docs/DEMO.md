# Demo Runbook

## Start

```bash
docker compose up --build
```

Open `frontend/index.html` in a browser for the lightweight production-style dashboard.

## Demo sequence

### Register
`POST /api/v1/auth/register`

### Login
`POST /api/v1/auth/login`

Use the returned bearer token for authenticated operations.

### Seed catalog

For a local SQLite setup:

```bash
python scripts/seed_catalog.py
```

### Create product

Use the admin demo account:

```text
admin@example.com / Admin123!
```

Then call `POST /api/v1/products`.

### Create order

Use a normal customer token and call `POST /api/v1/orders`.

## Operational demo

Open:

- Gateway Swagger
- Prometheus
- Grafana

Then generate traffic with:

```bash
locust -f tests/performance/locustfile.py --host http://localhost:8000
```

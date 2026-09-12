# Enterprise E-Commerce Platform

A production-style, industry-ready Python enterprise application demonstrating:

- Microservices architecture with FastAPI
- API Gateway pattern
- JWT authentication + refresh tokens
- Role-based access control (RBAC)
- PostgreSQL persistence with Alembic migrations
- Redis caching
- Docker / Docker Compose
- Kubernetes manifests
- GitHub Actions CI/CD
- Automated unit, integration and API tests
- Coverage gate >85%
- Ruff + Bandit + pip-audit security/quality checks
- Prometheus metrics + Grafana dashboard
- Structured JSON logging
- Rate limiting
- OpenAPI / Swagger documentation
- Health/readiness endpoints
- Performance test configuration
- Professional project documentation

## Architecture

```text
                         ┌──────────────────────┐
                         │       Client         │
                         └──────────┬───────────┘
                                    │
                              HTTP / JSON
                                    │
                         ┌──────────▼───────────┐
                         │      API Gateway     │
                         │ FastAPI + rate limit │
                         └──────┬─────┬─────┬───┘
                                │     │     │
                    ┌───────────┘     │     └────────────┐
                    ▼                 ▼                  ▼
             ┌────────────┐   ┌────────────┐    ┌────────────┐
             │ Auth       │   │ Catalog    │    │ Orders     │
             │ Service    │   │ Service    │    │ Service    │
             └─────┬──────┘   └─────┬──────┘    └─────┬──────┘
                   │                │                  │
             ┌─────▼──────┐   ┌─────▼──────┐    ┌─────▼──────┐
             │ PostgreSQL │   │ PostgreSQL │    │ PostgreSQL │
             └────────────┘   └────────────┘    └────────────┘
                                │                  │
                                └──────┬───────────┘
                                       ▼
                                    Redis

             Prometheus ◄── /metrics ── Services
                  │
                  ▼
               Grafana
```

## Services

| Service | Port | Responsibility |
|---|---:|---|
| Gateway | 8000 | Public API, routing, auth verification, rate limiting |
| Auth | 8001 | Users, JWT access/refresh tokens, RBAC |
| Catalog | 8002 | Products, stock, search, Redis caching |
| Orders | 8003 | Orders, totals, stock validation |
| PostgreSQL | 5432 | Persistent relational data |
| Redis | 6379 | Cache + rate-limit storage |
| Prometheus | 9090 | Metrics |
| Grafana | 3000 | Dashboards |

## Quick start

### 1. Clone / enter the project

```bash
cd enterprise_project
```

### 2. Start everything

```bash
docker compose up --build
```

### 3. Open API documentation

- Gateway Swagger: http://localhost:8000/docs
- Auth Swagger: http://localhost:8001/docs
- Catalog Swagger: http://localhost:8002/docs
- Orders Swagger: http://localhost:8003/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

Grafana default credentials in local development are `admin/admin`.

### 4. Demo account

The auth service creates a demo admin user on startup:

```text
email: admin@example.com
password: Admin123!
role: admin
```

Change the password and secret values for any real deployment.

## Local development without Docker

Python 3.12+ is recommended.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
pytest -q --cov=services --cov-report=term-missing
ruff check .
bandit -r services
```

For local development, services default to SQLite when their database URL is not supplied. Docker Compose uses PostgreSQL.

## Example API flow

1. `POST /api/v1/auth/login`
2. Receive access + refresh token.
3. `GET /api/v1/products`
4. `POST /api/v1/products` with an admin bearer token.
5. `POST /api/v1/orders`
6. `GET /api/v1/orders/{id}`

## Production notes

This repository is a complete portfolio/reference implementation. Before production use:

- Replace all development secrets.
- Put secrets in a managed secret store.
- Use managed PostgreSQL/Redis.
- Configure TLS at the ingress/load balancer.
- Configure domain-specific CORS.
- Use a real distributed tracing backend.
- Add centralized log retention and alert routing.
- Review Kubernetes resource limits, HPA and PodDisruptionBudgets for the target cluster.
- Run database migrations as a controlled deployment step.

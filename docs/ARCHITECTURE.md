# Architecture Notes

## Service ownership

Each service owns its domain model and database.

## Request flow

```text
Client
  |
  v
Gateway
  |
  +--> Auth
  |
  +--> Catalog <--> Redis
  |
  +--> Orders ----> Catalog
```

## Reliability

- Health/readiness probes
- Container restart policies
- Kubernetes replicas
- HPA
- Timeouts on service-to-service calls
- Metrics and alert rules

## Scalability

Stateless API services can be horizontally scaled. PostgreSQL and Redis should use managed/high-availability deployments in production.

## Observability

Metrics are emitted in Prometheus format. Logs are structured JSON and can be shipped to a centralized platform.

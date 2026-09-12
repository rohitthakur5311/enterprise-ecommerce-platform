# Deployment Guide

## Docker Compose

```bash
docker compose up --build
```

## Kubernetes

Build and tag service images:

```bash
docker build -f docker/Dockerfile --build-arg SERVICE_MODULE=services.gateway.app -t enterprise-gateway:latest .
docker build -f docker/Dockerfile --build-arg SERVICE_MODULE=services.auth.app -t enterprise-auth:latest .
docker build -f docker/Dockerfile --build-arg SERVICE_MODULE=services.catalog.app -t enterprise-catalog:latest .
docker build -f docker/Dockerfile --build-arg SERVICE_MODULE=services.orders.app -t enterprise-orders:latest .
```

Apply manifests:

```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/secret.example.yaml
kubectl apply -f kubernetes/
```

For a real deployment, do not commit plaintext secrets.

## Rolling deployment

Kubernetes Deployments use rolling updates by default. A more advanced release pipeline can add:

- blue/green
- canary
- automatic rollback
- health-based promotion

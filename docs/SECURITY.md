# Security Checklist

## Application

- [x] Password hashing
- [x] JWT access token
- [x] JWT refresh token
- [x] RBAC
- [x] Input validation
- [x] Rate limiting
- [x] Dependency auditing
- [x] Static security scanning
- [x] Secrets via environment variables

## Container

- [x] Non-root runtime user
- [x] Minimal Python slim image
- [x] `.dockerignore`

## Kubernetes

- [x] Non-root pod security context
- [x] NetworkPolicy baseline
- [x] Secret template
- [x] TLS-ready ingress
- [x] Resource requests/limits

## Before production

- Rotate all demo secrets.
- Configure TLS certificates.
- Use a managed secret manager.
- Enable database encryption.
- Add WAF rules.
- Add audit logging.
- Run DAST and container image scanning.

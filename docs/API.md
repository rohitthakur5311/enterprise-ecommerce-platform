# API Reference

All services expose interactive Swagger documentation at `/docs`.

## Gateway

### Health
`GET /health`

### Login
`POST /api/v1/auth/login`

Example:

```json
{
  "email": "admin@example.com",
  "password": "Admin123!"
}
```

### Register
`POST /api/v1/auth/register`

### Products
- `GET /api/v1/products`
- `GET /api/v1/products/{id}`
- `POST /api/v1/products` — admin
- `PATCH /api/v1/products/{id}/stock` — admin

### Orders
- `POST /api/v1/orders`
- `GET /api/v1/orders`
- `GET /api/v1/orders/{id}`

## Authentication

Send:

```text
Authorization: Bearer <access_token>
```

## Error conventions

The platform uses standard HTTP semantics:

- `400` invalid request
- `401` authentication failure
- `403` authorization failure
- `404` resource not found
- `409` business conflict
- `429` rate limit exceeded
- `5xx` server/infrastructure errors

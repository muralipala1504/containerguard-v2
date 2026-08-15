# API Reference

Base URL: `http://localhost:3001`

## Authentication

All endpoints (except auth) require JWT token in header:
Authorization: Bearer <token>
## Auth Endpoints

### Signup
POST /api/auth/signup

Body:
{
"email": "user@example.com",
"password": "password123",
"name": "John Doe"
}

Response:
{
"success": true,
"token": "eyJhbGc...",
"user": {
"id": 1,
"email": "user@example.com",
"name": "John Doe"
}
}
### Login
[200~POST /api/auth/login

Body:
{
"email": "user@example.com",
"password": "password123"
}

Response:
{
"success": true,
"token": "eyJhbGc...",
"user": { ... }
}~## Monitoring Endpoints

### Get All (K8s + Docker)
GET /api/monitoring/all

Response:
{
"k8s": {
"clusterInfo": {
"nodes": 1,
"nodeList": [ ... ]
},
"pods": [ ... ]
},
"docker": {
"info": {
"containers": 3,
"runningContainers": 2,
"stoppedContainers": 1,
"images": 6
},
"containers": [ ... ]
}
}
### Get K8s Only
GET /api/monitoring/k8s

Response:
{
"clusterInfo": { ... },
"pods": [
{
"name": "coredns-8db54c48d-cjt4m",
"namespace": "kube-system",
"status": "Running",
"containers": 1,
"image": "rancher/mirrored-coredns:1.14.3"
}
]
}
### Get Docker Only
GET /api/monitoring/docker

Response:
{
"info": {
"containers": 3,
"runningContainers": 2,
"images": 6
},
"containers": [
{
"id": "abc123...",
"name": "containerguard-backend",
"image": "containerguard-v2-backend",
"status": "running"
}
]
}
### Health Check
GET /health

Response:
{
"status": "healthy",
"service": "containerguard-backend"
}
## Status Codes

- **200** — Success
- **400** — Bad request
- **401** — Unauthorized (no token)
- **500** — Server error
- **503** — Service unavailable

## Rate Limiting

None currently implemented. Coming in future versions.

# ContainerGuard Agent - Phase 1 Deployment

## Quick Start (docker-compose)

```bash
git clone https://github.com/muralipala1504/containerguard-v2.git
cd containerguard-v2

# Start agent
docker compose up -d

# Verify
curl http://localhost:3001/health
```

## Signup & Get Token

```bash
curl -X POST http://localhost:3001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","email":"admin@local","name":"Admin","password":"changeme"}'
```

## Monitor Docker

```bash
TOKEN="<your-token>"
curl http://localhost:3001/api/monitoring/docker \
  -H "Authorization: Bearer $TOKEN"
```

## Monitor Kubernetes

```bash
curl http://localhost:3001/api/monitoring/k8s \
  -H "Authorization: Bearer $TOKEN"
```

## View Events

```bash
curl http://localhost:3001/api/events \
  -H "Authorization: Bearer $TOKEN"
```

## Configuration

Edit `backend/src/config.yaml` to add/modify rules:

```yaml
rules:
  - id: "rule-high-cpu"
    enabled: true
    trigger:
      type: "metric"
      resource: "container"
      metric: "cpu_percent"
      operator: ">"
      threshold: 80
    action:
      type: "alert"
      channels: ["log"]
```

## What's Included

- **Docker Monitoring**: Track container CPU, memory, network
- **Kubernetes Monitoring**: Track pod status, node health
- **Rule Engine**: Config-driven alerts and auto-remediation
- **Event Logging**: SQLite database for audit trail
- **REST API**: Full monitoring and event query API

## Deployment

Agent runs in container with:
- Docker socket mounted for container monitoring
- Kubeconfig mounted for K8s access
- SQLite database persisted to host

## Architecture
Agent (Docker Container on :3001)
├── FastAPI Backend
├── Docker Monitor (via docker.sock)
├── K8s Monitor (via kubeconfig)
├── Rule Engine (fires every 30s)
└── SQLite Event Logger
## Next Steps (Phase 2)

- Cloud dashboard SaaS
- Advanced rule conditions
- Webhook integrations
- Multi-agent federation

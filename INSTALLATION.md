# Installation Guide

## Prerequisites

- Docker & Docker Compose installed
- K8s cluster running (optional, works without it)
- 2GB RAM minimum
- Port 3001 & 5173 available

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/muralipala1504/containerguard-v2.git
cd containerguard-v2
```

### 2. Configure (Optional)

Edit `docker-compose.yml` if needed:

```yaml
environment:
  - K8S_API_ENDPOINT=https://your-k8s-cluster:6443
  - DOCKER_SOCKET=/var/run/docker.sock
```

### 3. Start Services

```bash
docker-compose up
```

Services:
- Backend: http://localhost:3001
- Dashboard: http://localhost:5173

### 4. Login

Default credentials (or create account):
- Email: test@example.com
- Password: password123

## Troubleshooting

**K8s pods not showing?**
- Check kubeconfig mounted in docker-compose.yml
- Verify K8s API endpoint is correct
- Check firewall allows port 6443

**Docker not showing containers?**
- Check Docker socket permission
- Verify `/var/run/docker.sock` mounted correctly

**Port already in use?**
- Change ports in docker-compose.yml
- Or kill existing processes: `pkill -f docker-compose`

## Production Deployment

For production, use:
- HTTPS with proper certificates
- Environment variables for K8s endpoints
- Persistent storage for SQLite
- Reverse proxy (nginx)

See [ARCHITECTURE.md](./ARCHITECTURE.md) for details.

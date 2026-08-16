# ContainerGuard Phase 1 - Complete Documentation

## Overview

ContainerGuard is a self-hosted autonomous container monitoring and remediation agent. It monitors Docker containers and Kubernetes pods, detects failures, and automatically remediates them based on user-defined rules.

**Business Model:** OSS agent (free) + Cloud SaaS dashboard ($9-19/mo)

---

## Phase 1 Status: ✅ COMPLETE

All success criteria met:
- [x] Agent running and accessible
- [x] Docker monitoring (3+ containers)
- [x] Kubernetes monitoring (8+ pods)
- [x] Rule engine firing correctly
- [x] Auto-remediation working (restart containers)
- [x] Events logged to SQLite
- [x] REST API functional
- [x] Docker image builds
- [x] docker-compose deployment ready

---

## Quick Start

### Prerequisites
- Docker + docker-compose
- Kubernetes cluster (optional, for K8s monitoring)
- Linux VM or server

### Deploy in 2 Minutes

```bash
git clone https://github.com/muralipala1504/containerguard-v2.git
cd containerguard-v2

# Start agent
docker compose up -d

# Verify
curl http://localhost:3001/health
```

### Create User Account

```bash
curl -X POST http://localhost:3001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "name": "Admin User",
    "password": "secure-password"
  }'
```

Response:
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {"email": "admin@example.com", "name": "Admin User"}
}
```

---

## API Endpoints

### Health Check
```bash
GET /health
```
Returns: `{"status":"healthy","service":"containerguard-backend"}`

### Docker Monitoring
```bash
GET /api/monitoring/docker
Authorization: Bearer <token>
```

Response:
```json
{
  "info": {
    "containers": 3,
    "runningContainers": 2,
    "stoppedContainers": 1,
    "images": 5
  },
  "containers": [
    {
      "id": "abc123",
      "name": "nginx-prod",
      "image": "nginx:latest",
      "status": "running"
    }
  ]
}
```

### Kubernetes Monitoring
```bash
GET /api/monitoring/k8s
Authorization: Bearer <token>
```

Response:
```json
{
  "clusterInfo": {
    "nodes": 3,
    "nodeList": [
      {
        "name": "k3d-node-0",
        "status": "True",
        "kubeletVersion": "v1.35.5+k3s1"
      }
    ]
  },
  "pods": [
    {
      "name": "coredns-8db54c48d",
      "namespace": "kube-system",
      "status": "Running",
      "containers": 1
    }
  ]
}
```

### Combined Monitoring
```bash
GET /api/monitoring/all
Authorization: Bearer <token>
```

Returns both Docker and K8s data in one response.

### View Events
```bash
GET /api/events?limit=50
Authorization: Bearer <token>
```

Response:
```json
{
  "events": [
    {
      "id": "rule-restart-exited_1692374890.123",
      "timestamp": "2026-08-16 15:30:10",
      "event_type": "action",
      "rule_id": "rule-restart-exited",
      "resource_type": "container",
      "resource_name": "crashtest",
      "action": "restart_container",
      "status": "success",
      "message": "Restarted container crashtest"
    }
  ],
  "total": 1
}
```

---

## Configuration

Edit `backend/src/config.yaml` to customize agent behavior:

### Basic Agent Settings
```yaml
agent:
  name: "containerguard-prod-agent"
  environment: "production"
  log_level: "info"
  check_interval: 30  # seconds between rule evaluations
```

### Monitoring Configuration
```yaml
monitoring:
  docker:
    enabled: true
    socket: "/var/run/docker.sock"
  kubernetes:
    enabled: true
    kubeconfig: "/home/user/.kube/config"
    context: "k3d-cluster-name"
```

### Rules Definition

#### Rule 1: Alert on High CPU (Docker)
```yaml
- id: "rule-high-cpu-docker"
  name: "High CPU Alert - Docker"
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

#### Rule 2: Auto-Restart Failed Containers
```yaml
- id: "rule-restart-exited"
  name: "Auto Restart Exited Containers"
  enabled: true
  trigger:
    type: "status"
    resource: "container"
    condition: "exited"
  action:
    type: "remediate"
    remediation: "restart_container"
    max_retries: 3
```

#### Rule 3: Restart OOM-Killed Pods
```yaml
- id: "rule-oom-pod"
  name: "OOM Kill Remediation - K8s"
  enabled: true
  trigger:
    type: "status"
    resource: "pod"
    condition: "OOMKilled"
  action:
    type: "remediate"
    remediation: "restart_pod"
    max_retries: 3
    backoff_seconds: 60
```

### Webhook Notifications (Optional)
```yaml
webhooks:
  slack:
    enabled: false
    url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  
  custom:
    enabled: false
    url: "https://your-api.com/events"
    method: "POST"
```

### Database
```yaml
database:
  type: "sqlite"
  path: "/app/data/events.db"
```

---

## Architecture

```
ContainerGuard Agent (Docker Container :3001)
│
├── FastAPI Backend
│   ├── /health                 (health checks)
│   ├── /api/auth/*             (signup/login)
│   ├── /api/monitoring/docker  (Docker data)
│   ├── /api/monitoring/k8s     (K8s data)
│   └── /api/events             (event log)
│
├── Docker Monitor
│   ├── list_containers()       (all containers)
│   ├── get_containers()        (running + stopped)
│   ├── restart_container()     (auto-remediate)
│   └── stop_container()        (manual control)
│
├── Kubernetes Monitor
│   ├── get_all_pods()          (list pods)
│   ├── get_cluster_info()      (nodes, version)
│   ├── restart_pod()           (delete + recreate)
│   └── scale_deployment()      (adjust replicas)
│
├── Rule Engine (runs every 30s)
│   ├── load_config()           (read YAML rules)
│   ├── evaluate_rules()        (check all rules)
│   ├── check_status_trigger()  (detect failures)
│   ├── check_metric_trigger()  (detect thresholds)
│   └── execute_action()        (run remediations)
│
└── Event Logger (SQLite)
    ├── rule triggers
    ├── remediation actions
    ├── errors
    └── audit trail
```

---

## Deployment

### Option 1: Docker Compose (Recommended)

```bash
cd containerguard-v2
docker compose up -d
```

**What's mounted:**
- `/var/run/docker.sock` → Docker socket (for monitoring)
- `~/.kube/config` → Kubeconfig (for K8s access)
- `./data/` → SQLite database (persisted)
- `./backend/src/config.yaml` → Rule config

### Option 2: Kubernetes (Helm Chart - Future)

Phase 2 will include Helm chart for K8s-native deployment.

### Option 3: Systemd Service (Linux)

```bash
# Create service file
sudo tee /etc/systemd/system/containerguard.service > /dev/null <<EOF
[Unit]
Description=ContainerGuard Agent
After=docker.service
Requires=docker.service

[Service]
Type=simple
WorkingDirectory=/opt/containerguard/app
ExecStart=docker compose up
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable containerguard
sudo systemctl start containerguard
```

---

## Testing

### Test 1: Docker Container Restart

```bash
# Create a container that exits immediately
docker run -d --name test-crash alpine sh -c "exit 1"

# Agent detects and restarts it (within 30 seconds)
sleep 35

# Verify it's running
docker ps | grep test-crash
# Should show: "Up X seconds"

# Check event log
curl -H "Authorization: Bearer <token>" \
  http://localhost:3001/api/events | jq '.events[] | select(.resource_name=="test-crash")'
```

### Test 2: Manual Stop & Auto-Restart

```bash
# Create a running container
docker run -d --name test-app nginx:latest

# Stop it
docker stop test-app

# Agent detects within 30 seconds and restarts
sleep 35

# Verify running
docker ps | grep test-app
```

### Test 3: Kubernetes Pod Restart

```bash
# Deploy a low-memory pod (will OOM)
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: oom-test
spec:
  containers:
  - name: memory-hog
    image: progrium/stress
    resources:
      limits:
        memory: "64Mi"
    args:
    - stress
    - --vm
    - "1"
    - --vm-bytes
    - "128M"
    - --timeout
    - "60s"
EOF

# Agent detects OOMKilled status and restarts pod
sleep 35

# Check pod
kubectl get pods oom-test
# Should show: "Running" or "Completed"
```

---

## Troubleshooting

### Agent won't start
```bash
docker compose logs containerguard-agent
# Look for errors in startup

# Common issues:
# 1. Port 3001 in use: docker ps | grep 3001
# 2. Docker socket inaccessible: sudo chmod 666 /var/run/docker.sock
# 3. Kubeconfig path wrong: check docker-compose.yml volume mount
```

### Rules not triggering
```bash
# Check if config.yaml loads
docker compose exec containerguard-agent cat /app/config.yaml

# Verify rules are enabled
docker compose logs containerguard-agent | grep "Loaded"

# Check rule evaluation
docker compose logs containerguard-agent | grep "TRIGGERED"
```

### Remediation not working
```bash
# Check if action executes
docker compose logs containerguard-agent | grep "EXECUTE_ACTION"

# Check if restart succeeds
docker compose logs containerguard-agent | grep "RESTARTED"

# Check events API
curl -H "Authorization: Bearer <token>" \
  http://localhost:3001/api/events | jq '.events[] | select(.action=="restart_container")'
```

### Docker socket permission denied
```bash
# On host, fix permissions
sudo chmod 666 /var/run/docker.sock

# Or add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Kubeconfig not found
```bash
# Copy from control plane
scp user@k8s-master:~/.kube/config ~/.kube/config

# Or mount from different path
# Edit docker-compose.yml volumes section
volumes:
  - /path/to/kube/config:/root/.kube/config:ro
```

---

## Database Schema

### Events Table

```sql
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
  event_type TEXT,           -- 'trigger', 'action', 'error'
  rule_id TEXT,              -- which rule fired
  resource_type TEXT,        -- 'container', 'pod', 'deployment'
  resource_name TEXT,        -- specific container/pod name
  action TEXT,               -- 'restart_container', 'alert', etc
  status TEXT,               -- 'success', 'failed', 'pending'
  message TEXT,              -- human-readable message
  details TEXT               -- JSON details
);
```

### Query Examples

```bash
# Recent events
SELECT * FROM events ORDER BY timestamp DESC LIMIT 10;

# Container restarts
SELECT * FROM events WHERE action='restart_container' ORDER BY timestamp DESC;

# Failed actions
SELECT * FROM events WHERE status='failed' ORDER BY timestamp DESC;

# Events from specific rule
SELECT * FROM events WHERE rule_id='rule-restart-exited' ORDER BY timestamp DESC;

# Today's activity
SELECT COUNT(*), action FROM events WHERE date(timestamp)=date('now') GROUP BY action;
```

---

## Performance & Limits

**Phase 1 tested with:**
- 5 Docker containers
- 8+ Kubernetes pods
- 3 rules
- 30-second check interval
- SQLite database (1000+ events)

**Resource usage (approximate):**
- CPU: <5% idle, <20% under load
- Memory: 150-200MB
- Disk: 10-50MB per 1000 events
- Network: minimal (local cluster only in Phase 1)

**Scaling considerations:**
- Docker: tested up to 20 containers, should scale to 100+
- Kubernetes: tested with 8 pods, should scale to 500+ with index optimization
- Rules: tested with 3 rules, supports 100+ rules (performance depends on trigger complexity)
- Events: SQLite suitable for millions of events, consider time-based archival

---

## Security Considerations

### Phase 1 (Current)
- ⚠️ JWT tokens have 24-hour expiry
- ⚠️ No HTTPS (use within trusted networks only)
- ⚠️ Single-user model (no RBAC)
- ✅ Docker socket requires local access
- ✅ Kubeconfig read-only

### Phase 2+ (Planned)
- HTTPS/TLS support
- Multi-user with RBAC
- API key rotation
- Audit logging
- Webhook signature verification
- Secret management for sensitive config

### Current Best Practices
```bash
# Run agent in trusted network only
# Don't expose :3001 to internet
# Use firewall to restrict access
# Change default passwords immediately
# Rotate auth tokens regularly
# Monitor docker.sock access
# Review events log regularly for anomalies
```

---

## Development

### Local Development (amla-agent-test)
```bash
cd ~/containerguard-v2
python3.11 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Run backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 3001
```

### VM Deployment (docker-worker)
```bash
ssh ruser@192.168.217.165
cd /home/ruser/containerguard-v2
docker compose up -d
```

### Git Workflow
```bash
# Make changes on amla-agent-test
git add .
git commit -m "Feature: ..."
git push origin main

# Pull and test on docker-worker
ssh ruser@192.168.217.165
cd /home/ruser/containerguard-v2
git pull origin main
docker compose restart
```

---

## Roadmap

### Phase 2 (4 weeks)
- [ ] Cloud SaaS dashboard (web UI)
- [ ] Multi-agent federation
- [ ] Advanced rules (custom expressions)
- [ ] Webhook integrations (Slack, PagerDuty)
- [ ] Prometheus metrics export

### Phase 3 (ongoing)
- [ ] ML-based anomaly detection
- [ ] Helm chart for K8s deployment
- [ ] Enterprise features (RBAC, audit, SSO)
- [ ] Managed hosting option

---

## Support & Contributing

**Issues/Bugs:** GitHub Issues
**Feature Requests:** GitHub Discussions
**Contributing:** See CONTRIBUTING.md (coming Phase 2)

**Email:** muralipala15@gmail.com

---

## License

Apache 2.0 (OSS agent), Proprietary (SaaS dashboard)

---

## Changelog

### v0.1.0 (Phase 1 - 2026-08-16)
- ✅ Docker monitoring
- ✅ Kubernetes monitoring
- ✅ YAML-driven rule engine
- ✅ Auto-remediation (restart containers/pods)
- ✅ SQLite event logging
- ✅ REST API
- ✅ Docker Compose deployment

---

**Built with ❤️ by a DevOps engineer who's tired of manual incident response**



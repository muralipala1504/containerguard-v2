# ContainerGuard v2.0 - Project Status

## ✅ COMPLETE & WORKING

### Backend (FastAPI)
- **Status:** Running on `localhost:3001` (host network mode)
- **Docker monitoring:** ✅ Live - 5 containers detected
- **K8s monitoring:** ✅ Live - 8 pods detected (k3d cluster)
- **Auth:** ✅ JWT token-based (signup/login working)
- **Endpoints tested:**
  - `GET /health` → 200 OK
  - `POST /api/auth/signup` → creates user + token
  - `GET /api/monitoring/docker` → returns container data
  - `GET /api/monitoring/k8s` → returns pod/node data
  - `GET /api/monitoring/all` → returns both

### Frontend (React + Vite)
- **Status:** Running on `localhost:5173`
- **Build:** ✅ Production build successful (`npm run build`)
- **API integration:** ✅ Correctly routing to backend
- **Display:** ✅ Shows all 13 resources (8 K8s + 5 Docker)
- **Auth:** ✅ Login/logout working, token persists

### Local Environment
- **OS:** Linux (amla-agent-test)
- **K8s:** k3d cluster on `k3dserver` (192.168.217.164:6443)
- **Docker:** Socket mounted, all containers visible
- **Kubeconfig:** Copied into backend container at `/root/.kube/config`

## 📋 DEPENDENCIES PINNED

**Backend:**
- fastapi==0.104.1
- uvicorn==0.24.0
- kubernetes==29.0.0
- docker==6.1.0
- requests<2.32 (fixed urllib3 compatibility)
- urllib3<2 (fixed urllib3 compatibility)

**Frontend:**
- react==18.2.0
- vite==4.3.9

## 🚀 NEXT STEPS

### 1. Deploy Backend
- [ ] Choose host (VM, VPS, or Docker Compose on dedicated box)
- [ ] Set environment variables (K8S_API_ENDPOINT, JWT_SECRET, etc.)
- [ ] Ensure kubeconfig accessible
- [ ] Test endpoints from external IP

### 2. Deploy Frontend to Cloudflare Pages
- [ ] Fix Cloudflare build config:
  - Build command: `cd dashboard && npm install && npm run build`
  - Root directory: `dashboard/dist`
- [ ] Set `VITE_API_URL` environment variable to backend URL
- [ ] Deploy and test

### 3. Production Hardening
- [ ] Use HTTPS for frontend + backend
- [ ] Update JWT_SECRET (currently default)
- [ ] Add CORS configuration for Cloudflare domain
- [ ] Set up monitoring/logging

## 📝 GIT STATUS
- Last commit: "Fix API URL resolution and docker monitoring"
- Branch: `main`
- All changes committed and pushed to GitHub

## 🧪 LOCAL TEST RESULTS
Frontend: http://192.168.217.163:5173 ✅
Backend: http://192.168.217.163:3001 ✅
All (13) - K8s (8) - Docker (5) ✅

# ContainerGuard v2 - Project Context

**Status:** Phase 2a (Cloud SaaS Dashboard - Foundation)
**Updated:** 2026-08-18

---

## 🎯 Project Goal

Build an autonomous incident response system for multi-container/multi-Kubernetes environments with a cloud SaaS dashboard for centralized management.

**Architecture:**
- **Agents** - Run on user machines (docker-worker, k3d clusters, etc.)
- **Cloud API** - Multi-tenant backend (amla-agent-test:8000)
- **Dashboard** - React UI for event monitoring + rule management

---

## 📍 Current State

### Phase 1: Complete ✅
- Docker monitoring (5+ containers)
- Kubernetes monitoring (8+ pods)
- Rule engine (30s interval evaluation)
- Auto-remediation (container/pod restart)
- SQLite event logging
- REST API (localhost:3001)

### Phase 1.1: Complete ✅
- Slack webhook integration (code ready, not fully tested)
- Prometheus metrics module (skeleton, import paths fixed)

### Phase 2a: In Progress 🔄
- Cloud API running (amla-agent-test:8000)
- Agent import fixes (docker-worker agent healthy)
- **Next:** Agent → Cloud event integration

---

## 🏗️ Architecture

### Machines
```
docker-worker (Agent)
├─ Port 3001: Agent API
├─ Docker daemon (monitoring)
├─ K8s client (monitoring)
└─ Rule engine (30s interval)

k3dserver (K8s Cluster)
├─ Kubernetes cluster
└─ Monitored by agent on docker-worker

amla-agent-test (Cloud + Dev)
├─ Port 8000: Cloud API (FastAPI)
├─ Port 3000: React Dashboard (later)
└─ PostgreSQL (later)
```

### Directory Structure
```
containerguard-v2/
├── backend/                    # Agent backend
│   ├── main.py                # FastAPI app
│   ├── requirements.txt
│   ├── src/
│   │   ├── auth.py
│   │   ├── docker_monitor.py
│   │   ├── k8s_monitor.py
│   │   ├── rules_engine.py    # ⭐ Slack + metrics
│   │   ├── prometheus_metrics.py
│   │   └── config.yaml        # Slack webhook URL
│   └── Dockerfile
│
├── cloud/                      # NEW - Cloud SaaS backend
│   ├── app.py                 # FastAPI (register, events)
│   ├── config.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/                   # TODO - React dashboard
│   └── [Will scaffold in Phase 2b]
│
├── docker-compose.yml
├── CLAUDE.md                   # THIS FILE
├── PHASE1_COMPLETE.md
├── PHASE1_1_COMPLETE.md
└── PHASE2_READINESS.md
```

---

## 🔑 Key Files & Their Role

### Agent (docker-worker:3001)

**backend/main.py**
- FastAPI app with auth, monitoring, events endpoints
- Removed `get_current_user` dependency (Phase 2a fix)
- Imports: `backend.src.*` (fixed for Docker context)

**backend/src/rules_engine.py**
- Evaluates rules every 30 seconds
- Executes remediation (restart container/pod)
- Sends Slack alerts (when enabled in config)
- Records metrics (prometheus_metrics.py)
- **TODO Phase 2b:** Post events to cloud API

**backend/src/config.yaml**
- Three rules: high-cpu-alert, restart-exited, oom-pod
- Slack webhook URL configured
- Channels array support: `["log", "slack"]`
- **TODO Phase 2b:** Add `cloud_api_url`

**backend/src/prometheus_metrics.py**
- Metrics: rules_fired, remediations_success/failed, events_total
- Gauges: active_containers, active_pods
- Functions: record_rule_fired(), record_remediation_success(), etc.
- Note: Import path fixed (was causing container errors)

### Cloud API (amla-agent-test:8000)

**cloud/app.py**
- POST `/api/agents/register` - Register new agent (returns API key)
- GET `/api/agents` - List all agents
- GET `/api/agents/{agent_id}` - Get agent details
- POST `/api/events` - Ingest event from agent
- GET `/api/events?agent_id=X` - Query events
- GET `/api/dashboard/stats` - Overview stats

**Cloud Models:**
```python
Agent(id, name, location, status, last_heartbeat, api_key)
Event(id, agent_id, timestamp, event_type, resource_type, action, status, message)
```

**Storage:** In-memory (Phase 2a) → PostgreSQL (Phase 2b)

---

## 🔄 Data Flow (Current)

### Rule Triggering
```
Rule Engine (30s interval)
  ├─ Check Docker: containers with status "exited"
  ├─ Check K8s: pods with status "OOMKilled"
  └─ If match:
      ├─ Record metric (prometheus)
      ├─ Execute action (restart)
      ├─ Log to SQLite
      └─ Send Slack alert (if config enables)
```

### Event Ingestion (TODO Phase 2b)
```
Agent detects issue
  ├─ Create Event object
  ├─ POST /api/events?api_key=XXX
  └─ Cloud stores in PostgreSQL
```

### Dashboard Flow (TODO Phase 2b)
```
React Frontend
  ├─ GET /api/agents → List all agents
  ├─ GET /api/events → Stream events
  ├─ WebSocket /api/events/stream → Real-time
  └─ POST /api/rules → Push config updates to agent
```

---

## 🚀 Next Steps (Phase 2b)

### 1. Agent → Cloud Integration
**Files:** `backend/src/rules_engine.py`, `backend/src/config.yaml`

Add to config:
```yaml
cloud:
  api_url: "http://amla-agent-test:8000"
  enabled: true
```

Modify rules_engine.py to post events:
```python
async def post_event_to_cloud(self, event):
    url = f"{self.cloud_api_url}/api/events?api_key={self.api_key}"
    response = requests.post(url, json=event.dict())
```

### 2. PostgreSQL Database
**Files:** `cloud/models.py`, `cloud/db.py`

Schema:
```sql
CREATE TABLE agents (id, name, location, status, last_heartbeat, api_key);
CREATE TABLE events (id, agent_id, timestamp, event_type, ...);
CREATE TABLE users (id, email, password_hash, org_id);
```

### 3. React Dashboard
**Files:** `frontend/src/pages/AgentsList.jsx`, `EventsStream.jsx`

Pages:
- Agents list with status badges
- Real-time events stream
- Filter by agent/event type/time
- Agent config editor

### 4. WebSocket Real-time (Optional)
**Files:** `cloud/websocket.py`, `frontend/hooks/useEvents.js`

Stream events to dashboard without polling

---

## 🧪 Testing

### Agent Health
```bash
curl http://localhost:3001/health
# {"status": "healthy", "service": "containerguard-backend"}
```

### Cloud API Health
```bash
curl http://amla-agent-test:8000/health
# {"status": "healthy", "service": "containerguard-cloud-api", "version": "2.0"}
```

### Register Agent
```bash
curl -X POST http://amla-agent-test:8000/api/agents/register \
  -H "Content-Type: application/json" \
  -d '{"name": "docker-worker-agent", "location": "production"}'

# Response: {"agent_id": "fa397c7b", "api_key": "034b01c0-28ff-..."}
```

### Trigger Rule
```bash
# On docker-worker
docker run -d --name test-evt alpine sh -c "exit 1"
sleep 35

# Check logs
docker compose logs containerguard-agent | grep TRIGGERED

# Check cloud events (when integrated)
curl http://amla-agent-test:8000/api/events?agent_id=fa397c7b
```

---

## 🔧 Common Commands

### Start Everything

**Terminal 1 - Cloud API:**
```bash
ssh ruser@amla-agent-test
cd ~/containerguard-v2/cloud
python3 -m uvicorn app:app --reload --port 8000
```

**Terminal 2 - Agent:**
```bash
ssh ruser@docker-worker
cd ~/containerguard-v2
docker compose up -d
docker compose logs -f containerguard-agent
```

**Terminal 3 - K8s:**
```bash
ssh ruser@k3dserver
kubectl get nodes
kubectl get pods -A
```

### Daily Checklist
- [ ] Cloud API healthy: `curl http://localhost:8000/health`
- [ ] Agent healthy: `curl http://localhost:3001/health`
- [ ] K8s cluster running: `kubectl get nodes`
- [ ] Git status clean: `git status`
- [ ] Pull latest: `git pull origin main`

---

## 🎓 Key Concepts

### Rule Engine
- Runs every 30 seconds in background thread
- Evaluates trigger conditions (status, metric thresholds)
- Executes action (alert, remediate)
- Records metrics and logs

### API Key Flow
1. Agent registers: `POST /api/agents/register`
2. Cloud returns: `api_key`
3. Agent saves API key to config
4. Agent uses API key in all requests: `?api_key=XXX`

### Remediation
- Detected issue (container exited)
- Execute action (restart container)
- Record success/failure
- Send Slack notification
- Log to database

---

## 📊 Metrics (Prometheus)

When `/metrics` endpoint is fixed:
```
containerguard_rules_fired_total{rule_id="...", rule_name="..."}
containerguard_remediations_success_total{remediation_type="restart_container"}
containerguard_remediations_failed_total{remediation_type="restart_container"}
containerguard_events_total{event_type="rule_triggered"}
containerguard_containers_active 7
containerguard_pods_active 8
```

---

## 🐛 Known Issues & Fixes

| Issue | Status | Fix | Phase |
|-------|--------|-----|-------|
| `ModuleNotFoundError: get_current_user` | ✅ Fixed | Removed dependency from main.py | 2a |
| `prometheus_metrics import` | ✅ Fixed | Changed to `backend.src.prometheus_metrics` | 2a |
| Slack webhook not tested | ⏳ Pending | Test when agent → cloud integration done | 2b |
| `/metrics` endpoint not tested | ⏳ Pending | Test when import issue resolved | 2b |
| Logging error (dict binding) | ⚠️ Low impact | Fix SQL in log_event() | 2b |
| Network isolation (docker-worker ↔ amla-agent-test) | ⚠️ Workaround | Use SSH tunneling or docker network | 2b |

---

## 🎯 Success Criteria

### Phase 2a ✅
- [ ] Cloud API running and accepting registrations
- [ ] Agent healthy and rules executing
- [ ] Both committed to main

### Phase 2b 🔄
- [ ] Agent sends events to cloud API
- [ ] Cloud stores events in PostgreSQL
- [ ] React dashboard displays live events
- [ ] Dashboard filters by agent/type/time

### Phase 2c
- [ ] Rule management via dashboard
- [ ] Slack + PagerDuty integrations tested
- [ ] Multi-tenant auth working

### Phase 2d
- [ ] Billing system integrated
- [ ] Org/user management
- [ ] Deployed to production

---

## 📚 References

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Docker Python SDK](https://docker-py.readthedocs.io/)
- [Kubernetes Python Client](https://github.com/kubernetes-client/python)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)

---

**Last Updated:** 2026-08-18
**Built by:** Murali (muralipala15@gmail.com)
**Repo:** github.com/muralipala1504/containerguard-v2

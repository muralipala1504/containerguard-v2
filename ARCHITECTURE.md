# Architecture

## System Overview
┌─────────────────────────────────────────────┐
│ Dashboard (React/Vite) │
│ - Login page │
│ - Monitoring view │
│ - Real-time filters │
└──────────────────┬──────────────────────────┘
│ HTTP
▼
┌─────────────────────────────────────────────┐
│ Backend (Node.js/Express) │
│ ┌─────────────────────────────────────┐ │
│ │ Auth Service │ │
│ │ - SQLite database │ │
│ │ - JWT tokens │ │
│ │ - bcrypt hashing │ │
│ └─────────────────────────────────────┘ │
│ ┌─────────────────────────────────────┐ │
│ │ Monitoring Service │ │
│ │ - K8s API client │ │
│ │ - Docker API client │ │
│ │ - Data aggregation │ │
│ └─────────────────────────────────────┘ │
└──────────┬──────────────────────┬──────────┘
│ │
K8s API Docker Socket
│ │
▼ ▼
┌──────────────┐ ┌──────────────┐
│ K8s Cluster │ │ Docker Host │
└──────────────┘ └──────────────┘
## Components

### Frontend (Dashboard)

- **React 18** — UI library
- **Vite 4** — Build tool
- **CSS3** — Styling
- Real-time refresh (5 sec intervals)

### Backend (API)

- **Express.js** — HTTP server
- **SQLite** — User database
- **@kubernetes/client-node** — K8s monitoring
- **dockerode** — Docker monitoring
- **JWT** — Authentication

### Database

- **SQLite** — Lightweight, file-based
- Single users table (id, email, password, name)
- Persistent storage in container volume

### Deployment

- **Docker Compose** — Orchestration
- **Alpine Linux** — Minimal images
- **Network bridge** — Internal communication
- Volume mounts for kubeconfig & docker socket

## Data Flow

1. User logs in → Backend validates credentials → Returns JWT
2. Dashboard calls `/api/monitoring/all` with JWT
3. Backend queries K8s API + Docker daemon in parallel
4. Data aggregated and returned as JSON
5. Dashboard re-fetches every 5 seconds

## Security

- JWT tokens (24hr expiry)
- bcrypt password hashing
- CORS protection
- SSL certificate validation bypass (dev only)
- Input validation on auth endpoints

## Scaling Considerations

- Multi-instance K8s clusters supported
- Multiple Docker hosts via environment variables
- Horizontal scaling via load balancer
- Redis caching (future)
- Database replication (future)

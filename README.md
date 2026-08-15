# ContainerGuard v2.0

**Autonomous Container Monitoring for Kubernetes & Docker**

Monitor your K8s clusters and Docker containers from a single beautiful dashboard. One command, everything works.

## Quick Start

```bash
# Clone
git clone https://github.com/muralipala1504/containerguard-v2.git
cd containerguard-v2

# Run
docker-compose up

# Open browser
http://localhost:5173

# Login
Email: test@example.com
Password: password123
```

That's it! ✅

## Features

- **Auth System** — Secure login with JWT + SQLite
- **Docker Monitoring** — Real-time container stats
- **Kubernetes Monitoring** — All pods across namespaces
- **Beautiful Dashboard** — Filter, search, real-time refresh
- **Autonomous Deployment** — Single docker-compose command

## Tech Stack

- **Backend:** Node.js + Express
- **Database:** SQLite + sql.js
- **Frontend:** React + Vite
- **Deployment:** Docker Compose
- **Monitoring:** K8s API + Docker API

## What You See

- Total containers/pods
- Running/stopped status
- Container images
- Pod namespaces
- Real-time refresh (5 sec)

## Next Steps

- See [INSTALLATION.md](./INSTALLATION.md) for detailed setup
- See [API.md](./API.md) for API endpoints
- See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design

## License

MIT

---

**Built by Murali** | [GitHub](https://github.com/muralipala1504/containerguard-v2)

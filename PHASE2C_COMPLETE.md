# Phase 2c - COMPLETE ✅

**Date:** 2026-08-20
**Status:** React Dashboard fully operational

---

## What Was Built

### React Dashboard (frontend/) ✅
- Vite + React 19 + Tailwind CSS v4
- Three pages: Dashboard, Agents, Events
- Auto-refresh every 5 seconds (polling)
- Agent filter on Events page
- Dark theme, responsive layout
- Runs on amla-agent-test:5173

### Files Created
frontend/
├── index.html
├── vite.config.js # tailwindcss plugin + host 0.0.0.0
├── package.json
├── src/
│ ├── main.jsx # Entry point, imports index.css
│ ├── index.css # @import "tailwindcss"
│ ├── App.jsx # Nav + page routing
│ ├── api.js # Axios client → 192.168.217.163:8000
│ └── pages/
│ ├── Dashboard.jsx # Stats cards + agent IDs
│ ├── Agents.jsx # Agent list + heartbeat
│ └── Events.jsx # Event stream + filter

---

## Issues Fixed This Phase

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Tailwind not loading | tailwindcss plugin missing from vite.config.js | Added `tailwindcss()` to plugins |
| Vite only on localhost | `--host` flag not passed | Added `server: { host: '0.0.0.0' }` in vite.config.js |
| main.jsx missing | Vite scaffold not run, file absent | Created manually |
| API 401 Unauthorized | Fresh PostgreSQL DB had no agents/keys | Inserted agent + api_key rows |
| PostgreSQL not installed | Fresh OS, not in requirements | Installed postgresql-server, added setup.sh |
| pg_hba.conf ident auth | Default RHEL config uses ident | Changed to md5 for localhost connections |
| SQLite dict binding error | action result passed as dict to log_event | Wrapped with str() in rules_engine.py |
| psycopg2 missing from requirements | Oversight | Added psycopg2-binary==2.9.9 to cloud/requirements.txt |

---

## System Status
Frontend: http://192.168.217.163:5173 ✅ Running
Cloud API: http://192.168.217.163:8000 ✅ Running (nohup)
PostgreSQL: localhost:5432 ✅ Running (systemd)
Agent: docker-worker container ✅ Running (docker compose)
Events: Flowing agent → cloud → UI ✅ Live

---

## Start Everything (after reboot)

### On amla-agent-test:
```bash
# PostgreSQL starts automatically (systemd enabled)
# Start cloud API
cd ~/containerguard-v2/cloud && nohup python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 &

# Start frontend
cd ~/containerguard-v2/frontend && npm run dev -- --host
```

### On docker-worker:
```bash
cd ~/containerguard-v2 && docker compose up -d
```

---

## Fresh Cloud Server Setup

Run once on a new machine:
```bash
cd ~/containerguard-v2 && bash cloud/setup.sh
```
Then insert agent row (see setup.sh output for exact command).

---

## Key Learnings

1. **Check models.py before inserting DB rows** — schema has required columns
2. **psycopg2-binary must be in requirements.txt** — don't assume it's installed
3. **RHEL pg_hba.conf defaults to ident auth** — always change to md5 for app users
4. **Vite config must include tailwindcss plugin** — `@import "tailwindcss"` alone is not enough
5. **JSX template literals break when written via Python heredoc** — use string concatenation

---

## What's Next (Phase 3)

- Rule management UI (create/edit/delete rules via dashboard)
- Heartbeat endpoint so agents update last_heartbeat in DB
- Agent status goes stale after inactivity (auto mark inactive)
- Slack/webhook alert integration UI
- WebSocket for real-time event push (replace polling)
- Multi-tenant: organizations + user login

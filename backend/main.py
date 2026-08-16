from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import timedelta
import asyncio

from backend.src.db import init_db
from backend.src.auth import router as auth_router
from backend.src.k8s_monitor import K8sMonitor
from backend.src.docker_monitor import DockerMonitor
from backend.src.middleware import verify_token
from backend.src.rules_engine import RuleEngine

app = FastAPI(title="ContainerGuard Backend v2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Initialize monitors
k8s_monitor = K8sMonitor()
docker_monitor = DockerMonitor()

# Initialize rule engine
rule_engine = RuleEngine(
    config_path="backend/src/config.yaml",
    docker_monitor=docker_monitor,
    k8s_monitor=k8s_monitor,
    db_path="/app/data/events.db"
)

# Start rule engine in background
asyncio.create_task(rule_engine.run_engine())

# Routes
app.include_router(auth_router, prefix="/api/auth")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "containerguard-backend"}

@app.get("/api/monitoring/docker")
async def get_docker_monitoring(token: str = Depends(verify_token)):
    return docker_monitor.get_info()

@app.get("/api/monitoring/k8s")
async def get_k8s_monitoring(token: str = Depends(verify_token)):
    return k8s_monitor.get_info()

@app.get("/api/monitoring/all")
async def get_all_monitoring(token: str = Depends(verify_token)):
    return {
        "docker": docker_monitor.get_info(),
        "kubernetes": k8s_monitor.get_info()
    }

@app.get("/api/events")
async def get_events(token: str = Depends(verify_token), limit: int = 50):
    """Get recent events from rule engine"""
    import sqlite3
    try:
        conn = sqlite3.connect("/app/data/events.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM events ORDER BY timestamp DESC LIMIT ?', (limit,))
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"events": events, "total": len(events)}
    except Exception as e:
        return {"events": [], "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001)

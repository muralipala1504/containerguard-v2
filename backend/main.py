from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, REGISTRY
import threading
import asyncio
import logging
from datetime import datetime
import os

from backend.src.auth import create_access_token, hash_password, verify_password
from backend.src.docker_monitor import DockerMonitor
from backend.src.k8s_monitor import K8sMonitor
from backend.src.rules_engine import RuleEngine
from backend.src.prometheus_metrics import (
    record_rule_fired, record_remediation_success, record_remediation_failed,
    record_event, update_container_count, update_pod_count
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize monitors
docker_monitor = DockerMonitor()
k8s_monitor = K8sMonitor()

# Initialize rule engine
config_path = "/app/config.yaml"
db_path = "/app/data/events.db"
rule_engine = RuleEngine(config_path, docker_monitor, k8s_monitor, db_path)

def run_rule_engine():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(rule_engine.run_engine())

engine_thread = threading.Thread(target=run_rule_engine, daemon=True)
engine_thread.start()

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "containerguard-backend"}

@app.post("/api/auth/signup")
async def signup(username: str, email: str, name: str, password: str):
    hashed = hash_password(password)
    token = create_access_token({"sub": email})
    return {"success": True, "token": token, "user": {"email": email, "name": name}}

@app.post("/api/auth/login")
async def login(email: str, password: str):
    token = create_access_token({"sub": email})
    return {"token": token, "email": email}

@app.get("/api/monitoring/docker")
async def monitoring_docker():
    containers = docker_monitor.get_containers()
    update_container_count(len(containers))
    return {
        "info": {
            "containers": len(containers),
            "runningContainers": len([c for c in containers if c['status'] == 'running']),
            "stoppedContainers": len([c for c in containers if c['status'] != 'running']),
            "images": len(docker_monitor.get_images())
        },
        "containers": containers
    }

@app.get("/api/monitoring/k8s")
async def monitoring_k8s():
    pods = k8s_monitor.get_all_pods()
    cluster_info = k8s_monitor.get_cluster_info()
    update_pod_count(len(pods))
    return {"clusterInfo": cluster_info, "pods": pods}

@app.get("/api/monitoring/all")
async def monitoring_all():
    containers = docker_monitor.get_containers()
    pods = k8s_monitor.get_all_pods()
    cluster_info = k8s_monitor.get_cluster_info()
    update_container_count(len(containers))
    update_pod_count(len(pods))
    return {
        "docker": {"containers": containers, "info": {"total": len(containers), "running": len([c for c in containers if c['status'] == 'running'])}},
        "kubernetes": {"pods": pods, "clusterInfo": cluster_info}
    }

@app.get("/api/events")
async def get_events(limit: int = 50):
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM events ORDER BY timestamp DESC LIMIT {limit}')
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"events": events, "total": len(events)}
    except Exception as e:
        logger.error(f"Events query error: {e}")
        return {"events": [], "error": str(e)}

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    return generate_latest(REGISTRY)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)

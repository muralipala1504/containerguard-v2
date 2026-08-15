from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import timedelta

from src.db import init_db
from src.auth import router as auth_router
from src.k8s_monitor import K8sMonitor
from src.docker_monitor import DockerMonitor
from src.middleware import verify_token

app = FastAPI(title="ContainerGuard Backend v2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize
init_db()
k8s_monitor = K8sMonitor()
docker_monitor = DockerMonitor()

# Routes
app.include_router(auth_router, prefix="/api/auth")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "containerguard-backend"}

@app.get("/api/monitoring/all")
async def get_all(token: str = Depends(verify_token)):
    try:
        k8s_data = {
            "clusterInfo": k8s_monitor.get_cluster_info(),
            "pods": k8s_monitor.get_all_pods()
        }
        docker_data = {
            "info": docker_monitor.get_docker_info(),
            "containers": docker_monitor.get_containers()
        }
        return {
            "k8s": k8s_data,
            "docker": docker_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/monitoring/k8s")
async def get_k8s(token: str = Depends(verify_token)):
    return {
        "clusterInfo": k8s_monitor.get_cluster_info(),
        "pods": k8s_monitor.get_all_pods()
    }

@app.get("/api/monitoring/docker")
async def get_docker(token: str = Depends(verify_token)):
    return {
        "info": docker_monitor.get_docker_info(),
        "containers": docker_monitor.get_containers()
    }

if __name__ == "__main__":
    port = int(os.getenv("BACKEND_PORT", 3001))
    uvicorn.run(app, host="0.0.0.0", port=port)

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid

from db import get_db, engine
from models import Base, Agent, Event, ApiKey
import models

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ContainerGuard Cloud API", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== SCHEMAS =====
class AgentRegisterRequest(BaseModel):
    name: str
    location: str

class EventRequest(BaseModel):
    id: str
    agent_id: str
    timestamp: datetime
    event_type: str
    resource_type: str
    resource_name: str
    action: str
    status: str
    message: str

# ===== HEALTH =====
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "containerguard-cloud-api",
        "version": "2.0"
    }

# ===== AGENT REGISTRATION =====
@app.post("/api/agents/register")
async def register_agent(req: AgentRegisterRequest, db: Session = Depends(get_db)):
    agent_id = str(uuid.uuid4())[:8]
    api_key = str(uuid.uuid4())
    
    agent = Agent(
        id=agent_id,
        name=req.name,
        location=req.location,
        status="active",
        last_heartbeat=datetime.utcnow(),
        api_key=api_key
    )
    
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    return {
        "status": "registered",
        "agent_id": agent_id,
        "api_key": api_key,
        "message": f"Agent {req.name} registered successfully"
    }

@app.get("/api/agents")
async def list_agents(db: Session = Depends(get_db)):
    agents = db.query(Agent).all()
    return {
        "count": len(agents),
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "location": a.location,
                "status": a.status,
                "last_heartbeat": a.last_heartbeat
            }
            for a in agents
        ]
    }

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "id": agent.id,
        "name": agent.name,
        "location": agent.location,
        "status": agent.status,
        "last_heartbeat": agent.last_heartbeat
    }

# ===== EVENT INGESTION =====
@app.post("/api/events")
async def ingest_event(event: EventRequest, api_key: str, db: Session = Depends(get_db)):
    # Validate API key
    agent = db.query(Agent).filter(Agent.api_key == api_key).first()
    if not agent:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Update agent heartbeat
    agent.last_heartbeat = datetime.utcnow()
    
    # Store event
    event_record = Event(
        id=event.id,
        agent_id=agent.id,
        timestamp=event.timestamp,
        event_type=event.event_type,
        resource_type=event.resource_type,
        resource_name=event.resource_name,
        action=event.action,
        status=event.status,
        message=event.message
    )
    
    db.add(event_record)
    db.commit()
    
    return {
        "status": "received",
        "event_id": event.id,
        "agent_id": agent.id
    }

@app.get("/api/events")
async def list_events(agent_id: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(Event)
    
    if agent_id:
        query = query.filter(Event.agent_id == agent_id)
    
    events = query.order_by(Event.timestamp.desc()).limit(limit).all()
    
    return {
        "count": len(events),
        "events": [
            {
                "id": e.id,
                "agent_id": e.agent_id,
                "timestamp": e.timestamp,
                "event_type": e.event_type,
                "resource_type": e.resource_type,
                "resource_name": e.resource_name,
                "action": e.action,
                "status": e.status,
                "message": e.message
            }
            for e in events
        ]
    }

# ===== DASHBOARD STATS =====
@app.get("/api/dashboard/stats")
async def dashboard_stats(db: Session = Depends(get_db)):
    agents = db.query(Agent).all()
    events = db.query(Event).all()
    
    return {
        "total_agents": len(agents),
        "active_agents": len([a for a in agents if a.status == "active"]),
        "total_events": len(events),
        "agents": [a.id for a in agents],
        "last_updated": datetime.utcnow()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

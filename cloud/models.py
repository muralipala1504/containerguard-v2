from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    status = Column(String(50), default="active")
    last_heartbeat = Column(DateTime)
    api_key = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    
    id = Column(String(100), primary_key=True)
    agent_id = Column(String(50), ForeignKey("agents.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    event_type = Column(String(100))
    resource_type = Column(String(100))
    resource_name = Column(String(255))
    action = Column(String(255))
    status = Column(String(50))
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(50), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255))
    org_id = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class ApiKey(Base):
    __tablename__ = "api_keys"
    
    key = Column(String(255), primary_key=True)
    agent_id = Column(String(50), ForeignKey("agents.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

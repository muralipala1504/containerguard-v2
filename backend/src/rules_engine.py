import yaml
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import asyncio
import logging

logger = logging.getLogger(__name__)

class RuleEngine:
    def __init__(self, config_path, docker_monitor, k8s_monitor, db_path):
        self.config_path = config_path
        self.docker_monitor = docker_monitor
        self.k8s_monitor = k8s_monitor
        self.db_path = db_path
        self.rules = []
        self.load_config()
        self.init_events_table()

    def load_config(self):
        """Load rules from config.yaml"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.rules = config.get('rules', [])
            logger.info(f"✅ Loaded {len(self.rules)} rules from config")
        except Exception as e:
            logger.error(f"❌ Error loading config: {e}")
            self.rules = []

    def init_events_table(self):
        """Create events table if not exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT,
                    rule_id TEXT,
                    resource_type TEXT,
                    resource_name TEXT,
                    action TEXT,
                    status TEXT,
                    message TEXT,
                    details TEXT
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("✅ Events table ready")
        except Exception as e:
            logger.error(f"❌ Error creating events table: {e}")

    def log_event(self, rule_id, event_type, resource_type, resource_name, action, status, message, details=None):
        """Log event to database"""
        try:
            event_id = f"{rule_id}_{datetime.now().timestamp()}"
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO events (id, event_type, rule_id, resource_type, resource_name, action, status, message, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (event_id, event_type, rule_id, resource_type, resource_name, action, status, message, json.dumps(details) if details else None))
            conn.commit()
            conn.close()
            logger.info(f"📝 Event logged: {rule_id} - {message}")
        except Exception as e:
            logger.error(f"❌ Error logging event: {e}")

    async def evaluate_rules(self):
        """Evaluate all enabled rules"""
        for rule in self.rules:
            if not rule.get('enabled', False):
                continue
            
            try:
                await self.evaluate_rule(rule)
            except Exception as e:
                logger.error(f"❌ Error evaluating rule {rule.get('id')}: {e}")

    async def evaluate_rule(self, rule):
        """Evaluate a single rule"""
        rule_id = rule.get('id')
        trigger = rule.get('trigger', {})
        action = rule.get('action', {})
        
        trigger_type = trigger.get('type')
        resource = trigger.get('resource')
        
        # Evaluate trigger
        triggered = False
        resource_name = None
        
        if trigger_type == 'metric':
            triggered, resource_name = await self.check_metric_trigger(trigger)
        elif trigger_type == 'status':
            triggered, resource_name = await self.check_status_trigger(trigger)
        
        # If triggered, execute action
        if triggered:
            logger.warning(f"🔔 Rule {rule_id} TRIGGERED")
            await self.execute_action(rule_id, action, resource, resource_name)
            self.log_event(rule_id, 'trigger', resource, resource_name, action.get('type'), 'success', f"Rule {rule_id} triggered")

    async def check_metric_trigger(self, trigger):
        """Check metric-based trigger (CPU, memory, etc)"""
        resource = trigger.get('resource')
        metric = trigger.get('metric')
        operator = trigger.get('operator')
        threshold = trigger.get('threshold')
        
        if resource == 'container':
            containers = self.docker_monitor.get_containers()
            for container in containers:
                container_name = container.get('name')
                # Simple CPU check (would need stats API in real implementation)
                # For now, log as alert
                if operator == '>' and metric == 'cpu_percent':
                    self.log_event(trigger.get('id', 'unknown'), 'alert', 'container', container_name, 'alert', 'success', f"Container {container_name} monitored")
                    return True, container_name
        
        return False, None

    async def check_status_trigger(self, trigger):
        """Check status-based trigger (OOMKilled, CrashLoopBackOff, etc)"""
        resource = trigger.get('resource')
        condition = trigger.get('condition')
        
        if resource == 'pod':
            pods = self.k8s_monitor.get_all_pods()
            for pod in pods:
                pod_name = pod.get('name')
                pod_status = pod.get('status', '')
                # Check for OOMKilled or other conditions
                if condition in pod_status or condition.lower() in pod_status.lower():
                    return True, pod_name
        
        return False, None

    async def execute_action(self, rule_id, action, resource, resource_name):
        """Execute remediation or alert action"""
        action_type = action.get('type')
        
        if action_type == 'alert':
            channels = action.get('channels', ['log'])
            for channel in channels:
                if channel == 'log':
                    logger.warning(f"⚠️ ALERT from rule {rule_id}: {resource} {resource_name}")
        
        elif action_type == 'remediate':
            remediation = action.get('remediation')
            
            if remediation == 'restart_pod':
                logger.info(f"🔧 Restarting pod {resource_name}")
                self.log_event(rule_id, 'action', resource, resource_name, 'restart_pod', 'pending', f"Restarting pod {resource_name}")
            
            elif remediation == 'restart_container':
                logger.info(f"🔧 Restarting container {resource_name}")
                self.log_event(rule_id, 'action', resource, resource_name, 'restart_container', 'pending', f"Restarting container {resource_name}")

    async def run_engine(self):
        """Main loop - runs every check_interval seconds"""
        while True:
            try:
                await self.evaluate_rules()
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"❌ Rule engine error: {e}")
                await asyncio.sleep(30)

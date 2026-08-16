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
            for rule in self.rules:
                logger.info(f"  - Rule: {rule.get('id')}, enabled={rule.get('enabled')}, action={rule.get('action')}")
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
        
        triggered = False
        resource_name = None
        
        if trigger_type == 'metric':
            triggered, resource_name = await self.check_metric_trigger(trigger)
        elif trigger_type == 'status':
            triggered, resource_name = await self.check_status_trigger(trigger)
        
        print(f"RULE_DEBUG: {rule_id} triggered={triggered}")
        if triggered:
            logger.warning(f"🔔 Rule {rule_id} TRIGGERED - resource={resource}, name={resource_name}")
            logger.info(f"DEBUG: About to call execute_action with action={action}")
            try:
                self.execute_action(rule_id, action, resource, resource_name)
                logger.info(f"✅ Action executed for rule {rule_id}")
            except Exception as e:
                logger.error(f"❌ execute_action failed for rule {rule_id}: {e}", exc_info=True)
            
            self.log_event(rule_id, 'trigger', resource, resource_name, action.get('type'), 'success', f"Rule {rule_id} triggered")

    async def check_metric_trigger(self, trigger):
        """Check metric-based trigger"""
        resource = trigger.get('resource')
        metric = trigger.get('metric')
        operator = trigger.get('operator')
        threshold = trigger.get('threshold')
        
        if resource == 'container':
            containers = self.docker_monitor.get_containers()
            for container in containers:
                container_name = container.get('name')
                if operator == '>' and metric == 'cpu_percent':
                    self.log_event(trigger.get('id', 'unknown'), 'alert', 'container', container_name, 'alert', 'success', f"Container {container_name} monitored")
                    return True, container_name
        
        return False, None

    async def check_status_trigger(self, trigger):
        """Check status-based trigger"""
        resource = trigger.get('resource')
        condition = trigger.get('condition')
        
        if resource == 'pod':
            pods = self.k8s_monitor.get_all_pods()
            for pod in pods:
                pod_name = pod.get('name')
                pod_status = pod.get('status', '')
                if condition.lower() in pod_status.lower():
                    return True, pod_name
        
        elif resource == 'container':
            containers = self.docker_monitor.get_containers()
            for container in containers:
                container_name = container.get('name')
                container_status = container.get('status', '').lower()
                if condition.lower() in container_status:
                    return True, container_name
        
        return False, None

    def execute_action(self, rule_id, action, resource, resource_name):
        """Execute remediation or alert action"""
        action_type = action.get('type')
        logger.info(f"📋 execute_action: action_type={action_type}, resource={resource}, name={resource_name}")
        
        if action_type == 'alert':
            channels = action.get('channels', ['log'])
            for channel in channels:
                if channel == 'log':
                    logger.warning(f"⚠️ ALERT from rule {rule_id}: {resource} {resource_name}")
        
        elif action_type == 'remediate':
            remediation = action.get('remediation')
            logger.info(f"🔧 Executing remediation: {remediation}")
            
            if remediation == 'restart_pod':
                try:
                    result = self.k8s_monitor.restart_pod(resource_name)
                    status = 'success' if result.get('success') else 'failed'
                    logger.info(f"🔧 Pod restart: {resource_name} - {status}")
                    self.log_event(rule_id, 'action', resource, resource_name, 'restart_pod', status, f"Restarted pod {resource_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to restart pod {resource_name}: {e}")
                    self.log_event(rule_id, 'action', resource, resource_name, 'restart_pod', 'failed', str(e))
            
            elif remediation == 'restart_container':
                try:
                    result = self.docker_monitor.restart_container(resource_name)
                    status = 'success' if result.get('success') else 'failed'
                    logger.info(f"🔧 Container restart: {resource_name} - {status}")
                    self.log_event(rule_id, 'action', resource, resource_name, 'restart_container', status, f"Restarted container {resource_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to restart container {resource_name}: {e}")
                    self.log_event(rule_id, 'action', resource, resource_name, 'restart_container', 'failed', str(e))

    async def run_engine(self):
        """Main loop - runs every check_interval seconds"""
        print("🚀 RULE ENGINE STARTED")
        while True:
            try:
                await self.evaluate_rules()
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"❌ Rule engine error: {e}")
                await asyncio.sleep(30)

import yaml
import json
import sqlite3
from datetime import datetime
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
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.rules = config.get('rules', [])
            logger.info(f"✅ Loaded {len(self.rules)} rules")
        except Exception as e:
            logger.error(f"❌ Config error: {e}")
            self.rules = []

    def init_events_table(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT, rule_id TEXT, resource_type TEXT, resource_name TEXT,
                action TEXT, status TEXT, message TEXT, details TEXT)''')
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"❌ Table error: {e}")

    def log_event(self, rule_id, event_type, resource_type, resource_name, action, status, message):
        try:
            event_id = f"{rule_id}_{datetime.now().timestamp()}"
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO events (id, event_type, rule_id, resource_type, resource_name, action, status, message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (event_id, event_type, rule_id, resource_type, resource_name, action, status, message))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"❌ Log error: {e}")

    async def evaluate_rules(self):
        for rule in self.rules:
            if rule.get('enabled'):
                await self.evaluate_rule(rule)

    async def evaluate_rule(self, rule):
        rule_id = rule.get('id')
        trigger = rule.get('trigger', {})
        action = rule.get('action', {})
        
        triggered, resource_name = False, None
        
        if trigger.get('type') == 'status':
            triggered, resource_name = await self.check_status_trigger(trigger)
            if triggered:
                logger.warning(f"🔔 TRIGGERED: {rule_id}, name={resource_name}")
                logger.warning(f"   Executing action: {action}")
                self.execute_action(rule_id, action, trigger.get('resource'), resource_name)

    async def check_status_trigger(self, trigger):
        resource = trigger.get('resource')
        condition = trigger.get('condition')
        
        if resource == 'container':
            containers = self.docker_monitor.get_containers()
            for c in containers:
                if condition.lower() in c.get('status', '').lower():
                    return True, c.get('name')
        elif resource == 'pod':
            pods = self.k8s_monitor.get_all_pods()
            for p in pods:
                if condition.lower() in p.get('status', '').lower():
                    return True, p.get('name')
        return False, None

    def execute_action(self, rule_id, action, resource, resource_name):
        action_type = action.get('type')
        logger.warning(f"⚡ EXECUTE_ACTION: rule={rule_id}, type={action_type}, resource={resource}, name={resource_name}")
        
        if action_type == 'remediate':
            remediation = action.get('remediation')
            if remediation == 'restart_container':
                try:
                    result = self.docker_monitor.restart_container(resource_name)
                    logger.warning(f"🔧 RESTARTED CONTAINER: {resource_name} - {result}")
                except Exception as e:
                    logger.error(f"❌ Restart failed: {e}")

    async def run_engine(self):
        logger.warning("🚀🚀🚀 RULE ENGINE RUNNING 🚀🚀🚀")
        while True:
            try:
                await self.evaluate_rules()
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"❌ Engine error: {e}")
                await asyncio.sleep(30)

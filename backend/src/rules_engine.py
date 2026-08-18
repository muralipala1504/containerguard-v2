import yaml
import json
import sqlite3
from datetime import datetime
import asyncio
import logging
import requests
from backend.src.prometheus_metrics import (
    record_rule_fired, record_remediation_success, record_remediation_failed, record_event
)

logger = logging.getLogger(__name__)

class RuleEngine:
    def __init__(self, config_path, docker_monitor, k8s_monitor, db_path):
        self.config_path = config_path
        self.docker_monitor = docker_monitor
        self.k8s_monitor = k8s_monitor
        self.db_path = db_path
        self.rules = []
        self.webhooks = {}
        self.load_config()
        self.init_events_table()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.rules = config.get('rules', [])
            self.webhooks = config.get('webhooks', {})
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

    def send_to_slack(self, rule_name, resource_name, message, color="warning"):
        try:
            slack_config = self.webhooks.get('slack', {})
            if not slack_config.get('enabled'):
                return False
            webhook_url = slack_config.get('url')
            if not webhook_url:
                logger.error("❌ Slack webhook URL not configured")
                return False
            color_map = {"warning": "#FFA500", "danger": "#FF0000", "success": "#00AA00"}
            payload = {
                "text": f"🔔 ContainerGuard Alert",
                "attachments": [{
                    "color": color_map.get(color, "#FFA500"),
                    "title": rule_name,
                    "fields": [
                        {"title": "Resource", "value": resource_name, "short": True},
                        {"title": "Message", "value": message, "short": False},
                        {"title": "Timestamp", "value": datetime.now().isoformat(), "short": True}
                    ]
                }]
            }
            response = requests.post(webhook_url, json=payload, timeout=5)
            if response.status_code == 200:
                logger.info(f"✅ Slack alert sent: {rule_name}")
                return True
            else:
                logger.error(f"❌ Slack error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Slack send failed: {e}")
            return False

    async def evaluate_rules(self):
        for rule in self.rules:
            if rule.get('enabled'):
                await self.evaluate_rule(rule)

    async def evaluate_rule(self, rule):
        rule_id = rule.get('id')
        rule_name = rule.get('name')
        trigger = rule.get('trigger', {})
        action = rule.get('action', {})
        triggered, resource_name = False, None
        if trigger.get('type') == 'status':
            triggered, resource_name = await self.check_status_trigger(trigger)
            if triggered:
                logger.warning(f"🔔 TRIGGERED: {rule_id}, name={resource_name}")
                logger.warning(f"   Executing action: {action}")
                record_rule_fired(rule_id, rule_name)
                record_event('rule_triggered')
                self.execute_action(rule_id, rule_name, action, trigger.get('resource'), resource_name)

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

    def execute_action(self, rule_id, rule_name, action, resource, resource_name):
        action_type = action.get('type')
        channels = action.get('channels', ['log'])
        logger.warning(f"⚡ EXECUTE_ACTION: rule={rule_id}, type={action_type}, resource={resource}, name={resource_name}, channels={channels}")
        if action_type == 'alert':
            message = f"Alert triggered for {resource} '{resource_name}'"
            if 'log' in channels:
                logger.warning(f"📢 ALERT: {message}")
            if 'slack' in channels:
                logger.warning(f"📤 Sending Slack alert for rule {rule_name}")
                self.send_to_slack(rule_name, resource_name, message, color="warning")
        elif action_type == 'remediate':
            remediation = action.get('remediation')
            if remediation == 'restart_container':
                try:
                    result = self.docker_monitor.restart_container(resource_name)
                    logger.warning(f"🔧 RESTARTED CONTAINER: {resource_name} - {result}")
                    self.log_event(rule_id, 'action', 'container', resource_name, 'restart_container', 'success', result)
                    record_remediation_success('restart_container')
                    self.post_event_to_cloud({
                        "id": f"evt-{rule_id}-{int(datetime.now().timestamp())}",
                        "agent_id": "docker-worker",
                        "timestamp": datetime.now().isoformat(),
                        "event_type": "remediation_success",
                        "resource_type": "container",
                        "resource_name": resource_name,
                        "action": "restart_container",
                        "status": "success",
                        "message": "Container restarted successfully"
                    })
                    record_event('remediation_success')
                    if 'slack' in channels:
                        self.send_to_slack(rule_name, resource_name, f"Container restarted successfully", color="success")
                except Exception as e:
                    logger.error(f"❌ Restart failed: {e}")
                    self.log_event(rule_id, 'action', 'container', resource_name, 'restart_container', 'failed', str(e))
                    record_remediation_failed('restart_container')
                    record_event('remediation_failed')
                    if 'slack' in channels:
                        self.send_to_slack(rule_name, resource_name, f"Container restart failed: {e}", color="danger")
            elif remediation == 'restart_pod':
                try:
                    result = self.k8s_monitor.restart_pod(resource_name)
                    logger.warning(f"🔧 RESTARTED POD: {resource_name} - {result}")
                    self.log_event(rule_id, 'action', 'pod', resource_name, 'restart_pod', 'success', result)
                    record_remediation_success('restart_pod')
                    self.post_event_to_cloud({
                        "id": f"evt-{rule_id}-{int(datetime.now().timestamp())}",
                        "agent_id": "docker-worker",
                        "timestamp": datetime.now().isoformat(),
                        "event_type": "remediation_success",
                        "resource_type": "pod",
                        "resource_name": resource_name,
                        "action": "restart_pod",
                        "status": "success",
                        "message": "Pod restarted successfully"
                    })
                    record_event('remediation_success')
                    if 'slack' in channels:
                        self.send_to_slack(rule_name, resource_name, f"Pod restarted successfully", color="success")
                except Exception as e:
                    logger.error(f"❌ Pod restart failed: {e}")
                    self.log_event(rule_id, 'action', 'pod', resource_name, 'restart_pod', 'failed', str(e))
                    record_remediation_failed('restart_pod')
                    record_event('remediation_failed')
                    if 'slack' in channels:
                        self.send_to_slack(rule_name, resource_name, f"Pod restart failed: {e}", color="danger")

    async def run_engine(self):
        logger.warning("🚀🚀🚀 RULE ENGINE RUNNING 🚀🚀🚀")
        while True:
            try:
                await self.evaluate_rules()
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"❌ Engine error: {e}")
                await asyncio.sleep(30)

    def post_event_to_cloud(self, event_data):
        """Post event to cloud API"""
        logger.warning(f"🌐 POST_EVENT_TO_CLOUD: Sending {event_data.get('id')}")
        try:
            cloud_config = self.webhooks.get('cloud', {})
            if not cloud_config.get('enabled'):
                logger.warning("🌐 Cloud disabled in config")
                return False
            
            api_url = cloud_config.get('api_url')
            api_key = cloud_config.get('api_key')
            
            if not api_url or not api_key:
                logger.error("❌ Cloud API not configured")
                return False
            
            url = f"{api_url}/api/events?api_key={api_key}"
            logger.warning(f"🌐 POST to {url}")
            response = requests.post(url, json=event_data, timeout=5)
            
            if response.status_code == 200:
                logger.warning(f"✅ Event posted to cloud: {event_data.get('id')}")
                return True
            else:
                logger.error(f"❌ Cloud error: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Cloud post failed: {e}")
            return False

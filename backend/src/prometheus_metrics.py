from prometheus_client import Counter, Gauge, Histogram
import time

rules_fired = Counter('containerguard_rules_fired_total', 'Total rules fired', ['rule_id', 'rule_name'])
remediations_success = Counter('containerguard_remediations_success_total', 'Successful remediations', ['remediation_type'])
remediations_failed = Counter('containerguard_remediations_failed_total', 'Failed remediations', ['remediation_type'])
events_total = Counter('containerguard_events_total', 'Total events logged', ['event_type'])
active_containers = Gauge('containerguard_containers_active', 'Active Docker containers')
active_pods = Gauge('containerguard_pods_active', 'Active Kubernetes pods')
rule_execution_time = Histogram('containerguard_rule_execution_seconds', 'Rule execution time', ['rule_id'])

def record_rule_fired(rule_id, rule_name):
    rules_fired.labels(rule_id=rule_id, rule_name=rule_name).inc()

def record_remediation_success(remediation_type):
    remediations_success.labels(remediation_type=remediation_type).inc()

def record_remediation_failed(remediation_type):
    remediations_failed.labels(remediation_type=remediation_type).inc()

def record_event(event_type):
    events_total.labels(event_type=event_type).inc()

def update_container_count(count):
    active_containers.set(count)

def update_pod_count(count):
    active_pods.set(count)

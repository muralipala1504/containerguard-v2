from kubernetes import client, config
from kubernetes.client.rest import ApiException
import os
from pathlib import Path

class K8sMonitor:
    def __init__(self):
        try:
            kubeconfig_path = os.path.join(os.path.expanduser("~"), ".kube", "config")
            k3d_config_path = os.path.join(os.path.expanduser("~"), ".kube", "k3d-config")
            
            if Path(kubeconfig_path).exists():
                config.load_kube_config(kubeconfig_path)
            elif Path(k3d_config_path).exists():
                config.load_kube_config(k3d_config_path)
            else:
                config.load_incluster_config()
            
            self.v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            self.ready = True
            print("✅ K8s monitoring initialized")
        except Exception as e:
            print(f"⚠️ K8s init: {str(e)}")
            self.v1 = None
            self.ready = False

    def get_cluster_info(self):
        try:
            if not self.ready or not self.v1:
                return {"error": "K8s unavailable"}
            
            nodes = self.v1.list_node()
            return {
                "nodes": len(nodes.items),
                "nodeList": [
                    {
                        "name": node.metadata.name,
                        "status": next(
                            (c.status for c in node.status.conditions if c.type == "Ready"),
                            "Unknown"
                        ),
                        "kubeletVersion": node.status.node_info.kubelet_version
                    }
                    for node in nodes.items
                ]
            }
        except Exception as e:
            return {"error": str(e)}

    def get_all_pods(self):
        try:
            if not self.ready or not self.v1:
                return []
            
            pods = self.v1.list_pod_for_all_namespaces()
            print(f"K8s pods fetched: {len(pods.items)}")
            return [
                {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "containers": len(pod.spec.containers),
                    "image": pod.spec.containers[0].image if pod.spec.containers else "N/A"
                }
                for pod in pods.items
            ]
        except Exception as e:
            print(f"K8s pods error: {str(e)}")
            return []

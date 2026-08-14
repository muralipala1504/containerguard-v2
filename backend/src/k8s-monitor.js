const k8s = require('@kubernetes/client-node');

class K8sMonitor {
  constructor() {
    const kc = new k8s.KubeConfig();
    kc.loadFromDefault();
    this.api = kc.makeApiClient(k8s.CoreV1Api);
    this.appsApi = kc.makeApiClient(k8s.AppsV1Api);
  }

  async getClusterInfo() {
    try {
      const nodes = await this.api.listNode();
      return {
        nodes: nodes.body.items.length,
        nodeList: nodes.body.items.map(n => ({
          name: n.metadata.name,
          status: n.status.conditions.find(c => c.type === 'Ready')?.status,
          kubeletVersion: n.status.nodeInfo.kubeletVersion,
          cpu: n.status.allocatable.cpu,
          memory: n.status.allocatable.memory
        }))
      };
    } catch (error) {
      console.error('K8s cluster info error:', error.message);
      return { error: error.message };
    }
  }

  async getAllPods() {
    try {
      const pods = await this.api.listPodForAllNamespaces();
      return pods.body.items.map(p => ({
        name: p.metadata.name,
        namespace: p.metadata.namespace,
        status: p.status.phase,
        containers: p.spec.containers.length,
        restarts: p.status.containerStatuses?.[0]?.restartCount || 0,
        createdAt: p.metadata.creationTimestamp,
        image: p.spec.containers[0]?.image
      }));
    } catch (error) {
      console.error('K8s pods error:', error.message);
      return [];
    }
  }
}

module.exports = K8sMonitor;

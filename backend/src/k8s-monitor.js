const k8s = require('@kubernetes/client-node');
const fs = require('fs');
const path = require('path');
const https = require('https');

class K8sMonitor {
  constructor() {
    try {
      const kc = new k8s.KubeConfig();
      
      // Try to load kubeconfig from standard location
      const kubeconfigPath = path.join(process.env.HOME || '/root', '.kube', 'config');
      const k3dConfigPath = path.join(process.env.HOME || '/root', '.kube', 'k3d-config');
      
      // Check which config file exists
      if (fs.existsSync(kubeconfigPath)) {
        kc.loadFromFile(kubeconfigPath);
      } else if (fs.existsSync(k3dConfigPath)) {
        kc.loadFromFile(k3dConfigPath);
      } else {
        kc.loadFromDefault();
      }
      
      this.api = kc.makeApiClient(k8s.CoreV1Api);
      this.appsApi = kc.makeApiClient(k8s.AppsV1Api);
      
      // Skip SSL verification for dev
      if (this.api && this.api.defaultClient) {
        this.api.defaultClient.httpsAgent = new https.Agent({
          rejectUnauthorized: false
        });
      }
    } catch (error) {
      console.error('K8s init error:', error.message);
      this.api = null;
      this.appsApi = null;
    }
  }

  async getClusterInfo() {
    try {
      if (!this.api) return { error: 'K8s not initialized' };
      
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
      if (!this.api) return [];
      
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

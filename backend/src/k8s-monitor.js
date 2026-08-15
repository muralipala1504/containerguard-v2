const k8s = require('@kubernetes/client-node');
const fs = require('fs');
const path = require('path');
const https = require('https');

class K8sMonitor {
  constructor() {
    try {
      const kc = new k8s.KubeConfig();
      
      const kubeconfigPath = path.join(process.env.HOME || '/root', '.kube', 'config');
      const k3dConfigPath = path.join(process.env.HOME || '/root', '.kube', 'k3d-config');
      
      if (fs.existsSync(kubeconfigPath)) {
        kc.loadFromFile(kubeconfigPath);
      } else if (fs.existsSync(k3dConfigPath)) {
        kc.loadFromFile(k3dConfigPath);
      } else {
        kc.loadFromDefault();
      }
      
      // Create clients with proper agent
      const agent = new https.Agent({
        rejectUnauthorized: false,
        checkServerIdentity: () => undefined
      });
      
      this.api = kc.makeApiClient(k8s.CoreV1Api);
      this.appsApi = kc.makeApiClient(k8s.AppsV1Api);
      
      // Set agent on the request object
      if (this.api && this.api.setDefaultAuthentication) {
        const opts = kc.getCurrentCluster();
        if (opts) {
          opts.skipTLSVerify = true;
        }
      }
      
      this.kc = kc;
      this.agent = agent;
      this.ready = true;
    } catch (error) {
      console.warn('⚠️ K8s init:', error.message);
      this.api = null;
      this.ready = false;
    }
  }

  async getClusterInfo() {
    try {
      if (!this.api || !this.ready) return { error: 'K8s unavailable' };
      const nodes = await this.api.listNode();
      return {
        nodes: nodes.body.items.length,
        nodeList: nodes.body.items.map(n => ({
          name: n.metadata.name,
          status: n.status.conditions.find(c => c.type === 'Ready')?.status
        }))
      };
    } catch (error) {
      return { error: error.message };
    }
  }

  async getAllPods() {
    try {
      if (!this.api || !this.ready) return [];
      const res = await this.api.listPodForAllNamespaces();
      console.log('K8s pods fetched:', res.body.items.length);
      return res.body.items.map(p => ({
        name: p.metadata.name,
        namespace: p.metadata.namespace,
        status: p.status.phase,
        containers: p.spec.containers.length,
        image: p.spec.containers[0]?.image
      }));
    } catch (error) {
      console.error('K8s pods error:', error.message);
      return [];
    }
  }
}

module.exports = K8sMonitor;

const express = require('express');
const cors = require('cors');
require('dotenv').config();
const { initDB } = require('./db');
const authRoutes = require('./auth');
const K8sMonitor = require('./k8s-monitor');
const DockerMonitor = require('./docker-monitor');

const app = express();
const PORT = process.env.BACKEND_PORT || 3001;

// Initialize monitors
let k8sMonitor = null;
let dockerMonitor = null;

try {
  k8sMonitor = new K8sMonitor();
  console.log('✅ K8s monitoring initialized');
} catch (error) {
  console.warn('⚠️ K8s monitoring unavailable:', error.message);
}

try {
  dockerMonitor = new DockerMonitor();
  console.log('✅ Docker monitoring initialized');
} catch (error) {
  console.warn('⚠️ Docker monitoring unavailable:', error.message);
}

// CORS Configuration
app.use(cors({
  origin: function (origin, callback) {
    const allowedOrigins = [
      'http://localhost:5173',
      'http://localhost:3000',
      'http://192.168.217.163:5173',
      'http://127.0.0.1:5173',
      'http://172.18.0.3:5173',
      'http://192.168.217.163:3001'
    ];
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      console.log('CORS blocked:', origin);
      callback(new Error('Not allowed by CORS'), false);
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json());

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    service: 'ContainerGuard Backend',
    version: '2.0',
    status: 'running',
    endpoints: {
      health: '/health',
      auth: {
        signup: 'POST /api/auth/signup',
        login: 'POST /api/auth/login'
      },
      monitoring: {
        all: 'GET /api/monitoring/all',
        k8s: 'GET /api/monitoring/k8s',
        docker: 'GET /api/monitoring/docker'
      }
    }
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'containerguard-backend' });
});

// Auth routes
app.use('/api/auth', authRoutes);

// Monitoring endpoints
app.get('/api/monitoring/all', async (req, res) => {
  try {
    const k8sData = k8sMonitor ? {
      clusterInfo: await k8sMonitor.getClusterInfo(),
      pods: await k8sMonitor.getAllPods()
    } : { error: 'K8s monitoring unavailable' };

    const dockerData = dockerMonitor ? {
      info: await dockerMonitor.getDockerInfo(),
      containers: await dockerMonitor.getRunningContainers()
    } : { error: 'Docker monitoring unavailable' };

    res.json({ k8s: k8sData, docker: dockerData });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/monitoring/k8s', async (req, res) => {
  try {
    if (!k8sMonitor) {
      return res.status(503).json({ error: 'K8s monitoring unavailable' });
    }
    const clusterInfo = await k8sMonitor.getClusterInfo();
    const pods = await k8sMonitor.getAllPods();
    res.json({ clusterInfo, pods });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/monitoring/docker', async (req, res) => {
  try {
    if (!dockerMonitor) {
      return res.status(503).json({ error: 'Docker monitoring unavailable' });
    }
    const info = await dockerMonitor.getDockerInfo();
    const containers = await dockerMonitor.getRunningContainers();
    res.json({ info, containers });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Initialize and start
(async () => {
  try {
    await initDB();
    app.listen(PORT, () => {
      console.log(`🚀 ContainerGuard Backend v2.0 running on port ${PORT}`);
      console.log(`✅ Ready for autonomous deployment`);
    });
  } catch (error) {
    console.error('Failed to start:', error);
    process.exit(1);
  }
})();

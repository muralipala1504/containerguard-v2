const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.BACKEND_PORT || 3001;

// CORS Configuration
app.use(cors({
  origin: function (origin, callback) {
    const allowedOrigins = [
      'http://localhost:5173',
      'http://localhost:3000',
      'http://192.168.217.163:5173',
      'http://127.0.0.1:5173'
    ];
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
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

// Placeholder monitoring endpoints
app.get('/api/monitoring/all', (req, res) => {
  res.json({ message: 'Monitoring endpoint - coming soon' });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 ContainerGuard Backend v2.0 running on port ${PORT}`);
  console.log(`✅ Ready for autonomous deployment`);
});

const Docker = require('dockerode');

class DockerMonitor {
  constructor() {
    this.docker = new Docker({ socketPath: '/var/run/docker.sock' });
  }

  async getDockerInfo() {
    try {
      const info = await this.docker.info();
      return {
        containers: info.Containers,
        runningContainers: info.ContainersRunning,
        pausedContainers: info.ContainersPaused,
        stoppedContainers: info.Containers - info.ContainersRunning - info.ContainersPaused,
        images: info.Images,
        osType: info.OSType,
        architecture: info.Architecture
      };
    } catch (error) {
      console.error('Docker info error:', error.message);
      return { error: error.message };
    }
  }

  async getRunningContainers() {
    try {
      const containers = await this.docker.listContainers({ all: true });
      return containers.map(c => ({
        id: c.Id.substring(0, 12),
        name: c.Names[0]?.replace('/', ''),
        image: c.Image,
        status: c.State,
        ports: c.Ports
      }));
    } catch (error) {
      console.error('Docker containers error:', error.message);
      return [];
    }
  }
}

module.exports = DockerMonitor;

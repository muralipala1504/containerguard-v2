import docker
from docker.errors import DockerException

class DockerMonitor:
    def __init__(self):
        try:
            self.client = docker.from_env()
            print("✅ Docker monitoring initialized")
        except Exception as e:
            print(f"⚠️ Docker init: {str(e)}")
            self.client = None

    def get_docker_info(self):
        try:
            if not self.client:
                return {"error": "Docker unavailable"}
            
            containers = self.client.containers.list(all=True)
            running = len(self.client.containers.list())
            images = self.client.images.list()
            
            return {
                "containers": len(containers),
                "runningContainers": running,
                "stoppedContainers": len(containers) - running,
                "images": len(images)
            }
        except Exception as e:
            return {"error": str(e)}

    def get_containers(self):
        try:
            if not self.client:
                return []
            
            containers = self.client.containers.list(all=True)
            return [
                {
                    "id": c.id[:12],
                    "name": c.name,
                    "image": c.image.tags[0] if c.image.tags else c.image.id[:12],
                    "status": c.status
                }
                for c in containers
            ]
        except Exception as e:
            print(f"Docker containers error: {str(e)}")
            return []

    def restart_container(self, container_id):
        """Restart a container by ID"""
        try:
            container = self.client.containers.get(container_id)
            container.restart()
            return {"success": True, "container_id": container_id, "action": "restart"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_container(self, container_id):
        """Stop a container by ID"""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            return {"success": True, "container_id": container_id, "action": "stop"}
        except Exception as e:
            return {"success": False, "error": str(e)}

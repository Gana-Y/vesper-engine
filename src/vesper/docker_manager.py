import os
import uuid
from typing import Optional

try:
    import docker
    HAS_DOCKER_LIB = True
except ImportError:
    HAS_DOCKER_LIB = False


class DockerUnavailableError(Exception):
    """Raised when Docker daemon is not active or unreachable."""
    pass


class DockerManager:
    """
    Manages secure container isolation, lifecycle, and cgroup enforcement for Vesper.
    """

    def __init__(self, time_limit: float, memory_limit: int, judger_vol_path: str):
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.judger_vol_path = os.path.abspath(judger_vol_path)
        self.image_name = "vesper-runtime-img"
        self._client = None

    @property
    def client(self):
        if not HAS_DOCKER_LIB:
            raise DockerUnavailableError("The 'docker' Python package is not installed.")
        if self._client is None:
            try:
                self._client = docker.from_env()
                self._client.ping()
            except Exception as e:
                raise DockerUnavailableError(f"Docker daemon is unreachable: {e}")
        return self._client

    def is_available(self) -> bool:
        """Checks if Docker daemon is running and accessible."""
        try:
            return self.client.ping() is True
        except Exception:
            return False

    def ensure_image(self):
        """Ensures the Vesper runtime image is available or builds it."""
        try:
            return self.client.images.get(self.image_name)
        except docker.errors.ImageNotFound:
            dockerfile_dir = os.path.join(os.path.dirname(__file__), "..", "judger_dockerfile")
            dockerfile_dir = os.path.abspath(dockerfile_dir)
            if not os.path.exists(dockerfile_dir):
                raise FileNotFoundError(f"Dockerfile directory not found at: {dockerfile_dir}")

            image, _ = self.client.images.build(
                path=dockerfile_dir,
                tag=self.image_name,
                forcerm=True
            )
            return image

    def create_sandbox_container(self, submission_id: str):
        """
        Spawns a hardened, single-tenant ephemeral sandbox container
        isolated with strict Linux cgroup and security envelopes.
        """
        image = self.ensure_image()
        container_name = f"vesper-sandbox-{submission_id[:8]}"

        container = self.client.containers.run(
            image=image.id,
            name=container_name,
            detach=True,
            tty=True,
            volumes={self.judger_vol_path: {"bind": "/workspace", "mode": "rw"}},
            mem_limit=f"{self.memory_limit}m",
            memswap_limit=f"{self.memory_limit}m",
            pids_limit=64,                      # Fork bomb immunity
            network_disabled=True,             # Air-gapped network
            read_only=True,                    # Read-only rootfs
            tmpfs={"/tmp": "rw,noexec,nosuid,size=64m"},  # Scratch space for compilers
            user="nobody",                     # Non-root unprivileged execution
            stderr=True,
            stdout=True,
            stdin_open=True
        )
        return container

    def cleanup_container(self, container):
        """Safely stops and removes an ephemeral sandbox container."""
        if container:
            try:
                container.stop(timeout=1)
            except Exception:
                pass
            try:
                container.remove(force=True)
            except Exception:
                pass

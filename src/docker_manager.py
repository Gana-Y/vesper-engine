"""
Backward-compatible proxy for DockerManager.
"""
from .vesper.docker_manager import DockerManager, DockerUnavailableError

__all__ = ["DockerManager", "DockerUnavailableError"]

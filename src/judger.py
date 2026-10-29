"""
Backward-compatible judger facade delegating to VesperEngine.
"""
import sys
import os

# Add package root to sys.path to guarantee clean imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from .vesper import VesperEngine, Verdict, ExecutionResult, run_judger, custom_run
from .vesper.docker_manager import DockerManager
from .vesper.languages import get_language_instance

__all__ = [
    "run_judger",
    "custom_run",
    "get_language_instance",
    "DockerManager",
    "VesperEngine",
    "Verdict",
    "ExecutionResult"
]

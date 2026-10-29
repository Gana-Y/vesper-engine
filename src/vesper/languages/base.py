from abc import ABC, abstractmethod
from typing import Tuple, Optional


class BaseLanguage(ABC):
    """
    Abstract interface for multi-language compilation and execution runtimes.
    """

    def __init__(self, time_limit: float, memory_limit: int, container=None):
        """
        :param time_limit: Maximum allowed runtime in seconds.
        :param memory_limit: Maximum allowed memory in megabytes (MB).
        :param container: Optional Docker container instance for containerized execution.
        """
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.container = container

    @property
    @abstractmethod
    def name(self) -> str:
        """Language identifier (e.g. 'cpp', 'py', 'java')."""
        pass

    @property
    @abstractmethod
    def extension(self) -> str:
        """Source file extension (e.g. 'cpp', 'py', 'java')."""
        pass

    @property
    @abstractmethod
    def is_compiled(self) -> bool:
        """True if the language requires a preliminary compilation phase."""
        pass

    @abstractmethod
    def compile(self, submission_id: str, submission_dir: str) -> Tuple[int, str]:
        """
        Compiles the source code if applicable.
        Returns: (exit_code, compile_output_log)
        """
        pass

    @abstractmethod
    def run(self, submission_id: str, submission_dir: str) -> Tuple[int, str, str, float, float]:
        """
        Executes the user program.
        Returns: (exit_code, stdout, stderr, execution_time_ms, memory_kb)
        """
        pass

    def cleanup(self, submission_id: str, submission_dir: str) -> Tuple[int, str]:
        """
        Cleans up runtime artifacts for the submission.
        """
        if self.container:
            cleanup_cmd = f"/bin/sh -c 'rm -rf {submission_id}'"
            exit_code, output = self.container.exec_run(cleanup_cmd)
            return exit_code, output.decode("utf-8", errors="replace")
        return 0, "Host cleanup"

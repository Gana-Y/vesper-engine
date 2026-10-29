from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Verdict(str, Enum):
    """
    Standard competitive programming & online judge verdicts.
    """
    AC = "AC"        # Accepted
    WA = "WA"        # Wrong Answer
    TLE = "TLE"      # Time Limit Exceeded
    MLE = "MLE"      # Memory Limit Exceeded
    RE = "RE"        # Runtime Error (Segfault, division by zero, uncaught exception)
    CE = "CE"        # Compilation Error
    OLE = "OLE"      # Output Limit Exceeded
    UNKNOWN = "UNKNOWN"

    def __str__(self) -> str:
        return self.value

    @property
    def description(self) -> str:
        descriptions = {
            "AC": "Accepted - Output matches expected output exactly within limits.",
            "WA": "Wrong Answer - Program completed successfully but output differs.",
            "TLE": "Time Limit Exceeded - Execution took longer than allowed threshold.",
            "MLE": "Memory Limit Exceeded - Process exceeded maximum resident memory threshold.",
            "RE": "Runtime Error - Program crashed (Signal/Exception/Segfault).",
            "CE": "Compilation Error - Compiler failed to generate an executable binary.",
            "OLE": "Output Limit Exceeded - Program produced excessive stdout/disk output.",
            "UNKNOWN": "Unknown verdict or unexpected execution state."
        }
        return descriptions.get(self.value, "Undefined verdict.")


@dataclass
class ExecutionResult:
    """
    Structured outcome of an evaluated submission.
    """
    verdict: Verdict
    execution_time_ms: float = 0.0
    memory_kb: float = 0.0
    output: str = ""
    error: str = ""
    exit_code: int = 0
    submission_id: str = ""
    compile_output: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "submission_id": self.submission_id,
            "verdict": self.verdict.value,
            "verdict_desc": self.verdict.description,
            "execution_time_ms": round(self.execution_time_ms, 2),
            "memory_kb": round(self.memory_kb, 2),
            "exit_code": self.exit_code,
            "output": self.output,
            "error": self.error,
            "compile_output": self.compile_output,
        }

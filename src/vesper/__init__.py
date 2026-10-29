"""
Vesper — Isolated, High-Performance Code Execution Engine & Sandboxed Arbiter.
"""

from .models import Verdict, ExecutionResult
from .core import VesperEngine
from .docker_manager import DockerManager

__version__ = "1.0.0"


def run_judger(
    language: str,
    time_limit: float,
    memory_limit: int,
    judger_vol_path: str = None,
    src_code: str = None,
    std_in: str = None,
    expected_out: str = None,
    src_code_path: str = None,
    std_in_path: str = None,
    expected_out_path: str = None,
    mode: str = "auto"
) -> str:
    """
    Legacy drop-in compatibility helper returning string verdict (e.g. 'AC', 'WA', 'TLE', 'RE').
    """
    engine = VesperEngine(mode=mode)
    res = engine.evaluate(
        language=language,
        time_limit=time_limit,
        memory_limit=memory_limit,
        judger_vol_path=judger_vol_path,
        src_code=src_code,
        std_in=std_in,
        expected_out=expected_out,
        src_code_path=src_code_path,
        std_in_path=std_in_path,
        expected_out_path=expected_out_path
    )
    return res.verdict.value


def custom_run(
    language: str,
    time_limit: float,
    memory_limit: int,
    judger_vol_path: str = None,
    src_code: str = None,
    std_in: str = None,
    src_code_path: str = None,
    mode: str = "auto"
):
    """
    Legacy drop-in compatibility helper for custom test runs.
    """
    engine = VesperEngine(mode=mode)
    res = engine.run_custom(
        language=language,
        time_limit=time_limit,
        memory_limit=memory_limit,
        judger_vol_path=judger_vol_path,
        src_code=src_code,
        std_in=std_in,
        src_code_path=src_code_path
    )
    if res.verdict == Verdict.AC:
        return "AC", res.output
    return res.verdict.value, res.error or res.output


__all__ = [
    "VesperEngine",
    "Verdict",
    "ExecutionResult",
    "DockerManager",
    "run_judger",
    "custom_run",
]

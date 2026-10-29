import os
import signal
import subprocess
import time
from typing import Tuple, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


MAX_OUTPUT_BYTES = 5 * 1024 * 1024  # 5 MB Output Limit


def execute_with_telemetry(
    cmd: list,
    cwd: str,
    stdin_data: str,
    timeout_sec: float,
    max_memory_mb: int
) -> Tuple[int, str, str, float, float]:
    """
    Executes a process on the local supervisor with microsecond telemetry,
    peak memory tracking, and strict timeout enforcement.

    Returns:
        (exit_code, stdout, stderr, execution_time_ms, peak_memory_kb)
    """
    start_time = time.perf_counter()
    peak_memory_kb = 0.0

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        ps_proc = None
        if HAS_PSUTIL:
            try:
                ps_proc = psutil.Process(proc.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                ps_proc = None

        # Feed input and poll
        try:
            # We enforce timeout
            stdout, stderr = proc.communicate(input=stdin_data, timeout=timeout_sec)
            elapsed_time_ms = (time.perf_counter() - start_time) * 1000.0

            if ps_proc:
                try:
                    mem_info = ps_proc.memory_info()
                    peak_memory_kb = max(peak_memory_kb, mem_info.rss / 1024.0)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Check output size limits
            if len(stdout.encode("utf-8", errors="replace")) > MAX_OUTPUT_BYTES:
                return -100, stdout[:1000] + "\n...[OUTPUT TRUNCATED - OLE]...", "Output limit exceeded (OLE)", elapsed_time_ms, peak_memory_kb

            return proc.returncode, stdout, stderr, elapsed_time_ms, peak_memory_kb

        except subprocess.TimeoutExpired:
            # Kill process tree
            try:
                if ps_proc:
                    for child in ps_proc.children(recursive=True):
                        try:
                            child.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                proc.kill()
            except Exception:
                pass

            try:
                proc.communicate(timeout=0.5)
            except Exception:
                pass

            elapsed_time_ms = timeout_sec * 1000.0
            return 124, "", f"Time limit exceeded ({timeout_sec}s)", elapsed_time_ms, peak_memory_kb

    except Exception as e:
        elapsed_time_ms = (time.perf_counter() - start_time) * 1000.0
        return 1, "", str(e), elapsed_time_ms, peak_memory_kb

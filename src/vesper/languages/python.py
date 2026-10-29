import os
import sys
import time
from typing import Tuple
from .base import BaseLanguage
from ..process_runner import execute_with_telemetry


class PythonLanguage(BaseLanguage):
    """
    Handles Python execution under strict sandboxed envelopes.
    """

    @property
    def name(self) -> str:
        return "py"

    @property
    def extension(self) -> str:
        return "py"

    @property
    def is_compiled(self) -> bool:
        return False

    def compile(self, submission_id: str, submission_dir: str) -> Tuple[int, str]:
        # Pre-execution syntax validation via py_compile
        src_path = os.path.join(submission_dir, "UserProgram.py")
        if os.path.exists(src_path):
            try:
                with open(src_path, "r", encoding="utf-8", errors="replace") as f:
                    code = f.read()
                compile(code, "UserProgram.py", "exec")
                return 0, "Syntax verified successfully"
            except SyntaxError as se:
                return 1, f"SyntaxError: {se}"
            except Exception as e:
                return 1, f"Compilation error: {e}"
        return 0, "No compilation required"

    def run(self, submission_id: str, submission_dir: str) -> Tuple[int, str, str, float, float]:
        if self.container:
            # Docker container execution (-u forces unbuffered stdout)
            run_cmd = (
                f"/bin/sh -c 'timeout {self.time_limit} python -u "
                f"{submission_id}/UserProgram.py < {submission_id}/ip.txt "
                f"> {submission_id}/actual_op.txt 2> {submission_id}/err.txt'"
            )
            start = time.perf_counter()
            exit_code, _ = self.container.exec_run(run_cmd, stderr=True, stdout=True)
            elapsed_ms = (time.perf_counter() - start) * 1000.0

            actual_op = ""
            op_path = os.path.join(submission_dir, "actual_op.txt")
            if os.path.exists(op_path):
                try:
                    with open(op_path, "r", encoding="utf-8", errors="replace") as f:
                        actual_op = f.read()
                except Exception:
                    pass

            err_op = ""
            err_path = os.path.join(submission_dir, "err.txt")
            if os.path.exists(err_path):
                try:
                    with open(err_path, "r", encoding="utf-8", errors="replace") as f:
                        err_op = f.read()
                except Exception:
                    pass

            return exit_code, actual_op, err_op, elapsed_ms, 0.0

        else:
            # Local supervisor execution
            ip_data = ""
            ip_path = os.path.join(submission_dir, "ip.txt")
            if os.path.exists(ip_path):
                with open(ip_path, "r", encoding="utf-8", errors="replace") as f:
                    ip_data = f.read()

            python_bin = sys.executable or "python"
            exit_code, stdout, stderr, elapsed_ms, mem_kb = execute_with_telemetry(
                cmd=[python_bin, "-u", "UserProgram.py"],
                cwd=submission_dir,
                stdin_data=ip_data,
                timeout_sec=self.time_limit,
                max_memory_mb=self.memory_limit
            )

            # Persist output files for consistency
            with open(os.path.join(submission_dir, "actual_op.txt"), "w", encoding="utf-8") as f:
                f.write(stdout)

            return exit_code, stdout, stderr, elapsed_ms, mem_kb

import os
import shutil
import subprocess
import time
from typing import Tuple
from .base import BaseLanguage
from ..process_runner import execute_with_telemetry


class CppLanguage(BaseLanguage):
    """
    Handles C++ compilation and execution under strict sandboxed envelopes.
    """

    @property
    def name(self) -> str:
        return "cpp"

    @property
    def extension(self) -> str:
        return "cpp"

    @property
    def is_compiled(self) -> bool:
        return True

    def compile(self, submission_id: str, submission_dir: str) -> Tuple[int, str]:
        if self.container:
            # Containerized compilation
            compile_cmd = (
                f"/bin/sh -c 'g++ -O2 -std=c++17 -Wall "
                f"-o {submission_id}/UserProgram {submission_id}/UserProgram.cpp'"
            )
            exit_code, output = self.container.exec_run(compile_cmd)
            return exit_code, output.decode("utf-8", errors="replace")
        else:
            # Local supervisor compilation
            exe_name = "UserProgram.exe" if os.name == "nt" else "UserProgram"
            src_file = os.path.join(submission_dir, "UserProgram.cpp")
            out_bin = os.path.join(submission_dir, exe_name)

            cmd = ["g++", "-O2", "-std=c++17", "-Wall", "-o", out_bin, src_file]
            try:
                res = subprocess.run(
                    cmd,
                    cwd=submission_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=15.0
                )
                output = res.stdout + ("\n" + res.stderr if res.stderr else "")
                return res.returncode, output.strip()
            except Exception as e:
                return 1, f"Host g++ execution failed: {e}"

    def run(self, submission_id: str, submission_dir: str) -> Tuple[int, str, str, float, float]:
        if self.container:
            # Run within Docker container
            run_cmd = (
                f"/bin/sh -c 'timeout {self.time_limit} "
                f"{submission_id}/UserProgram < {submission_id}/ip.txt "
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
            # Local supervisor run
            exe_name = "UserProgram.exe" if os.name == "nt" else "./UserProgram"
            bin_path = os.path.join(submission_dir, exe_name)
            ip_data = ""
            ip_path = os.path.join(submission_dir, "ip.txt")
            if os.path.exists(ip_path):
                with open(ip_path, "r", encoding="utf-8", errors="replace") as f:
                    ip_data = f.read()

            exit_code, stdout, stderr, elapsed_ms, mem_kb = execute_with_telemetry(
                cmd=[bin_path],
                cwd=submission_dir,
                stdin_data=ip_data,
                timeout_sec=self.time_limit,
                max_memory_mb=self.memory_limit
            )

            # Persist output files for consistency
            with open(os.path.join(submission_dir, "actual_op.txt"), "w", encoding="utf-8") as f:
                f.write(stdout)

            return exit_code, stdout, stderr, elapsed_ms, mem_kb

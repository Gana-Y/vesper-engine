import os
import shutil
import uuid
from typing import Optional, Union
from .models import Verdict, ExecutionResult
from .languages import get_language_instance
from .docker_manager import DockerManager, DockerUnavailableError


class VesperEngine:
    """
    Vesper — Hardened, High-Performance Code Execution Engine.
    Orchestrates compilation, sandboxing, resource telemetry, and verdict evaluation.
    """

    def __init__(self, mode: str = "auto"):
        """
        :param mode: Execution backend mode: 'auto' (prefers Docker, falls back to local supervisor),
                     'docker' (strict Docker required), or 'local' (host supervisor).
        """
        self.mode = mode.lower()

    def _resolve_backend(self, time_limit: float, memory_limit: int, vol_path: str):
        """
        Determines whether to utilize Docker or the local process supervisor.
        """
        if self.mode == "local":
            return None, None

        dm = DockerManager(time_limit=time_limit, memory_limit=memory_limit, judger_vol_path=vol_path)
        if self.mode == "docker":
            return dm, True

        # Mode == "auto"
        if dm.is_available():
            return dm, True
        return None, False

    def evaluate(
        self,
        language: str,
        time_limit: float = 1.0,
        memory_limit: int = 128,
        judger_vol_path: Optional[str] = None,
        src_code: Optional[str] = None,
        src_code_path: Optional[str] = None,
        std_in: Optional[str] = None,
        std_in_path: Optional[str] = None,
        expected_out: Optional[str] = None,
        expected_out_path: Optional[str] = None,
        cleanup_after: bool = True
    ) -> ExecutionResult:
        """
        Evaluates a submission against expected output and resource limits.
        """
        if not judger_vol_path:
            judger_vol_path = os.path.join(os.getcwd(), ".vesper_workspace")

        judger_vol_path = os.path.abspath(judger_vol_path)
        os.makedirs(judger_vol_path, exist_ok=True)

        submission_id = str(uuid.uuid4())
        submission_dir = os.path.join(judger_vol_path, submission_id)
        os.makedirs(submission_dir, exist_ok=True)

        dm, use_docker = self._resolve_backend(time_limit, memory_limit, judger_vol_path)
        container = None

        try:
            # 1. Resolve source code
            if src_code_path:
                with open(src_code_path, "r", encoding="utf-8", errors="replace") as f:
                    resolved_src = f.read()
            elif src_code is not None:
                resolved_src = src_code
            else:
                raise ValueError("Source code not provided (neither src_code nor src_code_path provided).")

            # 2. Resolve input (default to empty string if not provided)
            if std_in_path:
                with open(std_in_path, "r", encoding="utf-8", errors="replace") as f:
                    resolved_in = f.read()
            elif std_in is not None:
                resolved_in = std_in
            else:
                resolved_in = ""

            # 3. Resolve expected output
            if expected_out_path:
                with open(expected_out_path, "r", encoding="utf-8", errors="replace") as f:
                    resolved_expected = f.read()
            elif expected_out is not None:
                resolved_expected = expected_out
            else:
                raise ValueError("Expected output not provided.")

            # Initialize container if Docker backend active
            if use_docker and dm:
                container = dm.create_sandbox_container(submission_id)

            # Instantiate language handler
            lang_runner = get_language_instance(
                language=language,
                time_limit=time_limit,
                memory_limit=memory_limit,
                container=container
            )

            # Persist files in submission directory
            src_filename = f"UserProgram.{lang_runner.extension}"
            with open(os.path.join(submission_dir, src_filename), "w", encoding="utf-8") as f:
                f.write(resolved_src)

            with open(os.path.join(submission_dir, "ip.txt"), "w", encoding="utf-8") as f:
                f.write(resolved_in)

            with open(os.path.join(submission_dir, "expected_op.txt"), "w", encoding="utf-8") as f:
                f.write(resolved_expected)

            # 4. Compilation & Pre-execution Validation Phase
            compile_exit_code, compile_output = lang_runner.compile(submission_id, submission_dir)
            if compile_exit_code != 0:
                return ExecutionResult(
                    submission_id=submission_id,
                    verdict=Verdict.CE,
                    exit_code=compile_exit_code,
                    compile_output=compile_output,
                    error=compile_output
                )

            # 5. Execution Phase
            run_exit_code, actual_stdout, actual_stderr, elapsed_ms, mem_kb = lang_runner.run(
                submission_id,
                submission_dir
            )

            # 6. Verdict Resolution
            if run_exit_code == 0:
                if actual_stdout.strip() == resolved_expected.strip():
                    verdict = Verdict.AC
                else:
                    verdict = Verdict.WA
            elif run_exit_code == -100:
                verdict = Verdict.OLE
            elif run_exit_code in (124, 143):
                verdict = Verdict.TLE
            elif run_exit_code == 137:
                verdict = Verdict.MLE
            else:
                verdict = Verdict.RE

            return ExecutionResult(
                submission_id=submission_id,
                verdict=verdict,
                execution_time_ms=elapsed_ms,
                memory_kb=mem_kb,
                output=actual_stdout,
                error=actual_stderr,
                exit_code=run_exit_code
            )

        finally:
            if container and dm:
                dm.cleanup_container(container)
            if cleanup_after:
                try:
                    shutil.rmtree(submission_dir, ignore_errors=True)
                except Exception:
                    pass

    def run_custom(
        self,
        language: str,
        time_limit: float = 1.0,
        memory_limit: int = 128,
        judger_vol_path: Optional[str] = None,
        src_code: Optional[str] = None,
        src_code_path: Optional[str] = None,
        std_in: Optional[str] = None,
        cleanup_after: bool = True
    ) -> ExecutionResult:
        """
        Executes custom code without comparison against expected output.
        """
        if not judger_vol_path:
            judger_vol_path = os.path.join(os.getcwd(), ".vesper_workspace")

        judger_vol_path = os.path.abspath(judger_vol_path)
        os.makedirs(judger_vol_path, exist_ok=True)

        submission_id = str(uuid.uuid4())
        submission_dir = os.path.join(judger_vol_path, submission_id)
        os.makedirs(submission_dir, exist_ok=True)

        dm, use_docker = self._resolve_backend(time_limit, memory_limit, judger_vol_path)
        container = None

        try:
            if src_code_path:
                with open(src_code_path, "r", encoding="utf-8", errors="replace") as f:
                    resolved_src = f.read()
            elif src_code is not None:
                resolved_src = src_code
            else:
                raise ValueError("Source code not provided.")

            resolved_in = std_in if std_in is not None else ""

            if use_docker and dm:
                container = dm.create_sandbox_container(submission_id)

            lang_runner = get_language_instance(
                language=language,
                time_limit=time_limit,
                memory_limit=memory_limit,
                container=container
            )

            src_filename = f"UserProgram.{lang_runner.extension}"
            with open(os.path.join(submission_dir, src_filename), "w", encoding="utf-8") as f:
                f.write(resolved_src)

            with open(os.path.join(submission_dir, "ip.txt"), "w", encoding="utf-8") as f:
                f.write(resolved_in)

            # Compile & Validate
            compile_exit_code, compile_output = lang_runner.compile(submission_id, submission_dir)
            if compile_exit_code != 0:
                return ExecutionResult(
                    submission_id=submission_id,
                    verdict=Verdict.CE,
                    exit_code=compile_exit_code,
                    compile_output=compile_output,
                    error=compile_output
                )

            # Run
            run_exit_code, actual_stdout, actual_stderr, elapsed_ms, mem_kb = lang_runner.run(
                submission_id,
                submission_dir
            )

            if run_exit_code == 0:
                verdict = Verdict.AC
            elif run_exit_code == -100:
                verdict = Verdict.OLE
            elif run_exit_code in (124, 143):
                verdict = Verdict.TLE
            elif run_exit_code == 137:
                verdict = Verdict.MLE
            else:
                verdict = Verdict.RE

            return ExecutionResult(
                submission_id=submission_id,
                verdict=verdict,
                execution_time_ms=elapsed_ms,
                memory_kb=mem_kb,
                output=actual_stdout,
                error=actual_stderr,
                exit_code=run_exit_code
            )

        finally:
            if container and dm:
                dm.cleanup_container(container)
            if cleanup_after:
                try:
                    shutil.rmtree(submission_dir, ignore_errors=True)
                except Exception:
                    pass

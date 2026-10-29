"""
Vesper Automated Test Suite
Validates verdict arbitration, multi-language runtimes, and resource containment.
"""

import pytest
from src import VesperEngine, Verdict, run_judger, custom_run


@pytest.fixture
def engine():
    return VesperEngine(mode="auto")


def test_python_ac(engine):
    res = engine.evaluate(
        language="py",
        time_limit=1.0,
        memory_limit=128,
        src_code="print('Hello Vesper')",
        expected_out="Hello Vesper"
    )
    assert res.verdict == Verdict.AC
    assert res.exit_code == 0
    assert "Hello Vesper" in res.output


def test_python_wa(engine):
    res = engine.evaluate(
        language="py",
        time_limit=1.0,
        memory_limit=128,
        src_code="print('Hello World')",
        expected_out="Hello Vesper"
    )
    assert res.verdict == Verdict.WA
    assert res.exit_code == 0


def test_python_tle(engine):
    infinite_loop = "import time\nwhile True:\n    time.sleep(0.1)"
    res = engine.evaluate(
        language="py",
        time_limit=0.4,
        memory_limit=64,
        src_code=infinite_loop,
        expected_out="Output"
    )
    assert res.verdict == Verdict.TLE


def test_python_re(engine):
    crash_code = "print(10 / 0)"
    res = engine.evaluate(
        language="py",
        time_limit=1.0,
        memory_limit=64,
        src_code=crash_code,
        expected_out="0"
    )
    assert res.verdict == Verdict.RE
    assert "ZeroDivisionError" in res.error


def test_python_ce(engine):
    invalid_syntax = "def broken(:\n    pass"
    res = engine.evaluate(
        language="py",
        time_limit=1.0,
        memory_limit=64,
        src_code=invalid_syntax,
        expected_out="0"
    )
    assert res.verdict == Verdict.CE
    assert "SyntaxError" in (res.compile_output or res.error)


def test_empty_stdin_allowed(engine):
    no_input_code = "print('Standalone Output')"
    res = engine.evaluate(
        language="py",
        time_limit=1.0,
        memory_limit=64,
        src_code=no_input_code,
        std_in=None,
        expected_out="Standalone Output"
    )
    assert res.verdict == Verdict.AC


def test_cpp_ac(engine):
    res = engine.evaluate(
        language="cpp",
        time_limit=2.0,
        memory_limit=128,
        src_code_path=r".\tests\cpp\cpp_test.cpp",
        expected_out_path=r".\tests\cpp\cpp_op.txt"
    )
    assert res.verdict == Verdict.AC
    assert len(res.output.strip().splitlines()) == 15


def test_java_ac(engine):
    res = engine.evaluate(
        language="java",
        time_limit=3.0,
        memory_limit=128,
        src_code_path=r".\tests\java\UserProgram.java",
        std_in="15\n25",
        expected_out="Sum: 40"
    )
    assert res.verdict == Verdict.AC
    assert "Sum: 40" in res.output


def test_custom_run(engine):
    res = engine.run_custom(
        language="py",
        time_limit=1.0,
        memory_limit=64,
        src_code="print('Custom Output Test')",
        std_in=""
    )
    assert res.verdict == Verdict.AC
    assert "Custom Output Test" in res.output.strip()


def test_legacy_run_judger():
    verdict = run_judger(
        language="py",
        time_limit=1.0,
        memory_limit=128,
        src_code="print('Legacy Match')",
        expected_out="Legacy Match"
    )
    assert verdict == "AC"

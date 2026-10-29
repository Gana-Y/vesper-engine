"""
Vesper Execution Engine - Interactive Showcase
Demonstrating multi-language evaluation, sandboxed resource telemetry, and verdict arbitration.
"""

from src import VesperEngine, Verdict, run_judger

def main():
    print("=" * 65)
    print("      VESPER — ISOLATED CODE EXECUTION & BENCHMARK ARBITER     ")
    print("=" * 65)

    engine = VesperEngine(mode="auto")

    # 1. Evaluate Python Submission (Accepted)
    print("\n[TEST 1] Python Evaluation (Sum of numbers) -> Expected: AC")
    py_code = """
a = int(input())
b = int(input())
print(f"Sum is {a + b}")
"""
    result = engine.evaluate(
        language="py",
        time_limit=1.0,
        memory_limit=128,
        src_code=py_code,
        std_in="10\n25",
        expected_out="Sum is 35"
    )
    print(f"Verdict         : {result.verdict.value} ({result.verdict.description})")
    print(f"Execution Time  : {result.execution_time_ms:.2f} ms")
    print(f"Peak Memory     : {result.memory_kb:.2f} KB")
    print(f"Program Output  : {result.output.strip()}")

    # 2. Evaluate C++ Submission from File (Accepted)
    print("\n[TEST 2] C++ File Compilation & Execution -> Expected: AC")
    cpp_res = engine.evaluate(
        language="cpp",
        time_limit=2.0,
        memory_limit=128,
        src_code_path=r".\tests\cpp\cpp_test.cpp",
        expected_out_path=r".\tests\cpp\cpp_op.txt"
    )
    print(f"Verdict         : {cpp_res.verdict.value} ({cpp_res.verdict.description})")
    print(f"Execution Time  : {cpp_res.execution_time_ms:.2f} ms")
    print(f"Lines Produced  : {len(cpp_res.output.strip().splitlines())}")

    # 3. Evaluate Java Submission from File (Accepted)
    print("\n[TEST 3] Java File Compilation (javac) & Execution -> Expected: AC")
    java_res = engine.evaluate(
        language="java",
        time_limit=3.0,
        memory_limit=128,
        src_code_path=r".\tests\java\UserProgram.java",
        std_in="10\n20",
        expected_out_path=r".\tests\java\java_op.txt"
    )
    print(f"Verdict         : {java_res.verdict.value} ({java_res.verdict.description})")
    print(f"Execution Time  : {java_res.execution_time_ms:.2f} ms")
    print(f"Program Output  : {java_res.output.strip()}")

    # 4. Time Limit Exceeded (TLE) Detection
    print("\n[TEST 4] Infinite Loop Containment -> Expected: TLE")
    tle_code = """
import time
while True:
    time.sleep(0.1)
"""
    tle_res = engine.evaluate(
        language="py",
        time_limit=0.5,
        memory_limit=64,
        src_code=tle_code,
        expected_out="Never reached"
    )
    print(f"Verdict         : {tle_res.verdict.value} ({tle_res.verdict.description})")
    print(f"Elapsed Time    : {tle_res.execution_time_ms:.2f} ms")

    # 5. Runtime Error (RE) Detection
    print("\n[TEST 5] Unhandled ZeroDivision Crash -> Expected: RE")
    re_code = """
val = 42 / 0
print(val)
"""
    re_res = engine.evaluate(
        language="py",
        time_limit=1.0,
        memory_limit=64,
        src_code=re_code,
        expected_out="42"
    )
    print(f"Verdict         : {re_res.verdict.value} ({re_res.verdict.description})")
    print(f"Captured Stderr : {re_res.error.strip().splitlines()[-1] if re_res.error else 'None'}")

    # 6. Legacy API Drop-in Verification
    print("\n[TEST 6] Legacy API Compatibility (run_judger)")
    legacy_verdict = run_judger(
        language="py",
        time_limit=1.0,
        memory_limit=128,
        src_code="print('Hello Vesper')",
        expected_out="Hello Vesper"
    )
    print(f"Legacy Verdict  : {legacy_verdict}")

    print("\n" + "=" * 65)
    print("All Vesper benchmark passes completed successfully.")
    print("=" * 65)

if __name__ == "__main__":
    main()


import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

PIPELINE = [
    ("Event Log Validation", "validate_event_log.py"),
    ("Process Mining", "process_mining.py"),
    ("Bottleneck Analysis", "bottleneck_analysis.py"),
    ("Loop-back Analysis", "loopback_analysis.py"),
    ("Conformance Checking", "conformance_checking.py"),
    ("Deviation Summary", "deviation_summary.py"),
    ("Process Variant Analysis", "process_variants.py"),
    ("Process Improvement Simulation", "process_improvement_simulation.py"),
]

TEST_FILES = [
    "test_process_improvement.py",
    "test_validate_event_log.py",
]


def run_command(label, command):
    print(f"\nRunning: {label}", flush=True)

    try:
        subprocess.run(
            command,
            cwd=ROOT,
            check=True,
        )
        print(f"SUCCESS: {label}", flush=True)
        return True

    except subprocess.CalledProcessError as error:
        print(f"\nFAILED: {label}", flush=True)
        print(f"Exit code: {error.returncode}", flush=True)
        return False


def main():
    print("=" * 60)
    print("CAREFLOW - ANALYSIS PIPELINE")
    print("=" * 60, flush=True)

    # Run analysis scripts in dependency order
    for step, script in PIPELINE:
        script_path = ROOT / script

        if not script_path.is_file():
            print(f"FAILED: Script not found: {script}")
            return 1

        if not run_command(
            step,
            [sys.executable, str(script_path)],
        ):
            print("\nPipeline stopped due to an analysis error.")
            return 1

    # Verify test files exist
    for test_file in TEST_FILES:
        if not (ROOT / test_file).is_file():
            print(f"FAILED: Test file not found: {test_file}")
            return 1

    # Run automated tests after analysis
    test_command = [
        sys.executable,
        "-m",
        "unittest",
        *TEST_FILES,
        "-v",
    ]

    if not run_command("Automated Tests", test_command):
        print("\nPipeline stopped because automated tests failed.")
        return 1

    print("\n" + "=" * 60)
    print("ALL ANALYSIS STEPS AND TESTS PASSED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())

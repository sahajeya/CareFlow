import unittest
from pathlib import Path

import pandas as pd


class TestCareFlowPipelineOutputs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.project_dir = Path(__file__).parent

        cls.required_outputs = [
            "event_log_validation.csv",
            "bottleneck_analysis.csv",
            "loopback_analysis.csv",
            "conformance_results.csv",
            "conformance_status_summary.csv",
            "deviation_summary.csv",
            "deviation_details.csv",
            "process_variants.csv",
            "patient_process_variants.csv",
            "process_improvement_scenarios.csv",
        ]

    def test_all_required_output_files_exist(self):
        for filename in self.required_outputs:
            with self.subTest(filename=filename):
                file_path = self.project_dir / filename
                self.assertTrue(
                    file_path.exists(),
                    f"Missing pipeline output: {filename}"
                )

    def test_all_required_output_files_are_readable(self):
        for filename in self.required_outputs:
            with self.subTest(filename=filename):
                file_path = self.project_dir / filename
                df = pd.read_csv(file_path)
                self.assertGreater(
                    len(df),
                    0,
                    f"Output file is empty: {filename}"
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
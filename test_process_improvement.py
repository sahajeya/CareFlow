import unittest
import subprocess
import sys
from pathlib import Path

import pandas as pd


class TestProcessImprovementSimulation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Run the simulation script before testing its output
        subprocess.run(
            [sys.executable, "process_improvement_simulation.py"],
            check=True,
            capture_output=True,
            text=True
        )

        cls.output_file = Path("process_improvement_scenarios.csv")
        cls.df = pd.read_csv(cls.output_file)

    def test_output_file_exists(self):
        self.assertTrue(self.output_file.exists())

    def test_four_improvement_scenarios_generated(self):
        self.assertEqual(len(self.df), 4)

    def test_expected_reduction_percentages(self):
        self.assertEqual(
            self.df["assumed_reduction_percent"].tolist(),
            [10, 20, 30, 40]
        )

    def test_simulated_mean_calculations(self):
        expected = [33.08, 29.40, 25.72, 22.05]

        actual = self.df["simulated_mean_minutes"].tolist()

        for actual_value, expected_value in zip(actual, expected):
            self.assertAlmostEqual(
                actual_value, expected_value, places=2
            )

    def test_required_output_columns(self):
        required_columns = {
            "from_activity",
            "to_activity",
            "transition_count",
            "baseline_mean_minutes",
            "assumed_reduction_percent",
            "simulated_mean_minutes",
            "estimated_minutes_saved_per_transition",
            "estimated_total_transition_minutes_saved",
        }

        self.assertTrue(
            required_columns.issubset(set(self.df.columns))
        )

    def test_improvement_reduces_mean_time(self):
        self.assertTrue(
            (
                self.df["simulated_mean_minutes"]
                < self.df["baseline_mean_minutes"]
            ).all()
        )

    def test_estimated_savings_are_positive(self):
        self.assertTrue(
            (
                self.df["estimated_total_transition_minutes_saved"] > 0
            ).all()
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
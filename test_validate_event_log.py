
import unittest
import pandas as pd
from pathlib import Path


class TestEventLogValidation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.project_dir = Path(__file__).parent
        cls.event_log_path = cls.project_dir / "hospital_event_logs.csv"
        cls.report_path = cls.project_dir / "event_log_validation.csv"

        if not cls.event_log_path.exists():
            raise FileNotFoundError("hospital_event_logs.csv not found")

        cls.df = pd.read_csv(cls.event_log_path)

    def test_event_log_file_exists(self):
        self.assertTrue(self.event_log_path.exists())

    def test_required_columns_exist(self):
        required = {"case_id", "activity_name", "timestamp"}
        self.assertTrue(required.issubset(set(self.df.columns)))

    def test_event_log_is_not_empty(self):
        self.assertGreater(len(self.df), 0)

    def test_required_values_have_no_missing_data(self):
        required = ["case_id", "activity_name", "timestamp"]
        self.assertEqual(
            int(self.df[required].isna().sum().sum()), 0
        )

    def test_timestamps_are_valid(self):
        timestamps = pd.to_datetime(
            self.df["timestamp"], errors="coerce"
        )
        self.assertEqual(int(timestamps.isna().sum()), 0)

    def test_patient_timestamp_records_are_unique(self):
        duplicates = self.df.duplicated(
            ["case_id", "timestamp"]
        ).sum()
        self.assertEqual(int(duplicates), 0)

    def test_patients_start_with_registration(self):
        df = self.df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        first = (
            df.sort_values(["case_id", "timestamp"])
            .groupby("case_id")["activity_name"]
            .first()
        )
        self.assertTrue((first == "Patient Registration").all())

    def test_patients_end_with_discharge(self):
        df = self.df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        last = (
            df.sort_values(["case_id", "timestamp"])
            .groupby("case_id")["activity_name"]
            .last()
        )
        self.assertTrue((last == "Discharge").all())


if __name__ == "__main__":
    unittest.main()

import pandas as pd
import random
from datetime import datetime, timedelta

activities = [
    "Patient Registration",
    "Triage",
    "Doctor Consultation",
    "Lab Test",
    "Lab Result",
    "Treatment",
    "Discharge"
]

data = []

for case_id in range(1, 101):

    current_time = datetime(2026, 1, 1, 8, 0, 0)

    for activity in activities:

        # Random waiting time
        current_time += timedelta(minutes=random.randint(5, 60))

        data.append({
            "case_id": f"P{case_id:04d}",
            "activity_name": activity,
            "timestamp": current_time
        })

df = pd.DataFrame(data)

df.to_csv("hospital_event_logs.csv", index=False)

print("Hospital event log created successfully!")
print(df.head(10))
print("\nTotal events:", len(df))
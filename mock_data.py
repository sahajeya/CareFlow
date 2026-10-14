import pandas as pd
import random
from datetime import datetime, timedelta

data = []

for case_id in range(1, 101):

    current_time = datetime(2026, 1, 1, 8, 0, 0)

    # Patient Registration
    current_time += timedelta(minutes=random.randint(5, 60))
    data.append({
        "case_id": f"P{case_id:04d}",
        "activity_name": "Patient Registration",
        "timestamp": current_time
    })

    # Triage
    current_time += timedelta(minutes=random.randint(5, 60))
    data.append({
        "case_id": f"P{case_id:04d}",
        "activity_name": "Triage",
        "timestamp": current_time
    })

    # Doctor Consultation
    current_time += timedelta(minutes=random.randint(5, 60))
    data.append({
        "case_id": f"P{case_id:04d}",
        "activity_name": "Doctor Consultation",
        "timestamp": current_time
    })

    # 85% patients need laboratory testing
    if random.random() < 0.85:

        # Lab Test
        current_time += timedelta(minutes=random.randint(5, 60))
        data.append({
            "case_id": f"P{case_id:04d}",
            "activity_name": "Lab Test",
            "timestamp": current_time
        })

        # Lab Result
        current_time += timedelta(minutes=random.randint(5, 60))
        data.append({
            "case_id": f"P{case_id:04d}",
            "activity_name": "Lab Result",
            "timestamp": current_time
        })

        # 30% patients return to doctor
        if random.random() < 0.30:
            current_time += timedelta(minutes=random.randint(5, 60))
            data.append({
                "case_id": f"P{case_id:04d}",
                "activity_name": "Doctor Consultation",
                "timestamp": current_time
            })

    # Treatment
    current_time += timedelta(minutes=random.randint(5, 60))
    data.append({
        "case_id": f"P{case_id:04d}",
        "activity_name": "Treatment",
        "timestamp": current_time
    })

    # 15% patients need repeated treatment
    if random.random() < 0.15:
        current_time += timedelta(minutes=random.randint(5, 60))
        data.append({
            "case_id": f"P{case_id:04d}",
            "activity_name": "Treatment",
            "timestamp": current_time
        })

    # Discharge
    current_time += timedelta(minutes=random.randint(5, 60))
    data.append({
        "case_id": f"P{case_id:04d}",
        "activity_name": "Discharge",
        "timestamp": current_time
    })


# Create DataFrame
df = pd.DataFrame(data)

# Sort data
df = df.sort_values(["case_id", "timestamp"])

# Save CSV
df.to_csv("hospital_event_logs.csv", index=False)

print("Hospital event log created successfully!")

print("\nSample data:")
print(df.head(20))

print("\nTotal events:", len(df))

print("\nUnique activities:")
print(df["activity_name"].value_counts())
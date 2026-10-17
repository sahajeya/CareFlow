
import pandas as pd
from difflib import SequenceMatcher

# 1. Load the hospital event log
df = pd.read_csv("hospital_event_logs.csv")

# 2. Convert timestamps and arrange events in order
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["case_id", "activity_name", "timestamp"])
df = df.sort_values(["case_id", "timestamp"])

# 3. Define the ideal patient pathway
ideal_pathway = [
    "Patient Registration",
    "Triage",
    "Doctor Consultation",
    "Lab Test",
    "Lab Result",
    "Treatment",
    "Discharge",
]

# 4. Compare every patient's actual pathway with the ideal pathway
results = []

for patient_id, group in df.groupby("case_id"):
    actual_pathway = group["activity_name"].tolist()

    if actual_pathway == ideal_pathway:
        status = "Conforming"
        deviation_details = "No deviation"
    else:
        status = "Deviated"
        differences = []

        # Compare expected activities with actual activities
        matcher = SequenceMatcher(
            a=ideal_pathway,
            b=actual_pathway,
            autojunk=False
        )

        for operation, i1, i2, j1, j2 in matcher.get_opcodes():
            if operation == "equal":
                continue

            expected = ideal_pathway[i1:i2]
            actual = actual_pathway[j1:j2]

            if operation == "delete":
                differences.append(
                    "Missing expected activity: " + ", ".join(expected)
                )

            elif operation == "insert":
                differences.append(
                    "Extra/repeated activity: " + ", ".join(actual)
                )

            elif operation == "replace":
                differences.append(
                    "Expected [" + ", ".join(expected)
                    + "] but found [" + ", ".join(actual) + "]"
                )

        deviation_details = "; ".join(differences)

    results.append({
        "case_id": patient_id,
        "actual_pathway": " -> ".join(actual_pathway),
        "ideal_pathway": " -> ".join(ideal_pathway),
        "status": status,
        "deviation_details": deviation_details,
        "number_of_events": len(actual_pathway),
    })

# 5. Save patient-level conformance results
result_df = pd.DataFrame(results)
result_df.to_csv("conformance_results.csv", index=False)

# 6. Display the summary
print("\nCARE FLOW - CONFORMANCE CHECKING")
print("=" * 45)
print("Total patients:", len(result_df))

print("\nConformance summary:")
print(result_df["status"].value_counts().to_string())

conforming = (result_df["status"] == "Conforming").sum()
total = len(result_df)

conformance_rate = (conforming / total * 100) if total else 0

print(f"\nConformance rate: {conformance_rate:.2f}%")
print(f"Deviation rate: {100 - conformance_rate:.2f}%")

print("\nSample patient results:")
print(
    result_df[
        ["case_id", "status", "deviation_details"]
    ].head(10).to_string(index=False)
)

print("\nReport saved: conformance_results.csv")

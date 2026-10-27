
from pathlib import Path

import pandas as pd

# Define input and output paths
data_dir = Path("frontend") / "public"
input_csv = data_dir / "hospital_event_logs.csv"
output_csv = data_dir / "bottleneck_analysis.csv"

# Load hospital event log
if not input_csv.exists():
    raise FileNotFoundError(
        f"Hospital event log not found: {input_csv}"
    )

df = pd.read_csv(input_csv)

# Validate required columns
required_columns = [
    "case_id",
    "activity_name",
    "timestamp"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

if df.empty:
    raise ValueError("Hospital event log is empty.")

# Validate required data
if df[required_columns].isnull().any().any():
    raise ValueError(
        "Required columns contain missing values."
    )

# Convert timestamp and validate its format
df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

if df["timestamp"].isnull().any():
    invalid_count = df["timestamp"].isnull().sum()
    raise ValueError(
        f"Found {invalid_count} invalid timestamps."
    )

# Sort by patient and time
df = df.sort_values(
    ["case_id", "timestamp"]
).reset_index(drop=True)

# Get next activity and next timestamp
df["next_activity"] = (
    df.groupby("case_id")["activity_name"].shift(-1)
)

df["next_timestamp"] = (
    df.groupby("case_id")["timestamp"].shift(-1)
)

# Calculate transition time in minutes
df["transition_minutes"] = (
    df["next_timestamp"] - df["timestamp"]
).dt.total_seconds() / 60

# Remove last activity of each patient
df = df.dropna(
    subset=["next_activity", "transition_minutes"]
)

# Group transitions and calculate statistics
bottleneck = (
    df.groupby(
        ["activity_name", "next_activity"]
    )["transition_minutes"]
    .agg(["count", "mean", "median", "max"])
    .reset_index()
)

# Round values
bottleneck[["mean", "median", "max"]] = (
    bottleneck[["mean", "median", "max"]].round(2)
)

# Sort by average transition time
bottleneck = bottleneck.sort_values(
    "mean",
    ascending=False
)

print("\n" + "=" * 60)
print("CARE FLOW - TRANSITION TIME BOTTLENECK ANALYSIS")
print("=" * 60)

print(bottleneck.to_string(index=False))

# Save result for the dashboard
bottleneck.to_csv(output_csv, index=False)

print("\nBottleneck analysis completed successfully!")
print(f"Saved as: {output_csv}")

print(f"Transitions analysed: {len(df)}")
print(f"Unique activity transitions: {len(bottleneck)}")

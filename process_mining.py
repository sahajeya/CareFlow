import pandas as pd
import pm4py

# Load hospital event log
df = pd.read_csv("hospital_event_logs.csv")

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Sort events by patient and time
df = df.sort_values(["case_id", "timestamp"])

print("Event log loaded successfully!")
print(df.head(10))

# Convert DataFrame to PM4Py event log
event_log = pm4py.format_dataframe(
    df,
    case_id="case_id",
    activity_key="activity_name",
    timestamp_key="timestamp"
)

print("\nPM4Py event log created successfully!")
print("Total events:", len(df))

# Discover process tree
process_tree = pm4py.discover_process_tree_inductive(event_log)

print("\nProcess tree discovered successfully!")

# Save process tree as PNG
pm4py.save_vis_process_tree(
    process_tree,
    "process_tree.png"
)

print("\nProcess tree saved successfully!")
print("Saved as: process_tree.png")
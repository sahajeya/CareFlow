import pandas as pd
import pm4py
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.process_tree import visualizer as pt_visualizer

# Load hospital event log
df = pd.read_csv("hospital_event_logs.csv")

print("Total events:", len(df))

# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Rename columns for PM4Py
df = df.rename(columns={
    "case_id": "case:concept:name",
    "activity_name": "concept:name",
    "timestamp": "time:timestamp"
})

# Convert to PM4Py event log
event_log = log_converter.apply(
    df,
    variant=log_converter.Variants.TO_EVENT_LOG
)

# Discover process tree
process_tree = inductive_miner.apply(event_log)

print("Process tree discovered successfully!")

# Save process tree visualization
gviz = pt_visualizer.apply(process_tree)
pt_visualizer.save(gviz, "process_tree.png")

print("Process tree saved as process_tree.png")
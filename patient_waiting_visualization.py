import pandas as pd
import matplotlib.pyplot as plt

# Load patient pathway analysis data
df = pd.read_csv("patient_waiting_analysis.csv")

# Select first 10 patients
df = df.head(10)

# Create bar chart
plt.figure(figsize=(12, 6))

plt.bar(
    df["case_id"],
    df["total_pathway_minutes"],
    color="teal"
)

# Add chart details
plt.title("Patient Pathway Time Analysis")
plt.xlabel("Patient ID")
plt.ylabel("Total Pathway Time (Minutes)")

plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.5)

plt.tight_layout()

# Save chart
plt.savefig("patient_waiting_chart.png", dpi=300)

print("Patient pathway visualization completed successfully!")
print("Saved: patient_waiting_chart.png")

plt.show()
# CareFlow: Clinical Pathway Process Mining

**Infotact Group Project**

## 1. Project Overview

CareFlow is a healthcare process analytics project that uses Process Mining to analyze simulated hospital event logs. It identifies patient journey patterns, process bottlenecks, repeated activities, and deviations from an expected clinical pathway.

The project also simulates hypothetical process improvement scenarios to estimate how reducing elapsed time between activities could affect overall transition time.

## 2. Problem Statement

Average hospital journey times alone may not reveal which activities or transitions contribute to delays or why patient pathways differ. CareFlow analyzes event-level data to identify these patterns and support evidence-based investigation of potential process improvements.

## 3. Objectives

- Validate hospital event log quality.
- Discover the hospital process model using PM4Py.
- Identify transitions with high elapsed times.
- Analyze repeated activities and loop-back patterns.
- Compare observed pathways with an expected pathway.
- Group patients by process variants.
- Simulate hypothetical process improvement scenarios.
- Generate CSV reports for further analysis.

## 4. Technologies Used

- Python
- Pandas
- PM4Py
- CSV-based event logs
- Python `unittest`
- dbt and Google BigQuery for the data transformation workflow

## 5. Project Modules

| Module | Purpose |
|---|---|
| `validate_event_log.py` | Checks event log quality |
| `process_mining.py` | Discovers and exports a process tree |
| `bottleneck_analysis.py` | Calculates elapsed-time statistics for activity transitions |
| `loopback_analysis.py` | Identifies repeated or backward activity transitions |
| `conformance_checking.py` | Compares observed pathways with an expected pathway |
| `deviation_summary.py` | Summarizes pathway deviations |
| `process_variants.py` | Identifies unique patient journey patterns |
| `process_improvement_simulation.py` | Estimates hypothetical improvement scenarios |
| `test_process_improvement.py` | Runs automated tests for the simulation |
| `mock_data.py` | Supports mock event data generation |

## 6. Event Log

The current simulated dataset contains 723 events for 100 patients. The event log includes case identifiers, activity names, and timestamps.

The expected pathway is:

Patient Registration → Triage → Doctor Consultation → Lab Test → Lab Result → Treatment → Discharge

## 7. Setup

Create and activate a Python virtual environment, then install the required dependencies used by the project scripts.

```bash
python -m venv venv
venv\Scripts\activate
pip install pandas pm4py
```

Additional dependencies may be required for the dbt/BigQuery workflow. Configure Google Cloud authentication and the dbt profile separately before running that workflow.

## 8. Running the Analysis

Run these commands from the project directory:

```bash
python validate_event_log.py
python process_mining.py
python bottleneck_analysis.py
python loopback_analysis.py
python conformance_checking.py
python deviation_summary.py
python process_variants.py
python process_improvement_simulation.py
```

Run the automated tests with:

```bash
python -m unittest test_process_improvement.py -v
```

## 9. Current Results

- 100 simulated patient journeys and 723 events.
- 47 patients followed the expected pathway; 53 were classified as deviating from it by the current conformance script.
- Five distinct process variants were identified.
- The Lab Result → Treatment transition had a mean recorded elapsed time of 36.75 minutes across 56 transitions.
- Seven automated process-improvement simulation tests passed.

## 10. Output Reports

The scripts generate CSV reports for event validation, bottleneck analysis, loop-back patterns, conformance results, deviation summaries, process variants, and improvement scenarios. The process mining module also generates `process_tree.png`.

## 11. Limitations

The dataset is simulated and does not represent real patient records. Recorded elapsed time between activities should not automatically be interpreted as actual waiting time. Simulated improvement scenarios are estimates, not measured real-world outcomes. Pathway deviations indicate differences from the expected sequence and do not by themselves establish clinical errors.

## 12. Future Work

- Build an interactive dashboard for exploring bottlenecks and process variants.
- Add further data-quality and integration tests.
- Compare process models and investigate deviations in more detail.
- Evaluate improvement scenarios using validated operational data when available.
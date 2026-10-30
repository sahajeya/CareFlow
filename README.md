# CareFlow – Clinical Pathway Process Mining

## 1. Project Overview
CareFlow is a healthcare process analytics project that analyses hospital patient journeys using process mining and data analysis techniques. It helps identify delays and bottlenecks in patient treatment pathways.

## 2. Problem Statement
Hospitals may experience delays during patient registration, triage, doctor consultation, laboratory testing, treatment, and discharge. Average waiting-time reports alone may not clearly explain where delays occur in the patient journey.

## 3. Objectives
- Analyse hospital patient journey event logs.
- Calculate patient pathway durations.
- Identify bottlenecks between consecutive activities.
- Compare waiting and pathway durations.
- Visualise key findings through a Power BI dashboard.

## 4. Tools and Technologies
- Python – Data processing and analysis
- Pandas – Data manipulation
- PM4Py – Process mining
- Power BI – Dashboard and visualisation
- CSV – Event logs and analysis reports
- Git and GitHub – Version control and collaboration

## 5. Dataset Description
The project uses a hospital event log dataset containing patient case IDs, activity names, and timestamps.

The dataset represents activities such as:
- Patient Registration
- Triage
- Doctor Consultation
- Lab Test
- Lab Result
- Treatment
- Discharge

The dataset is used to analyse the sequence and duration of patient activities.

## 6. Process Mining
Process mining is used to explore patient activity sequences and understand how patients move through the hospital workflow.

PM4Py is used to discover process patterns from the event log data.

## 7. Bottleneck Analysis
Python scripts analyse the time between consecutive hospital activities. The results help identify transitions associated with longer durations.

The generated reports include average and maximum transition durations and bottleneck rankings.

## 8. Patient Pathway Analysis
Patient pathway analysis calculates the total duration between the first and last recorded activities for each patient case. These results help compare pathway durations across patients.

## 9. Power BI Dashboard
The dashboard presents key project findings through:
- Average Patient Pathway Time
- Total Patients Analysed
- Longest Patient Pathway
- Bottleneck Ranking by Average Duration
- Top 10 Patients by Pathway Duration
- Average Activity Transition Duration

## 10. Expected Outcomes
- Better visibility into hospital patient pathways.
- Identification of activities associated with longer durations.
- Clear visual summaries of patient pathway and bottleneck analysis.
- Data-supported insights for further hospital workflow investigation.

## 11. Project Status
The event log analysis, bottleneck reports, patient pathway analysis, and Power BI dashboard have been developed as part of the project.

## 12. Team
Infotact Group Project

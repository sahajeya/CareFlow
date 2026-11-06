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
- Flask – Web application and API
- Pandas – Data manipulation
- PM4Py – Process mining
- Matplotlib – Data visualisation
- Power BI – Dashboard and reporting
- SQLite – Database
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

## 10. Flask Application and API Endpoints
The Flask application provides a web interface and API endpoints for accessing CareFlow analysis results.

| Endpoint | Description |
|---|---|
| / | Displays the dashboard |
| /api/status | Returns application status |
| /api/summary | Returns summary information |
| /api/patients | Returns patient records |
| /api/patients/<case_id> | Returns details for a patient case |
| /api/bottlenecks | Returns bottleneck analysis |
| /api/pathway-analysis | Returns patient pathway analysis |
| /api/activity-waiting | Returns activity waiting-time analysis |

## 11. Installation and Setup
1. Install Python on your system.
2. Clone the CareFlow repository.
3. Open the project folder in the terminal.
4. Create a virtual environment:
   python -m venv venv
5. Activate the virtual environment:
   .\venv\Scripts\Activate.ps1
6. Install dependencies:
   pip install -r requirements.txt

## 12. How to Run the Application
Run the Flask application:
   python app.py

Open this address in your browser:
   http://127.0.0.1:5000

## 13. Testing
The project includes API endpoint validation and system testing.
- Eight application endpoints were tested.
- Three invalid-route tests returned the expected 404 responses.
- Testing results are documented in DAY3_TESTING_REPORT.md and DAY4_TESTING_REPORT.md.

## 14. Expected Outcomes
- Better visibility into hospital patient pathways.
- Identification of activities associated with longer durations.
- Clear visual summaries of patient pathway and bottleneck analysis.
- Data-supported insights for further hospital workflow investigation.

## 15. Project Status
The event log analysis, bottleneck reports, patient pathway analysis, Flask application, API validation, and Power BI dashboard have been developed as part of the project.

## 16. Team
Infotact Group Project


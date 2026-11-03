# CareFlow
### Infotact Group Project

**Healthcare Process Intelligence – Clinical Pathway Process Mining**

## 📌 About the Project

CareFlow is a healthcare process intelligence project designed to analyze hospital workflows using process mining techniques. It helps identify bottlenecks, monitor patient pathways, evaluate process conformance, and understand delays in hospital activities.

The project provides an interactive analytics dashboard to visualize hospital process data and support better workflow analysis.

## 🎯 Project Objectives

- Analyze patient journeys through different hospital activities.
- Identify bottlenecks and delays in clinical workflows.
- Monitor patient pathway performance.
- Evaluate process conformance against the discovered process model.
- Visualize healthcare process insights through an interactive dashboard.

## ✨ Key Features

- **Patient Flow Analysis:** Track patient activities and waiting times between consecutive activities.
- **Bottleneck Analysis:** Identify time-consuming transitions in hospital workflows.
- **Conformance Analysis:** Evaluate whether patient pathways follow the discovered process model.
- **Analytics Dashboard:** Display important healthcare process metrics and visualizations.
- **Case-wise Analysis:** View individual patient case details and process performance.

## 📊 Dashboard Modules

1. **Overview** – Displays total patients, conformance rate, average trace fitness, and high-priority bottleneck count.
2. **Patient Flow** – Displays patient activity timelines and waiting times between activities.
3. **Bottleneck Analysis** – Identifies process transitions with high, medium, and low priority delays.
4. **Conformance** – Displays conformant and non-conformant cases with trace fitness scores.

## 🔄 Hospital Workflow

The analyzed hospital workflow includes the following activities:

1. Patient Registration
2. Triage
3. Doctor Consultation
4. Lab Test
5. Lab Result
6. Treatment
7. Discharge

## 🛠️ Technologies Used

**Frontend**
- React.js
- Vite
- JavaScript
- CSS

**Data Analysis & Process Mining**
- Python
- Pandas
- PM4Py

**Data Visualization**
- Recharts
- PapaParse
- Lucide React

**Data Platform**
- Google BigQuery
- dbt

## 📁 Project Structure

```text
CareFlow/
│
├── frontend/
│   ├── public/
│   │   ├── hospital_event_logs.csv
│   │   ├── bottleneck_analysis.csv
│   │   └── conformance_results.csv
│   │
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── ...
│   │
│   └── package.json
│
├── bottleneck_analysis.py
├── process_mining.py
└── README.md
```

*Note: Update the structure if your actual repository contains different filenames or folders.*

## ⚙️ Installation and Setup

### Prerequisites

- Node.js and npm
- Python 3
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/sahajeya/CareFlow.git
```

### Step 2: Navigate to the Frontend

```bash
cd CareFlow/frontend
```

### Step 3: Install Dependencies

```bash
npm install
```

### Step 4: Run the Application

```bash
npm run dev
```

### Step 5: Open in Browser

Open the local URL displayed in the terminal, usually:

```text
http://localhost:5173/
```

## 📈 Dataset and Analysis

The project uses hospital event log data containing patient case IDs, activity names, and timestamps.

The current analysis includes:
- 100 patient cases
- 700 hospital activity events
- Bottleneck transition analysis
- Process conformance evaluation
- Trace fitness measurement

The displayed results reflect the supplied process-mining dataset and model. They are intended for workflow analysis and are not clinical diagnoses.

## 👥 Project Details

**Project Name:** CareFlow  
**Organization:** Infotact  
**Project Type:** Group Project  
**Domain:** Healthcare Analytics and Process Mining

## 🚀 Future Enhancements

- Integration with real-time hospital data.
- Advanced process performance monitoring.
- Improved clinical workflow analytics.
- More detailed patient journey visualizations.
- Enhanced reporting and insights.

## 📌 Conclusion

CareFlow aims to improve the understanding of hospital workflows through process mining and interactive analytics. By identifying bottlenecks, analyzing patient pathways, and evaluating process conformance, the project provides useful insights into healthcare process performance.

---

**CareFlow – Healthcare Process Intelligence**
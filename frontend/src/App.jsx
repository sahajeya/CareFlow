import React, { useState, useEffect } from "react";

import Papa from "papaparse";

import {

  Activity,

  LayoutDashboard,

  GitBranch,

  ChartNoAxesColumn,
  Grid3X3,

  ClipboardCheck,

  Menu,

  Bell,

  Search,

  Users,

  Clock3,

  CircleCheck,

  CircleAlert,

  ArrowUpRight,

  HeartPulse,

  Download,

} from "lucide-react";



import {

  ResponsiveContainer,

  BarChart,

  Bar,

  XAxis,

  YAxis,

  CartesianGrid,

  Tooltip,

  PieChart,

  Pie,

  Cell,

  Legend,

} from "recharts";



import "./App.css";



const pages = [
  { name: "Overview", icon: LayoutDashboard },
  { name: "Patient Flow", icon: GitBranch },
  { name: "Process Map", icon: GitBranch },
  { name: "Waiting Time Heatmap", icon: Grid3X3 },
  { name: "Bottleneck Analysis", icon: ChartNoAxesColumn },
  { name: "Process Deviation Details", icon: ClipboardCheck },
  { name: "Conformance", icon: ClipboardCheck },
];



function isConformantValue(value) {

  return (

    value === true ||

    value === 1 ||

    value === "1" ||

    value === "True" ||

    value === "true"

  );

}



function App() {

  const [activePage, setActivePage] = useState("Overview");

  const [menuOpen, setMenuOpen] = useState(true);

  const [bottlenecks, setBottlenecks] = useState([]);

  const [conformance, setConformance] = useState([]);

  const [eventLogs, setEventLogs] = useState([]);

  const [selectedCase, setSelectedCase] = useState("P0001");

  const [globalPatientFilter, setGlobalPatientFilter] = useState("All");

  const [loading, setLoading] = useState(true);

  const [dataError, setDataError] = useState("");

  const [activityFilter, setActivityFilter] = useState("All");

  const [dateFrom, setDateFrom] = useState("");

  const [dateTo, setDateTo] = useState("");



  useEffect(() => {

    async function loadCsvData() {

      try {

        const [

          bottleneckResponse,

          conformanceResponse,

          eventLogsResponse,

        ] = await Promise.all([

          fetch("/bottleneck_analysis.csv"),

          fetch("/conformance_results.csv"),

          fetch("/hospital_event_logs.csv"),

        ]);



        if (

          !bottleneckResponse.ok ||

          !conformanceResponse.ok ||

          !eventLogsResponse.ok

        ) {

          throw new Error("CSV files could not be loaded.");

        }



        const bottleneckText = await bottleneckResponse.text();

        const conformanceText = await conformanceResponse.text();

        const eventLogsText = await eventLogsResponse.text();



        const bottleneckResult = Papa.parse(bottleneckText, {

          header: true,

          skipEmptyLines: true,

          dynamicTyping: true,

        });



        const conformanceResult = Papa.parse(conformanceText, {

          header: true,

          skipEmptyLines: true,

          dynamicTyping: true,

        });



        const eventLogsResult = Papa.parse(eventLogsText, {

          header: true,

          skipEmptyLines: true,

          dynamicTyping: true,

        });



        const parsedBottlenecks = bottleneckResult.data.map((row) => ({

          ...row,

          activity: `${row.activity_name} → ${row.next_activity}`,

          minutes: Number(row.mean) || 0,

        }));



        setBottlenecks(parsedBottlenecks);

        setConformance(conformanceResult.data);

        setEventLogs(eventLogsResult.data);

      } catch (error) {

        console.error("CSV loading error:", error);

        setDataError(error.message);

      } finally {

        setLoading(false);

      }

    }



    loadCsvData();

  }, []);



  // Apply the global patient, date, and activity filters first.
  const globallyFilteredEvents = eventLogs.filter((row) => {
    const eventDate = new Date(row.timestamp);
    const fromDate = dateFrom ? new Date(`${dateFrom}T00:00:00`) : null;
    const toDate = dateTo ? new Date(`${dateTo}T23:59:59`) : null;

    if (globalPatientFilter !== "All" && row.case_id !== globalPatientFilter) {
      return false;
    }
    if (fromDate && eventDate < fromDate) return false;
    if (toDate && eventDate > toDate) return false;
    if (activityFilter !== "All" && row.activity_name !== activityFilter) {
      return false;
    }
    return true;
  });

  const globallyFilteredCaseIds = new Set(
    globallyFilteredEvents.map((row) => row.case_id)
  );

  const globallyFilteredConformance = conformance.filter((row) =>
    globallyFilteredCaseIds.has(row.case_id)
  );

  // Show only cases marked non-conformant by the existing conformance output.
  const processDeviations = globallyFilteredConformance.filter(
    (row) => !isConformantValue(row.is_conformant)
  );

  // Recalculate transition averages from date/patient-filtered records.
  // Keep the full activity sequence so selecting one activity does not
  // accidentally create artificial transitions between non-adjacent events.
  const bottleneckSourceEvents = eventLogs.filter((row) => {
    const eventDate = new Date(row.timestamp);
    const fromDate = dateFrom ? new Date(`${dateFrom}T00:00:00`) : null;
    const toDate = dateTo ? new Date(`${dateTo}T23:59:59`) : null;

    if (globalPatientFilter !== "All" && row.case_id !== globalPatientFilter) return false;
    if (fromDate && eventDate < fromDate) return false;
    if (toDate && eventDate > toDate) return false;
    return true;
  });

  const filteredBottlenecks = (() => {
    const groupedCases = {};

    bottleneckSourceEvents.forEach((row) => {
      if (!groupedCases[row.case_id]) groupedCases[row.case_id] = [];
      groupedCases[row.case_id].push(row);
    });

    const transitions = {};

    Object.values(groupedCases).forEach((events) => {
      const sortedEvents = [...events].sort(
        (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
      );

      for (let i = 0; i < sortedEvents.length - 1; i++) {
        const current = sortedEvents[i];
        const next = sortedEvents[i + 1];
        const minutes =
          (new Date(next.timestamp) - new Date(current.timestamp)) / 60000;

        if (!Number.isFinite(minutes) || minutes < 0) continue;

        if (
          activityFilter !== "All" &&
          current.activity_name !== activityFilter &&
          next.activity_name !== activityFilter
        ) {
          continue;
        }

        const key = `${current.activity_name} → ${next.activity_name}`;
        if (!transitions[key]) {
          transitions[key] = {
            activity: key,
            totalMinutes: 0,
            count: 0,
          };
        }
        transitions[key].totalMinutes += minutes;
        transitions[key].count += 1;
      }
    });

    return Object.values(transitions).map((item) => ({
      ...item,
      minutes: item.count ? item.totalMinutes / item.count : 0,
    }));
  })();

  // Overview metrics use the globally filtered records.
  const totalPatients = new Set(
    globallyFilteredEvents.map((row) => row.case_id).filter(Boolean)
  ).size;

  const totalCases = globallyFilteredConformance.length;

  const conformantCases = globallyFilteredConformance.filter((row) =>
    isConformantValue(row.is_conformant)
  ).length;

  const nonConformantCases = totalCases - conformantCases;

  const averageFitness = totalCases
    ? globallyFilteredConformance.reduce(
        (sum, row) => sum + (Number(row.trace_fitness) || 0),
        0
      ) / totalCases
    : 0;

  const conformantPercent = totalCases
    ? (conformantCases / totalCases) * 100
    : 0;

  const nonConformantPercent = totalCases
    ? (nonConformantCases / totalCases) * 100
    : 0;

  const topBottleneck = [...filteredBottlenecks].sort(
    (a, b) => b.minutes - a.minutes
  )[0];

  // High priority bottlenecks: 35 minutes or above.
  const highPriorityBottlenecks = filteredBottlenecks.filter(
    (item) => Number.isFinite(item.minutes) && item.minutes >= 35
  );

  const bottleneckCount = highPriorityBottlenecks.length;

  const patientCases = [
    ...new Set(globallyFilteredEvents.map((row) => row.case_id)),
  ]
    .filter(Boolean)
    .sort();

  const selectedEvents = globallyFilteredEvents

  .filter((row) =>

    row.case_id ===

    (globalPatientFilter === "All"

      ? selectedCase

      : globalPatientFilter)

  )

    .filter((row) => {

       const eventDate = new Date(row.timestamp);

       const fromDate = dateFrom ? new Date(`${dateFrom}T00:00:00`) : null;

       const toDate = dateTo ? new Date(`${dateTo}T23:59:59`) : null;



       if (fromDate && eventDate < fromDate) return false;

       if (toDate && eventDate > toDate) return false;



       if (

         activityFilter !== "All" &&

         row.activity_name !== activityFilter

      ) {

        return false;

        }



        return true;

   })

   .sort(

     (a, b) => new Date(a.timestamp) - new Date(b.timestamp)

    )

    .map((row, index, events) => {

     if (index === 0) {

      return { ...row, waitingMinutes: null };

    }



    const previousTime = new Date(events[index - 1].timestamp);

    const currentTime = new Date(row.timestamp);



    const difference =

      (currentTime - previousTime) / (1000 * 60);



    return {

      ...row,

      waitingMinutes: Number.isFinite(difference)

        ? Math.max(0, Math.round(difference))

        : null,

    };

  });



      // Download filtered patient events as CSV*

  const downloadPatientCSV = () => {

    if (selectedEvents.length === 0) {

      alert("No patient events available to download.");

      return;

    }



    const csvData = selectedEvents.map((row) => ({

      Case_ID: row.case_id,

      Activity: row.activity_name,

      Timestamp: row.timestamp,

      Waiting_Minutes: row.waitingMinutes ?? "",

    }));



    const csv = Papa.unparse(csvData);

    const blob = new Blob([csv], {

      type: "text/csv;charset=utf-8;",

    });



    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");



    link.href = url;

    link.download = `${selectedCase}\_Patient_Flow.csv`;

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    URL.revokeObjectURL(url);

  };



  // Print the filtered patient journey and save it as PDF*

  const downloadPatientPDF = () => {

    if (selectedEvents.length === 0) {

      alert("No patient events available to export.");

      return;

    }



    window.print();

  };



    // Download bottleneck analysis as CSV*

  const downloadBottleneckCSV = () => {

    if (filteredBottlenecks.length === 0) {

      alert("No bottleneck data available to download.");

      return;

    }



    const csvData = filteredBottlenecks.map((item) => ({

      Activity: item.activity_name,

      Next_Activity: item.next_activity,

      Transition: item.activity,

      Average_Minutes: item.minutes.toFixed(2),

      Priority:

        item.minutes >= 35

          ? "High"

          : item.minutes >= 30

            ? "Medium"

            : "Low",

    }));



    const csv = Papa.unparse(csvData);

    const blob = new Blob([csv], {

      type: "text/csv;charset=utf-8;",

    });



    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");



    link.href = url;

    link.download = "CareFlow_Bottleneck_Analysis.csv";



    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    URL.revokeObjectURL(url);

  };



    // Download conformance results as CSV*

  const downloadConformanceCSV = () => {

    if (conformance.length === 0) {

      alert("No conformance data available to download.");

      return;

    }



    const csvData = globallyFilteredConformance.map((row) => ({

      Case_ID: row.case_id,

      Trace_Fitness: Number(row.trace_fitness).toFixed(2),

      Conformance_Status: isConformantValue(row.is_conformant)

        ? "Conformant"

        : "Non-conformant",

    }));



    const csv = Papa.unparse(csvData);

    const blob = new Blob([csv], {

      type: "text/csv;charset=utf-8;",

    });



    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");



    link.href = url;

    link.download = "CareFlow_Conformance_Results.csv";



    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    URL.revokeObjectURL(url);

  };



  // Print conformance report and save as PDF*

  const downloadConformancePDF = () => {

    if (conformance.length === 0) {

      alert("No conformance data available to export.");

      return;

    }



    window.print();

  };



  return (

    <div className="app-shell">

      <aside className={`sidebar ${menuOpen ? "" : "collapsed"}`}>

        <div className="brand">

          <div className="brand-icon">

            <HeartPulse size={25} />

          </div>



          {menuOpen && (

            <div>

              <h2>CareFlow</h2>

              <span>CLINICAL ANALYTICS</span>

            </div>

          )}

        </div>



        <p className="nav-label">

          {menuOpen ? "WORKSPACE" : ""}

        </p>



        <nav>

          {pages.map(({ name, icon: Icon }) => (

            <button

              key={name}

              className={`nav-item ${

                activePage === name ? "active" : ""

              }`}

              onClick={() => setActivePage(name)}

              title={name}

            >

              <Icon size={19} />

              {menuOpen && <span>{name}</span>}

            </button>

          ))}

        </nav>



        <div className="sidebar-bottom">

          <Activity size={20} />

          {menuOpen && <span>Clinical Process Mining</span>}

        </div>

      </aside>



      <main className="main-content">

        <header className="topbar">

          <button

            className="icon-button"

            onClick={() => setMenuOpen(!menuOpen)}

          >

            <Menu size={21} />

          </button>



          <div className="breadcrumb">

            Workspace / <b>{activePage}</b>

          </div>



          <div className="top-actions">

            <div className="search-box">

              <Search size={16} />

              <input placeholder="Search dashboard..." />

            </div>



            <button

              className="icon-button"

              title="Notifications"

            >

              <Bell size={19} />

            </button>



            <div className="avatar">CF</div>

          </div>

        </header>



        <section className="page-content">

          <div className="welcome-row">

            <div>

              <span className="eyebrow">

                HEALTHCARE PROCESS INTELLIGENCE

              </span>



              <h1>

                {activePage === "Overview"

                  ? "Clinical Dashboard"

                  : activePage}

              </h1>



              <p>

                Monitor patient pathways, identify delays and improve

                clinical workflows.

              </p>

            </div>



            <div className="status-pill">

              <span />

              Analytics workspace

            </div>

          </div>



          {loading && (

            <div className="panel">

              <p>Loading CareFlow data...</p>

            </div>

          )}



          {!loading && dataError && (

            <div className="panel">

              <p>{dataError}</p>

              <p>

                Check that all three CSV files are inside the frontend

                public folder.

              </p>

            </div>

          )}



          {!loading && !dataError && (

            <>

              {activePage === "Overview" && (

                <>

                  <div className="section-heading">

                    <h2>Performance Overview</h2>

                    <span>Based on current project analysis</span>

                  </div>



                  <div className="kpi-grid">

                    <Kpi

                      icon={Users}

                      label="Total Patients"

                      value={totalPatients}

                      note="Unique patient cases in event logs"

                      color="blue"

                    />



                    <Kpi

                      icon={CircleCheck}

                      label="Conformance Rate"

                      value={`${conformantPercent.toFixed(1)}%`}

                      note={`${conformantCases} of ${totalCases} cases conformant`}

                      color="green"

                    />



                    <Kpi

                      icon={Clock3}

                      label="Average Fitness"

                      value={averageFitness.toFixed(2)}

                      note="Average trace fitness (0–1)"

                      color="purple"

                    />



                    <Kpi

                      icon={CircleAlert}

                      label="Bottleneck Count"

                      value={bottleneckCount}

                      note="High priority · ≥ 35 min"

                      color="orange"

                    />

                  </div>



                  <div className="content-grid">

                    <div className="panel chart-panel">

                      <div className="panel-heading">

                        <div>

                          <h3>Clinical Transition Bottlenecks</h3>

                          <p>Average transition time in minutes</p>

                        </div>



                        <span className="tag">Top delays</span>

                      </div>



                      <div className="chart-area">

                        <ResponsiveContainer width="100%" height="100%">

                          <BarChart

                            data={filteredBottlenecks}

                            layout="vertical"

                            margin={{ left: 15, right: 22 }}

                          >

                            <CartesianGrid

                              strokeDasharray="3 3"

                              horizontal={false}

                            />



                            <XAxis

                              type="number"

                              tick={{ fill: "#8190a5", fontSize: 11 }}

                            />



                            <YAxis

                              dataKey="activity"

                              type="category"

                              width={150}

                              tick={{ fill: "#56657a", fontSize: 11 }}

                            />



                            <Tooltip

                              formatter={(value) => [

                                `${value} min`,

                                "Average time",

                              ]}

                            />



                            <Bar

                              dataKey="minutes"

                              fill="#3978f6"

                              radius={[0, 5, 5, 0]}

                              barSize={20}

                            />

                          </BarChart>

                        </ResponsiveContainer>

                      </div>

                    </div>



                    <div className="panel insights-panel">

                      <div className="panel-heading">

                        <div>

                          <h3>Key Insights</h3>

                          <p>Areas to investigate</p>

                        </div>



                        <Activity size={20} color="#3978f6" />

                      </div>



                      <div className="insight-item">

                        <div className="insight-icon orange">

                          <Clock3 size={18} />

                        </div>



                        <div>

                          <b>Longest average transition</b>

                          <p>

                            {topBottleneck?.activity || "No data available"}

                          </p>



                          <strong>

                            {topBottleneck

                              ? `${topBottleneck.minutes.toFixed(2)} minutes`

                              : "—"}

                          </strong>

                        </div>

                      </div>



                      <div className="insight-item">

                        <div className="insight-icon purple">

                          <GitBranch size={18} />

                        </div>



                        <div>

                          <b>Process deviations</b>

                          <p>

                            Cases not matching the discovered process model

                          </p>

                          <strong>{processDeviations.length} cases</strong>

                        </div>

                      </div>



                      <div className="insight-note">

                        <ArrowUpRight size={17} />

                        <span>

                          Review the highest-delay transitions first.

                          These are analytical findings, not clinical

                          diagnoses.

                        </span>

                      </div>

                    </div>

                  </div>



                  <div className="panel table-panel">

                    <div className="panel-heading">

                      <div>

                        <h3>Transition Summary</h3>

                        <p>

                          Selected transitions from bottleneck analysis

                        </p>

                      </div>



                      <button

                        className="text-button"

                        onClick={() =>

                          setActivePage("Bottleneck Analysis")

                        }

                      >

                        View analysis →

                      </button>

                    </div>



                    <div>

                      <b>Longest average transition</b>

                      <p>

                        {topBottleneck?.activity || "No data available"}

                      </p>



                      <strong>

                        {topBottleneck

                          ? `${topBottleneck.minutes.toFixed(2)} minutes`

                          : "—"}

                      </strong>

                    </div>



                    <div className="table-wrap">

                      <table>

                        <thead>

                          <tr>

                            <th>Clinical transition</th>

                            <th>Avg. time</th>

                            <th>Priority</th>

                          </tr>

                        </thead>



                        <tbody>

                          {filteredBottlenecks.slice(0, 5).map((item) => (

                            <tr key={item.activity}>

                              <td>{item.activity}</td>

                              <td>{item.minutes.toFixed(2)} min</td>

                              <td>

                                <span

                                  className={`priority ${

                                    item.minutes >= 35

                                      ? "high"

                                      : item.minutes >= 30

                                        ? "medium"

                                        : "low"

                                  }`}

                                >

                                  {item.minutes >= 35

                                    ? "High"

                                    : item.minutes >= 30

                                      ? "Medium"

                                      : "Low"}

                                </span>

                              </td>

                            </tr>

                          ))}

                        </tbody>

                      </table>

                    </div>

                  </div>

                </>

              )}



              {activePage === "Patient Flow" && (

                <div className="panel flow-panel">

                  <h3>Clinical Patient Journey</h3>

                  <p>

                    Activities loaded from hospital_event_logs.csv.

                  </p>



                  <div className="patient-export-actions">

                    <button

                      className="export-btn csv-export-btn"

                      onClick={downloadPatientCSV}

                    >

                      <Download size={16} />

                      Download CSV

                    </button>



                    <button

                      className="export-btn pdf-export-btn"

                      onClick={downloadPatientPDF}

                    >

                     <Download size={16} />

                     Download PDF

                    </button>

                  </div>



                  <div className="case-selector">

                    <label htmlFor="patientCase">

                      Select Patient Case:{" "}

                    </label>



                    <select

                      id="patientCase"

                      value={selectedCase}

                      onChange={(e) => setSelectedCase(e.target.value)}

                    >

                      {patientCases.map((caseId) => (

                        <option key={caseId} value={caseId}>

                          {caseId}

                        </option>

                      ))}

                    </select>

                  </div>



                  <div className="filter-toolbar">

                    <div className="filter-field">
                      <label htmlFor="globalPatientFilter">Patient ID</label>
                      <select
                        id="globalPatientFilter"
                        value={globalPatientFilter}
                        onChange={(e) => setGlobalPatientFilter(e.target.value)}
                      >
                        <option value="All">All Patients</option>
                        {[...new Set(eventLogs.map((row) => row.case_id))]
                          .filter(Boolean)
                          .sort()
                          .map((caseId) => (
                            <option key={caseId} value={caseId}>
                              {caseId}
                            </option>
                          ))}
                      </select>
                    </div>

                    <div className="filter-field">

                      <label htmlFor="activityFilter">Activity</label>



                      <select

                        id="activityFilter"

                        value={activityFilter}

                        onChange={(e) => setActivityFilter(e.target.value)}

                      >

                        <option value="All">All Activities</option>



                        {[...new Set(eventLogs.map((row) => row.activity_name))]

                          .filter(Boolean)

                          .sort()

                          .map((activity) => (

                            <option key={activity} value={activity}>

                              {activity}

                            </option>

                       ))}

                     </select>

                    </div>



                    <div className="filter-field">

                      <label htmlFor="dateFrom">From Date</label>

                      <input

                        id="dateFrom"

                        type="date"

                        value={dateFrom}

                        max={dateTo || undefined}

                        onChange={(e) => setDateFrom(e.target.value)}

                      />

                    </div>



                    <div className="filter-field">

                      <label htmlFor="dateTo">To Date</label>

                      <input

                        id="dateTo"

                        type="date"

                        value={dateTo}

                        min={dateFrom || undefined}

                        onChange={(e) => setDateTo(e.target.value)}

                      />

                    </div>



                    <button

                      className="reset-filter-btn"

                      onClick={() => {

                        setActivityFilter("All");

                        setDateFrom("");

                        setDateTo("");

                      }}

                    >

                      Reset Filters

                    </button>

                 </div>



                  <div className="patient-timeline">

                    <h3>Patient Journey Timeline</h3>



                    <div className="timeline-list">

                      {selectedEvents.map((row, index) => (

                        <div

                          className="timeline-item"

                          key={`${row.case_id}-${index}`}

                        >

                          <div className="timeline-marker">

                            <span>{index + 1}</span>

                          </div>



                          <div className="timeline-content">

                            <h4>{row.activity_name}</h4>

                            <p>{row.timestamp}</p>



                            {index > 0 && (

                              <p

                                className="waiting-time"

                                style={{

                                  color: "#d97706",

                                  fontSize: "12px",

                                  fontWeight: 600,

                                  marginTop: "6px",

                                }}

                              >

                                <Clock3

                                  size={13}

                                  style={{

                                    display: "inline",

                                    verticalAlign: "middle",

                                    marginRight: "5px",

                                  }}

                                />



                                {row.waitingMinutes !== null

                                  ? `Waited ${row.waitingMinutes} minutes since previous activity`

                                  : "Waiting time unavailable"}

                              </p>

                            )}

                          </div>

                        </div>

                      ))}



                      {selectedEvents.length === 0 && (

                        <p>No events found for this case.</p>

                      )}

                    </div>

                  </div>



                  <div className="table-wrap">

                    <table>

                      <thead>

                        <tr>

                          <th>Case ID</th>

                          <th>Activity</th>

                          <th>Timestamp</th>

                        </tr>

                      </thead>



                      <tbody>

                        {selectedEvents.map((row, index) => (

                          <tr key={`${row.case_id}-${index}`}>

                            <td>{row.case_id}</td>

                            <td>{row.activity_name}</td>

                            <td>{row.timestamp}</td>

                          </tr>

                        ))}



                        {selectedEvents.length === 0 && (

                          <tr>

                            <td colSpan="3">No events available.</td>

                          </tr>

                        )}

                      </tbody>

                    </table>

                  </div>



                  <p className="disclaimer">

                    Showing event records for the selected patient case.

                  </p>

                </div>

              )}

                            {activePage === "Process Map" && (
                <div className="panel">
                  <div className="panel-heading">
                    <div>
                      <h3>Clinical Process Map</h3>
                      <p>Patient activity sequence and average time between activities</p>
                    </div>
                  </div>

                  <div
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      alignItems: "center",
                      justifyContent: "center",
                      gap: "12px",
                      padding: "28px 8px",
                    }}
                  >
                    {[
                      "Patient Registration",
                      "Triage",
                      "Doctor Consultation",
                      "Lab Test",
                      "Lab Result",
                      "Treatment",
                      "Discharge",
                    ].map((activity, index, activities) => {
                      const nextActivity = activities[index + 1];
                      const transition = nextActivity
                        ? filteredBottlenecks.find(
                            (item) =>
                              item.activity === `${activity} → ${nextActivity}`
                          )
                        : null;

                      return (
                        <React.Fragment key={activity}>
                          <div
                            style={{
                              minWidth: "145px",
                              padding: "18px 14px",
                              border: "1px solid #cfe0ff",
                              borderRadius: "12px",
                              background: "#f5f8ff",
                              textAlign: "center",
                              boxShadow: "0 2px 8px rgba(30, 64, 175, 0.06)",
                            }}
                          >
                            <div
                              style={{
                                width: "28px",
                                height: "28px",
                                margin: "0 auto 9px",
                                borderRadius: "50%",
                                display: "grid",
                                placeItems: "center",
                                background: "#3978f6",
                                color: "#fff",
                                fontWeight: 700,
                              }}
                            >
                              {index + 1}
                            </div>
                            <strong style={{ color: "#24334d", fontSize: "13px" }}>
                              {activity}
                            </strong>
                          </div>

                          {nextActivity && (
                            <div
                              style={{
                                minWidth: "82px",
                                textAlign: "center",
                                color: "#64748b",
                              }}
                            >
                              <div style={{ color: "#3978f6", fontSize: "22px" }}>
                                →
                              </div>
                              <small style={{ display: "block", fontWeight: 600 }}>
                                {transition
                                  ? `${transition.minutes.toFixed(1)} min`
                                  : "No data"}
                              </small>
                              <small style={{ display: "block", fontSize: "10px" }}>
                                Average wait
                              </small>
                            </div>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </div>

                  <p className="disclaimer">
                    Average transition times are calculated from the available event
                    records and respond to the current patient and date filters.
                    They describe process timing, not clinical outcomes.
                  </p>
                </div>
              )}

              {activePage === "Waiting Time Heatmap" && (
                <div className="panel">
                  <div className="panel-heading">
                    <div>
                      <h3>Waiting Time Heatmap</h3>
                      <p>Average waiting time between consecutive patient activities</p>
                    </div>
                  </div>

                  <div
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      gap: "10px",
                      margin: "18px 0 22px",
                    }}
                  >
                    {[
                      { label: "Low", range: "Below 30 min", color: "#dcfce7", text: "#166534" },
                      { label: "Medium", range: "30–34.9 min", color: "#ffedd5", text: "#9a3412" },
                      { label: "High", range: "35 min and above", color: "#fee2e2", text: "#991b1b" },
                    ].map((level) => (
                      <div
                        key={level.label}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: "7px",
                          padding: "7px 11px",
                          borderRadius: "8px",
                          background: level.color,
                          color: level.text,
                          fontSize: "12px",
                          fontWeight: 600,
                        }}
                      >
                        <span>{level.label}</span>
                        <span style={{ fontWeight: 400 }}>({level.range})</span>
                      </div>
                    ))}
                  </div>

                  {filteredBottlenecks.length > 0 ? (
                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
                        gap: "14px",
                      }}
                    >
                      {filteredBottlenecks.map((item, index) => {
                        const minutes = Number(item.minutes);
                        const level = minutes >= 35
                          ? { label: "High delay", background: "#fee2e2", color: "#991b1b", border: "#fca5a5" }
                          : minutes >= 30
                            ? { label: "Medium delay", background: "#ffedd5", color: "#9a3412", border: "#fdba74" }
                            : { label: "Low delay", background: "#dcfce7", color: "#166534", border: "#86efac" };

                        return (
                          <div
                            key={`${item.activity}-${index}`}
                            style={{
                              padding: "18px",
                              borderRadius: "12px",
                              background: level.background,
                              border: `1px solid ${level.border}`,
                              color: level.color,
                              minHeight: "112px",
                              display: "flex",
                              flexDirection: "column",
                              justifyContent: "space-between",
                            }}
                          >
                            <strong style={{ fontSize: "13px", lineHeight: 1.5 }}>
                              {item.activity}
                            </strong>
                            <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: "8px", marginTop: "12px" }}>
                              <strong style={{ fontSize: "25px" }}>
                                {Number.isFinite(minutes) ? minutes.toFixed(1) : "—"}
                                <span style={{ fontSize: "12px", marginLeft: "4px" }}>min</span>
                              </strong>
                              <span style={{ fontSize: "11px", fontWeight: 600 }}>{level.label}</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <p style={{ padding: "24px", textAlign: "center" }}>
                      No waiting-time data available for the selected filters.
                    </p>
                  )}

                  <p className="disclaimer" style={{ marginTop: "18px" }}>
                    Heatmap colors classify average transition waiting times: below 30 minutes is low, 30–34.9 minutes is medium, and 35 minutes or more is high. Values respond to the current dashboard filters. These are process-delay indicators, not clinical outcomes.
                  </p>
                </div>
              )}

              {activePage === "Bottleneck Analysis" && (

                <div className="panel chart-panel standalone-chart">

                  {topBottleneck && (

                    <div className="bottleneck-highlight">

                      <h3>Highest Delay Transition</h3>

                      <p>{topBottleneck.activity}</p>

                      <strong>

                        {topBottleneck.minutes.toFixed(2)} minutes

                      </strong>

                    </div>

                  )}



                  <div className="panel-heading">

                    <div>

                      <h3>All Transition Bottlenecks</h3>

                      <p>Average transition time (minutes)</p>

                    </div>

                  </div>



                  <div className="patient-export-actions">

                    <button

                      className="export-btn csv-export-btn"

                      onClick={downloadBottleneckCSV}

                    >

                      <Download size={16} />

                      Download CSV

                    </button>

                  </div>



                  <div className="chart-area large-chart">

                    <ResponsiveContainer width="100%" height="100%">

                      <BarChart

                        data={filteredBottlenecks}

                        layout="vertical"

                        margin={{ left: 15, right: 30 }}

                      >

                        <CartesianGrid

                          strokeDasharray="3 3"

                          horizontal={false}

                        />



                        <XAxis type="number" />



                        <YAxis

                          dataKey="activity"

                          type="category"

                          width={165}

                          tick={{ fontSize: 12 }}

                        />



                        <Tooltip

                          formatter={(value) => [

                            `${value} min`,

                            "Average time",

                          ]}

                        />



                        <Bar

                          dataKey="minutes"

                          radius={[0, 5, 5, 0]}

                          barSize={25}

                        >

                          {filteredBottlenecks.map((item) => (

                            <Cell

                              key={item.activity}

                              fill={

                                item.minutes >= 35

                                  ? "#dc4b4b"

                                  : item.minutes >= 30

                                    ? "#ed9b35"

                                    : "#2eaa70"

                              }

                            />

                          ))}

                        </Bar>

                      </BarChart>

                    </ResponsiveContainer>

                  </div>



                  <div className="table-wrap">

                    <table>

                      <thead>

                        <tr>

                          <th>Transition</th>

                          <th>Average (min)</th>

                          <th>Priority</th>

                        </tr>

                      </thead>



                      <tbody>

                        {filteredBottlenecks.map((item) => (

                          <tr key={item.activity}>

                            <td>{item.activity}</td>

                            <td>{item.minutes.toFixed(2)}</td>

                            <td>

                              <span

                                className={`priority ${

                                  item.minutes >= 35

                                    ? "high"

                                    : item.minutes >= 30

                                      ? "medium"

                                      : "low"

                                }`}

                              >

                                {item.minutes >= 35

                                  ? "High"

                                  : item.minutes >= 30

                                    ? "Medium"

                                    : "Low"}

                              </span>

                            </td>

                          </tr>

                        ))}

                      </tbody>

                    </table>

                  </div>

                </div>

              )}



              {activePage === "Process Deviation Details" && (
                <div className="panel">
                  <div className="panel-heading">
                    <div>
                      <h3>Process Deviation Details</h3>
                      <p>Cases flagged as non-conformant in the current conformance results</p>
                    </div>
                    <span className="priority high">{processDeviations.length} Deviations</span>
                  </div>

                  <div className="kpi-grid">
                    <Kpi
                      icon={CircleAlert}
                      label="Non-conformant Cases"
                      value={processDeviations.length}
                      note="Within current dashboard filters"
                      color="orange"
                    />
                    <Kpi
                      icon={Users}
                      label="Cases Reviewed"
                      value={globallyFilteredConformance.length}
                      note="Available conformance records"
                      color="blue"
                    />
                  </div>

                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Case ID</th>
                          <th>Trace Fitness</th>
                          <th>Missing Tokens</th>
                          <th>Remaining Tokens</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {processDeviations.map((row, index) => {
                          const fitness = Number(row.trace_fitness);
                          const showTokenValue = (value) =>
                            value === undefined || value === null || value === ""
                              ? "Not available"
                              : String(value);
                          return (
                            <tr key={`${row.case_id || index}-deviation`}>
                              <td>{row.case_id || `Case ${index + 1}`}</td>
                              <td>{Number.isFinite(fitness) ? fitness.toFixed(2) : "—"}</td>
                              <td>{showTokenValue(row.missing_tokens)}</td>
                              <td>{showTokenValue(row.remaining_tokens)}</td>
                              <td><span className="priority high">Non-conformant</span></td>
                            </tr>
                          );
                        })}
                        {processDeviations.length === 0 && (
                          <tr><td colSpan="5">No process deviations found for the current filters.</td></tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  <p className="disclaimer" style={{ marginTop: "16px" }}>
                    Deviation details are taken from the existing conformance results. Missing and remaining tokens describe differences between the recorded trace and the process model; they do not indicate clinical errors.
                  </p>
                </div>
              )}

              {activePage === "Conformance" && (

                <div className="conformance-page">

                  <div className="panel">

                    <h3>Conformance Analysis</h3>

                    <p>

                      Patient cases evaluated against the discovered process

                      model.

                    </p>



                    <div className="patient-export-actions">

                      <button

                        className="export-btn csv-export-btn"

                        onClick={downloadConformanceCSV}

                      >

                        <Download size={16} />

                        Download CSV

                      </button>



                      <button

                        className="export-btn pdf-export-btn"

                        onClick={downloadConformancePDF}

                      >

                        <Download size={16} />

                        Download PDF

                      </button>

                    </div>



                    <div className="kpi-grid">

                      <Kpi

                        icon={Users}

                        label="Total Cases"

                        value={totalCases}

                        note="Cases analysed"

                        color="blue"

                      />



                      <Kpi

                        icon={CircleCheck}

                        label="Conformant"

                        value={conformantCases}

                        note={`${conformantPercent.toFixed(1)}% of cases`}

                        color="green"

                      />



                      <Kpi

                        icon={CircleAlert}

                        label="Non-conformant"

                        value={nonConformantCases}

                        note={`${nonConformantPercent.toFixed(1)}% of cases`}

                        color="orange"

                      />

                    </div>

                  </div>



                  <div className="panel">

                    <h3>Conformance Breakdown</h3>



                    <div style={{ width: "100%", height: 300 }}>

                      <ResponsiveContainer width="100%" height="100%">

                        <PieChart>

                          <Pie

                            data={[

                              {

                                name: "Conformant",

                                value: conformantCases,

                              },

                              {

                                name: "Non-conformant",

                                value: nonConformantCases,

                              },

                            ].filter((item) => item.value > 0)}

                            dataKey="value"

                            nameKey="name"

                            cx="50%"

                            cy="50%"

                            outerRadius={95}

                            label={({ name, percent }) =>

                              `${name} ${(percent * 100).toFixed(1)}%`

                            }

                          >

                            <Cell fill="#16a34a" />

                            <Cell fill="#f59e0b" />

                          </Pie>



                          <Tooltip />

                          <Legend />

                        </PieChart>

                      </ResponsiveContainer>

                    </div>

                  </div>



                  <div className="panel">

                    <h3>Case-wise Conformance Results</h3>



                    <div className="table-wrap">

                      <table>

                        <thead>

                          <tr>

                            <th>Case ID</th>

                            <th>Trace Fitness</th>

                            <th>Conformance Status</th>

                          </tr>

                        </thead>



                        <tbody>

                          {globallyFilteredConformance.map((row, index) => {

                            const isConformant = isConformantValue(

                              row.is_conformant

                            );



                            const fitness = Number(row.trace_fitness);



                            return (

                              <tr key={`${row.case_id || index}`}>

                                <td>

                                  {row.case_id || `Case ${index + 1}`}

                                </td>



                                <td>

                                  {Number.isFinite(fitness)

                                    ? fitness.toFixed(2)

                                    : "—"}

                                </td>



                                <td>

                                  <span

                                    className={`priority ${

                                      isConformant ? "medium" : "high"

                                    }`}

                                  >

                                    {isConformant

                                      ? "Conformant"

                                      : "Non-conformant"}

                                  </span>

                                </td>

                              </tr>

                            );

                          })}



                          {globallyFilteredConformance.length === 0 && (

                            <tr>

                              <td colSpan="3">

                                No conformance results available.

                              </td>

                            </tr>

                          )}

                        </tbody>

                      </table>

                    </div>



                    <p className="disclaimer">

                      Results reflect the supplied process-mining dataset

                      and model. They are not clinical diagnoses.

                    </p>

                  </div>



                  <div className="panel">

                    <h3>Trace Fitness</h3>



                    <div className="fitness-number">

                      {averageFitness.toFixed(2)} <span>/ 1.00</span>

                    </div>



                    <p>

                      Average trace fitness from the current conformance

                      results.

                    </p>



                    <p className="disclaimer">

                      Use this score as a process similarity measure, not a

                      patient outcome measure.

                    </p>

                  </div>

                </div>

              )}

            </>

          )}



          <footer>

            CareFlow · Clinical Pathway Process Mining

            <span>Project analytics preview</span>

          </footer>

        </section>

      </main>

    </div>

  );

}



function Kpi({ icon: Icon, label, value, note, color }) {

  return (

    <div className="panel kpi-card">

      <div className={`kpi-icon ${color}`}>

        <Icon size={21} />

      </div>



      <p>{label}</p>



      <div className="kpi-value">{value}</div>



      <span>{note}</span>

    </div>

  );

}



export default App;

import { useState, useEffect } from "react";
import Papa from "papaparse";
import {
  Activity,
  LayoutDashboard,
  GitBranch,
  ChartNoAxesColumn,
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
  { name: "Bottleneck Analysis", icon: ChartNoAxesColumn },
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
  const [loading, setLoading] = useState(true);
  const [dataError, setDataError] = useState("");

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

  const totalCases = conformance.length;

  const conformantCases = conformance.filter((row) =>
    isConformantValue(row.is_conformant)
  ).length;

  const nonConformantCases = totalCases - conformantCases;

  const averageFitness = totalCases
    ? conformance.reduce(
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

  const topBottleneck = [...bottlenecks].sort(
    (a, b) => b.minutes - a.minutes
  )[0];

  const processDeviations = nonConformantCases;

  const patientCases = [
    ...new Set(eventLogs.map((row) => row.case_id)),
  ]
    .filter(Boolean)
    .sort();

  const selectedEvents = eventLogs.filter(
    (row) => row.case_id === selectedCase
  );

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
                      label="Total Patient Cases"
                      value={totalCases}
                      note="Cases analysed"
                      color="blue"
                    />

                    <Kpi
                      icon={CircleCheck}
                      label="Conformant Cases"
                      value={conformantCases}
                      note={`${conformantPercent.toFixed(1)}% of cases`}
                      color="green"
                    />

                    <Kpi
                      icon={CircleAlert}
                      label="Non-conformant"
                      value={nonConformantCases}
                      note={`${nonConformantPercent.toFixed(1)}% need review`}
                      color="orange"
                    />

                    <Kpi
                      icon={Clock3}
                      label="Avg. Trace Fitness"
                      value={averageFitness.toFixed(2)}
                      note="Process conformance"
                      color="purple"
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
                            data={bottlenecks}
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
                          <strong>{processDeviations} cases</strong>
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
                          {bottlenecks.slice(0, 5).map((item, index) => (
                            <tr key={item.activity}>
                              <td>{item.activity}</td>
                              <td>{item.minutes.toFixed(2)} min</td>
                              <td>
                                <span
                                  className={`priority ${
                                    index < 2 ? "high" : "medium"
                                  }`}
                                >
                                  {index < 2 ? "Review" : "Monitor"}
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

                  <div className="chart-area large-chart">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart
                        data={bottlenecks}
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
                          fill="#3978f6"
                          radius={[0, 5, 5, 0]}
                          barSize={25}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="table-wrap">
                    <table>
                      <thead>
                        <tr>
                          <th>Transition</th>
                          <th>Average (min)</th>
                        </tr>
                      </thead>

                      <tbody>
                        {bottlenecks.map((item) => (
                          <tr key={item.activity}>
                            <td>{item.activity}</td>
                            <td>{item.minutes.toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
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
                          {conformance.map((row, index) => {
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

                          {conformance.length === 0 && (
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

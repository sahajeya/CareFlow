\# Day 4 – System Testing and Validation Report



\## 1. Introduction

System testing was performed to verify the functionality, API responses, input validation, and frontend error handling of the CareFlow application.



\## 2. API Endpoint Testing



A total of 8 API endpoint tests were performed.



| API Endpoint | Expected Status | Actual Status | Result |

|---|---:|---:|---|

| /api/status | 200 | 200 | Pass |

| /api/summary | 200 | 200 | Pass |

| /api/patients | 200 | 200 | Pass |

| /api/patients/P0001 | 200 | 200 | Pass |

| /api/patients/INVALID001 | 404 | 404 | Pass |

| /api/bottlenecks | 200 | 200 | Pass |

| /api/activity-waiting | 200 | 200 | Pass |

| /api/pathway-analysis | 200 | 200 | Pass |



\*\*Result: 8 out of 8 API tests passed.\*\*



\## 3. Invalid Route Testing



| Test Case | Actual Status | Result |

|---|---:|---|

| Empty patient ID route | 404 | Pass |

| Unknown API route | 404 | Pass |

| Unknown webpage route | 404 | Pass |



\*\*Result: 3 out of 3 invalid-route tests passed.\*\*



\## 4. Frontend Testing



\- Dashboard loaded successfully in Chrome.

\- KPI cards displayed the expected values.

\- Patient journey records were displayed.

\- Browser Console showed no visible application errors.

\- Frontend error-handling functions were inspected.



\## 5. Database Verification



\- Total patients: 100

\- Total event records: 700

\- Total hospital activities: 7

\- Database connection verified successfully.



\## 6. Conclusion



System testing confirmed that the tested CareFlow API endpoints, invalid-route handling, database connection, and dashboard display are functioning as expected. No visible application errors were found in the local browser console.


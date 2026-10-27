-- CareFlow Week 3: Transition Time Analysis

WITH ordered_events AS (
    SELECT
        case_id,
        activity_name,
        timestamp AS event_timestamp,

        LAG(activity_name) OVER (
            PARTITION BY case_id
            ORDER BY timestamp
        ) AS previous_activity,

        LAG(timestamp) OVER (
            PARTITION BY case_id
            ORDER BY timestamp
        ) AS previous_timestamp

    FROM `clear-nebula-510706-t0.careflow_data.stg_hospital_events`
),

transitions AS (
    SELECT
        case_id,
        previous_activity,
        activity_name AS next_activity,

        TIMESTAMP_DIFF(
            event_timestamp,
            previous_timestamp,
            MINUTE
        ) AS transition_minutes

    FROM ordered_events
    WHERE previous_timestamp IS NOT NULL
)

SELECT
    previous_activity,
    next_activity,
    COUNT(*) AS transition_count,
    COUNT(DISTINCT case_id) AS unique_patients,
    ROUND(AVG(transition_minutes), 2) AS average_transition_minutes,
    MAX(transition_minutes) AS maximum_transition_minutes

FROM transitions
WHERE transition_minutes >= 0

GROUP BY
    previous_activity,
    next_activity

ORDER BY average_transition_minutes DESC;
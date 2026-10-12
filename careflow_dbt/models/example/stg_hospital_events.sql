
SELECT
    CAST(case_id AS STRING) AS case_id,
    CAST(activity_name AS STRING) AS activity_name,
    CAST(timestamp AS TIMESTAMP) AS timestamp

FROM `united-firefly-510706-m2.CareFlow_data.hospital_event_logs`

WHERE case_id IS NOT NULL
  AND activity_name IS NOT NULL
  AND timestamp IS NOT NULL


{{ config(materialized='table') }}

SELECT
  stop_id,
  COUNT(*)                                    AS total_records,
  ROUND(AVG(delay_minutes), 2)                AS avg_delay_minutes,
  ROUND(MAX(delay_minutes), 2)                AS max_delay_minutes,
  ROUND(AVG(CAST(is_delayed AS INT)), 2)      AS delay_rate,
  SUM(CASE WHEN delay_bucket = 'severe'   THEN 1 ELSE 0 END) AS severe_count,
  SUM(CASE WHEN delay_bucket = 'moderate' THEN 1 ELSE 0 END) AS moderate_count,
  SUM(CASE WHEN delay_bucket = 'minor'    THEN 1 ELSE 0 END) AS minor_count,
  SUM(CASE WHEN delay_bucket = 'on_time'  THEN 1 ELSE 0 END) AS on_time_count
FROM freightops.silver_train_delays
GROUP BY stop_id

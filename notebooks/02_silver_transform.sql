-- Silver layer: transform bronze GTFS-RT data into clean delay metrics

CREATE TABLE IF NOT EXISTS freightops.silver_train_delays (
  trip_id       STRING,
  stop_id       STRING,
  delay_seconds BIGINT,
  delay_minutes DOUBLE,
  is_delayed    BOOLEAN,
  delay_bucket  STRING,
  ingested_at   STRING
)
USING DELTA;

INSERT INTO freightops.silver_train_delays
SELECT
  trip_id,
  stop_id,
  COALESCE(arrival_delay, departure_delay, 0) AS delay_seconds,
  ROUND(COALESCE(arrival_delay, departure_delay, 0) / 60.0, 2) AS delay_minutes,
  COALESCE(arrival_delay, departure_delay, 0) > 300 AS is_delayed,
  CASE
    WHEN COALESCE(arrival_delay, departure_delay, 0) <= 0   THEN 'on_time'
    WHEN COALESCE(arrival_delay, departure_delay, 0) <= 300 THEN 'minor'
    WHEN COALESCE(arrival_delay, departure_delay, 0) <= 600 THEN 'moderate'
    ELSE 'severe'
  END AS delay_bucket,
  ingested_at
FROM freightops.bronze_gtfs_rt;

-- Gold layer: stop-level aggregated features for ML

CREATE TABLE IF NOT EXISTS freightops.gold_delay_features (
  stop_id            STRING,
  total_records      BIGINT,
  avg_delay_minutes  DOUBLE,
  max_delay_minutes  DOUBLE,
  delay_rate         DOUBLE,
  dominant_bucket    STRING
)
USING DELTA;

INSERT INTO freightops.gold_delay_features
SELECT
  stop_id,
  COUNT(*)                               AS total_records,
  ROUND(AVG(delay_minutes), 2)           AS avg_delay_minutes,
  ROUND(MAX(delay_minutes), 2)           AS max_delay_minutes,
  ROUND(AVG(CAST(is_delayed AS INT)), 2) AS delay_rate,
  first(delay_bucket)                    AS dominant_bucket
FROM freightops.silver_train_delays
GROUP BY stop_id;

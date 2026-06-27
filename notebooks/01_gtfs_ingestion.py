# Databricks notebook source
# MAGIC %pip install gtfs-realtime-bindings requests

# COMMAND ----------

# MAGIC %restart_python

# COMMAND ----------

import requests
from google.transit import gtfs_realtime_pb2

# BART (San Francisco) public GTFS-RT feed - no auth needed
GTFS_RT_URL = "http://api.bart.gov/gtfsrt/tripupdate.aspx"

response = requests.get(GTFS_RT_URL, timeout=10)
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

print(f"Entities in feed: {len(feed.entity)}")
for entity in feed.entity[:3]:
    print(entity)

# COMMAND ----------

from datetime import datetime

records = []
for entity in feed.entity:
    if entity.HasField("trip_update"):
        tu = entity.trip_update
        for stu in tu.stop_time_update:
            records.append({
                "entity_id":        entity.id,
                "trip_id":          tu.trip.trip_id,
                "route_id":         tu.trip.route_id,
                "stop_id":          stu.stop_id,
                "arrival_delay":    stu.arrival.delay   if stu.HasField("arrival")   else None,
                "departure_delay":  stu.departure.delay if stu.HasField("departure") else None,
                "ingested_at":      datetime.utcnow().isoformat(),
            })

print(f"Total stop-time records: {len(records)}")
print(records[0])

# COMMAND ----------

import pandas as pd

df = pd.DataFrame(records)
print(df.shape)
print(df.head())

# COMMAND ----------

df.to_csv("/tmp/gtfs_bronze.csv", index=False)
print("CSV saved!")
print(f"Rows: {len(df)}")
print(df.dtypes)

# COMMAND ----------

COPY INTO freightops.bronze_gtfs_rt
FROM (
  SELECT 
    entity_id,
    trip_id,
    route_id,
    stop_id,
    CAST(arrival_delay AS BIGINT),
    CAST(departure_delay AS BIGINT),
    ingested_at
  FROM read_files(
    'dbfs:/tmp/gtfs_bronze.csv',
    format => 'csv',
    header => true
  )
)
FILEFORMAT = CSV;
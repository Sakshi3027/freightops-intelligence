# Databricks notebook source
# MAGIC %pip install xgboost scikit-learn pandas

# COMMAND ----------

# MAGIC %restart_python

# COMMAND ----------

# MAGIC %pip install gtfs-realtime-bindings xgboost scikit-learn

# COMMAND ----------

# MAGIC %restart_python

# COMMAND ----------

import requests
from google.transit import gtfs_realtime_pb2
import pandas as pd

response = requests.get('http://api.bart.gov/gtfsrt/tripupdate.aspx', timeout=10)
feed = gtfs_realtime_pb2.FeedMessage()
feed.ParseFromString(response.content)

records = []
for entity in feed.entity:
    if entity.HasField('trip_update'):
        tu = entity.trip_update
        for stu in tu.stop_time_update:
            arr = stu.arrival.delay if stu.HasField('arrival') else 0
            dep = stu.departure.delay if stu.HasField('departure') else 0
            records.append({
                'trip_id': tu.trip.trip_id,
                'stop_id': stu.stop_id,
                'delay_seconds': arr if arr else dep,
            })

df = pd.DataFrame(records)
df['delay_minutes'] = df['delay_seconds'] / 60
df['is_delayed'] = (df['delay_seconds'] > 300).astype(int)
df['stop_num'] = df['stop_id'].str.extract(r'(\d+)').astype(float)

print(df.shape)
print(df.head())

# COMMAND ----------

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score

FEATURES = ['delay_seconds', 'delay_minutes', 'stop_num']
TARGET   = 'is_delayed'

clean = df.dropna(subset=FEATURES + [TARGET])
X = clean[FEATURES]
y = clean[TARGET]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = XGBClassifier(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)
model.fit(X_train, y_train)

preds = model.predict(X_test)
f1  = f1_score(y_test, preds, zero_division=0)
acc = accuracy_score(y_test, preds)

print(f"Accuracy : {acc:.3f}")
print(f"F1 Score : {f1:.3f}")
print(f"Features : {FEATURES}")
print(f"Train rows: {len(X_train)}  Test rows: {len(X_test)}")
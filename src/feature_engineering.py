import json
import pandas as pd
from preprocess import load_events
from feature_extraction import extract_features

EVENTS_PATH = 'c:\\Users\\tt8445\\Documents\\GitHub\\linkedin\\retail_events.json'
INCIDENT_LOG_PATH = 'incident_log.json'
OUTPUT_PATH = 'output/ml_training_data_advanced.json'

# Load events and features
events = load_events(EVENTS_PATH)
features = extract_features(events)
df = pd.DataFrame(features)

# Session-level features: group by scanner_id
session_features = df.groupby('scanner_id').agg({
    'event_type': 'count',
    'product_id': 'nunique',
    'queue_length': 'mean',
    'equipment_status': lambda x: (x == 'failure').sum(),
}).reset_index()
session_features.columns = ['scanner_id', 'event_count', 'unique_products', 'avg_queue_length', 'failures']

# Merge session features back to event features
df = df.merge(session_features, on='scanner_id', how='left')

# Load incident labels
with open(INCIDENT_LOG_PATH, 'r') as f:
    incidents = json.load(f)
incident_set = set((i['timestamp'], i.get('scanner_id'), i.get('product')) for i in incidents)

# Convert all keys to string for matching

def to_key(ts, scanner, product):
    ts_str = str(ts).replace('T', ' ').replace('Z', '')
    scanner_str = str(scanner)
    product_str = str(product)
    return (ts_str, scanner_str, product_str)

print("Sample incident keys:")
for i in incidents[:5]:
    print(to_key(i['timestamp'], i.get('scanner_id'), i.get('product')))
print("Sample event keys:")
for idx, row in df.head(5).iterrows():
    print(to_key(row.get('timestamp'), row.get('scanner_id'), row.get('product_id')))

incident_set = set(to_key(i['timestamp'], i.get('scanner_id'), i.get('product')) for i in incidents)

def label_row(row):
    key = to_key(row.get('timestamp'), row.get('scanner_id'), row.get('product_id'))
    return 1 if key in incident_set else 0

df['incident_label'] = df.apply(label_row, axis=1)

# Save advanced training data

# Print class counts for debugging
print("Class counts:")
print(df['incident_label'].value_counts())

print(f"Advanced training data shape: {df.shape}")
df.to_json(OUTPUT_PATH, orient='records', lines=False)

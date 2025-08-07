import json
from preprocess import load_events
from feature_extraction import extract_features
from datetime import datetime
from typing import List, Dict, Any

# Load ground truth incidents
INCIDENT_LOG_PATH = 'incident_log.json'
EVENTS_PATH = 'c:\\Users\\tt8445\\Documents\\GitHub\\linkedin\\retail_events.json'
OUTPUT_PATH = 'output/ml_training_data.json'

def load_incident_labels(path: str) -> List[Dict[str, Any]]:
    with open(path, 'r') as f:
        incidents = json.load(f)
    # Parse timestamps
    for inc in incidents:
        ts = inc.get('timestamp')
        if ts:
            try:
                inc['timestamp'] = datetime.fromisoformat(ts.replace('Z', ''))
            except Exception:
                pass
    return incidents

def label_events(features: List[Dict[str, Any]], incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Match by timestamp, scanner_id, and product_id if present
    incident_set = set()
    for inc in incidents:
        key = (inc['timestamp'], inc.get('scanner_id'), inc.get('product'))
        incident_set.add(key)
    labeled = []
    for feat in features:
        key = (feat.get('timestamp'), feat.get('scanner_id'), feat.get('product_id'))
        label = 1 if key in incident_set else 0
        feat['incident_label'] = label
        labeled.append(feat)
    return labeled

if __name__ == '__main__':
    events = load_events(EVENTS_PATH)
    features = extract_features(events)
    incidents = load_incident_labels(INCIDENT_LOG_PATH)
    labeled_data = label_events(features, incidents)
    print(f"Prepared {len(labeled_data)} labeled samples.")
    print("Sample labeled data:")
    for row in labeled_data[:3]:
        print(row)
    # Save to output file
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(labeled_data, f, default=str, indent=2)

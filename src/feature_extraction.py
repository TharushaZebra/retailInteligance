import json
from datetime import datetime
from typing import List, Dict, Any
from preprocess import load_events

# Feature extraction for retail events

def extract_features(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extracts features from raw event data for downstream analysis.
    Returns a list of feature dicts, one per event.
    """
    features = []
    for event in events:
        feat = {}
        # Basic features
        feat['timestamp'] = event.get('timestamp')
        feat['event_type'] = event.get('event_type')
        feat['scanner_id'] = event.get('scanner_id')
        feat['product_id'] = event.get('product_id')
        feat['barcode_data'] = event.get('barcode_data')
        feat['rfid_tag'] = event.get('rfid_tag')
        feat['camera_label'] = event.get('camera_label')
        feat['queue_length'] = event.get('queue_length')
        feat['equipment_status'] = event.get('equipment_status')
        # Add more features as needed
        features.append(feat)
    return features

if __name__ == '__main__':
    events = load_events('c:\\Users\\tt8445\\Documents\\GitHub\\linkedin\\retail_events.json')
    features = extract_features(events)
    print(f"Extracted features for {len(features)} events.")
    for f in features[:3]:
        print(f)

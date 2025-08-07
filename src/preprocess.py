import json
from datetime import datetime
from typing import List, Dict, Any

# Path to the retail events file
events_path = 'c:\\Users\\tt8445\\Documents\\GitHub\\linkedin\\retail_events.json'

def load_events(path: str) -> List[Dict[str, Any]]:
    """Load and clean retail events from JSON file."""
    with open(path, 'r') as f:
        events = json.load(f)
    cleaned = []
    for event in events:
        # Ensure timestamp is present and parseable
        ts = event.get('timestamp')
        if ts:
            try:
                event['timestamp'] = datetime.fromisoformat(ts.replace('Z', ''))
            except Exception:
                continue  # skip if timestamp is invalid
        cleaned.append(event)
    return cleaned

if __name__ == '__main__':
    events = load_events(events_path)
    print(f"Loaded {len(events)} events.")
    # Print first 3 events for inspection
    for e in events[:3]:
        print(e)

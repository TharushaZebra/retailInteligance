import json
import random
from datetime import datetime, timedelta

events = []
start_time = datetime(2025, 7, 27, 12, 0, 0)

for i in range(100):
    event = {
        "timestamp": (start_time + timedelta(seconds=i*5)).isoformat() + "Z",
        "scanner_id": f"ZB{random.randint(10000,99999)}",
        "event_type": random.choice(["decode", "no-decode"]),
        "barcode_data": f"CODE{random.randint(1000,9999)}"
    }
    events.append(event)

with open("events.json", "w") as f:
    json.dump(events, f, indent=2)

print("Sample dataset 'events.json' created with 100 records.")
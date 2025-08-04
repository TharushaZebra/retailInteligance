import json
import random
from datetime import datetime, timedelta

SCANNERS = ["SCO1", "SCO2", "SCO3"]
PRODUCTS = [
    {"name": "apple", "barcode": "CODE123", "rfid": "RFID123"},
    {"name": "banana", "barcode": "CODE124", "rfid": "RFID124"},
    {"name": "bread", "barcode": "CODE125", "rfid": "RFID125"},
    {"name": "milk", "barcode": "CODE126", "rfid": "RFID126"},
    {"name": "wine", "barcode": "CODE127", "rfid": "RFID127"},
    {"name": "chocolate_bar", "barcode": "CODE128", "rfid": "RFID128"},
    {"name": "orange", "barcode": "CODE129", "rfid": "RFID129"},
    {"name": "watermelon", "barcode": "CODE130", "rfid": "RFID130"},
    {"name": "snack", "barcode": "CODE131", "rfid": "RFID131"},
    {"name": "cheese", "barcode": "CODE132", "rfid": "RFID132"},
    {"name": "eggs", "barcode": "CODE133", "rfid": "RFID133"},
    {"name": "chicken", "barcode": "CODE134", "rfid": "RFID134"},
    {"name": "beef", "barcode": "CODE135", "rfid": "RFID135"},
    {"name": "fish", "barcode": "CODE136", "rfid": "RFID136"},
    {"name": "lettuce", "barcode": "CODE137", "rfid": "RFID137"},
    {"name": "tomato", "barcode": "CODE138", "rfid": "RFID138"},
    {"name": "potato", "barcode": "CODE139", "rfid": "RFID139"},
    {"name": "onion", "barcode": "CODE140", "rfid": "RFID140"},
    {"name": "cereal", "barcode": "CODE141", "rfid": "RFID141"},
    {"name": "soda", "barcode": "CODE142", "rfid": "RFID142"}
]

START_TIME = datetime(2025, 8, 4, 9, 0, 0)
SECONDS = 3600  # 1 hour

# Incident types and their probabilities per hour
INCIDENTS = [
    ("scanner_avoidance", 3),
    ("product_swap", 3),
    ("unscanned_item", 3),
    ("queue_buildup", 2),
    ("scanner_failure", 1),
    ("long_wait", 1)
]

random.seed(42)

def pick_product(exclude=None):
    choices = [p for p in PRODUCTS if not exclude or p["name"] != exclude]
    return random.choice(choices)

def main():
    events = []
    incident_log = []
    # Preselect incident times
    incident_times = {}
    for incident, count in INCIDENTS:
        times = sorted(random.sample(range(SECONDS), count))
        incident_times[incident] = times
    # Track scanner status
    scanner_status = {s: "operational" for s in SCANNERS}
    for sec in range(SECONDS):
        timestamp = (START_TIME + timedelta(seconds=sec)).isoformat() + "Z"
        # Check for incidents
        for incident, times in incident_times.items():
            if sec in times:
                scanner = random.choice(SCANNERS)
                if incident == "scanner_avoidance":
                    # RFID and camera, no barcode
                    prod = pick_product()
                    events.append({"timestamp": timestamp, "event_type": "rfid_read", "scanner_id": scanner, "product_id": prod["name"], "rfid_tag": prod["rfid"]})
                    events.append({"timestamp": timestamp, "event_type": "camera_image", "scanner_id": scanner, "product_id": prod["name"], "camera_label": prod["name"]})
                    incident_log.append({"timestamp": timestamp, "scanner_id": scanner, "incident": "scanner_avoidance", "product": prod["name"]})
                elif incident == "product_swap":
                    # Barcode for cheap, RFID/camera for expensive
                    cheap = pick_product()
                    expensive = pick_product(exclude=cheap["name"])
                    events.append({"timestamp": timestamp, "event_type": "barcode_scan", "scanner_id": scanner, "product_id": cheap["name"], "barcode_data": cheap["barcode"]})
                    events.append({"timestamp": timestamp, "event_type": "rfid_read", "scanner_id": scanner, "product_id": expensive["name"], "rfid_tag": expensive["rfid"]})
                    events.append({"timestamp": timestamp, "event_type": "camera_image", "scanner_id": scanner, "product_id": expensive["name"], "camera_label": expensive["name"]})
                    incident_log.append({"timestamp": timestamp, "scanner_id": scanner, "incident": "product_swap", "barcode": cheap["name"], "actual": expensive["name"]})
                elif incident == "unscanned_item":
                    # RFID/camera only
                    prod = pick_product()
                    events.append({"timestamp": timestamp, "event_type": "rfid_read", "scanner_id": scanner, "product_id": prod["name"], "rfid_tag": prod["rfid"]})
                    events.append({"timestamp": timestamp, "event_type": "camera_image", "scanner_id": scanner, "product_id": prod["name"], "camera_label": prod["name"]})
                    incident_log.append({"timestamp": timestamp, "scanner_id": scanner, "incident": "unscanned_item", "product": prod["name"]})
                elif incident == "queue_buildup":
                    # Queue length high
                    queue_len = random.randint(6, 10)
                    events.append({"timestamp": timestamp, "event_type": "queue_status", "scanner_id": scanner, "queue_length": queue_len})
                    incident_log.append({"timestamp": timestamp, "scanner_id": scanner, "incident": "queue_buildup", "queue_length": queue_len})
                elif incident == "scanner_failure":
                    # Equipment failure
                    events.append({"timestamp": timestamp, "event_type": "equipment_status", "scanner_id": scanner, "equipment_status": "failure"})
                    scanner_status[scanner] = "failure"
                    incident_log.append({"timestamp": timestamp, "scanner_id": scanner, "incident": "scanner_failure"})
                elif incident == "long_wait":
                    # Customer present for long time
                    events.append({"timestamp": timestamp, "event_type": "camera_image", "scanner_id": scanner, "product_id": "customer_present"})
                    incident_log.append({"timestamp": timestamp, "scanner_id": scanner, "incident": "long_wait"})
        # Normal events for operational scanners
        for scanner in SCANNERS:
            if scanner_status[scanner] == "operational":
                if random.random() < 0.7:  # 70% chance of normal transaction
                    prod = pick_product()
                    events.append({"timestamp": timestamp, "event_type": "barcode_scan", "scanner_id": scanner, "product_id": prod["name"], "barcode_data": prod["barcode"]})
                    events.append({"timestamp": timestamp, "event_type": "rfid_read", "scanner_id": scanner, "product_id": prod["name"], "rfid_tag": prod["rfid"]})
                    events.append({"timestamp": timestamp, "event_type": "camera_image", "scanner_id": scanner, "product_id": prod["name"], "camera_label": prod["name"]})
                # Queue status every 30 seconds
                if sec % 30 == 0:
                    queue_len = random.randint(0, 5)
                    events.append({"timestamp": timestamp, "event_type": "queue_status", "scanner_id": scanner, "queue_length": queue_len})
            else:
                # If failed, only queue and equipment status
                if sec % 30 == 0:
                    queue_len = random.randint(3, 10)
                    events.append({"timestamp": timestamp, "event_type": "queue_status", "scanner_id": scanner, "queue_length": queue_len})
                if sec % 60 == 0:
                    events.append({"timestamp": timestamp, "event_type": "equipment_status", "scanner_id": scanner, "equipment_status": "failure"})
        # Randomly recover failed scanners after 5-10 minutes
        for scanner in SCANNERS:
            if scanner_status[scanner] == "failure" and random.random() < 0.01:
                events.append({"timestamp": timestamp, "event_type": "equipment_status", "scanner_id": scanner, "equipment_status": "operational"})
                scanner_status[scanner] = "operational"
    # Write dataset
    with open("retail_events.json", "w") as f:
        json.dump(events, f, indent=2)
    with open("incident_log.json", "w") as f:
        json.dump(incident_log, f, indent=2)

if __name__ == "__main__":
    main()

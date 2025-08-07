from feature_extraction import extract_features
from preprocess import load_events
from datetime import timedelta
import json

# Rule-based incident detection

def detect_incidents(features):
    incidents = []
    # Track last seen times and states for each scanner
    last_scanner_status = {}
    last_customer_present = {}
    scanned_products = set()
    rfid_camera_buffer = {}
    barcode_buffer = {}
    for feat in features:
        ts = feat['timestamp']
        scanner = feat['scanner_id']
        product = feat.get('product_id')
        # Buffer events by timestamp and scanner
        key = (ts, scanner)
        if key not in rfid_camera_buffer:
            rfid_camera_buffer[key] = set()
        if key not in barcode_buffer:
            barcode_buffer[key] = set()
        # Collect event types for enhanced logic
        if feat['event_type'] in ['rfid_read', 'camera_image'] and product and product != 'customer_present':
            rfid_camera_buffer[key].add(product)
        if feat['event_type'] == 'barcode_scan' and product:
            barcode_buffer[key].add(product)
        # Queue buildup
        if feat['event_type'] == 'queue_status' and feat['queue_length'] is not None:
            if feat['queue_length'] > 7:
                incidents.append({
                    'timestamp': ts,
                    'scanner_id': scanner,
                    'incident': 'queue_buildup',
                    'queue_length': feat['queue_length']
                })
        # Scanner failure
        if feat['event_type'] == 'equipment_status' and feat['equipment_status'] == 'failure':
            incidents.append({
                'timestamp': ts,
                'scanner_id': scanner,
                'incident': 'scanner_failure'
            })
            last_scanner_status[scanner] = 'failure'
        # Long wait (track consecutive customer_present events)
        if feat['event_type'] == 'camera_image' and product == 'customer_present':
            if scanner not in last_customer_present:
                last_customer_present[scanner] = ts
            else:
                duration = ts - last_customer_present[scanner]
                if duration >= timedelta(minutes=5):
                    incidents.append({
                        'timestamp': ts,
                        'scanner_id': scanner,
                        'incident': 'long_wait'
                    })
                    last_customer_present[scanner] = ts
        # Track scanned products
        if feat['event_type'] == 'barcode_scan' and product:
            scanned_products.add((scanner, product))
    # Enhanced detection after buffering
    for key in rfid_camera_buffer:
        ts, scanner = key
        rfid_products = rfid_camera_buffer[key]
        barcode_products = barcode_buffer.get(key, set())
        # Scanner avoidance: RFID/camera but no barcode for same product
        for prod in rfid_products:
            if prod not in barcode_products:
                incidents.append({
                    'timestamp': ts,
                    'scanner_id': scanner,
                    'incident': 'scanner_avoidance',
                    'product': prod
                })
        # Product swap: barcode for one product, RFID/camera for another at same time
        for bprod in barcode_products:
            for rprod in rfid_products:
                if bprod != rprod:
                    incidents.append({
                        'timestamp': ts,
                        'scanner_id': scanner,
                        'incident': 'product_swap',
                        'barcode': bprod,
                        'actual': rprod
                    })
        # Unscanned item: RFID/camera product not in scanned_products
        for prod in rfid_products:
            if (scanner, prod) not in scanned_products:
                incidents.append({
                    'timestamp': ts,
                    'scanner_id': scanner,
                    'incident': 'unscanned_item',
                    'product': prod
                })
    return incidents

if __name__ == '__main__':
    events = load_events('c:\\Users\\tt8445\\Documents\\GitHub\\linkedin\\retail_events.json')
    features = extract_features(events)
    incidents = detect_incidents(features)
    print(f"Detected {len(incidents)} incidents.")
    for inc in incidents[:5]:
        print(inc)
    # Save to output file
    with open('output/incident_log.json', 'w') as f:
        json.dump([{
            **i,
            'timestamp': i['timestamp'].isoformat() + 'Z' if hasattr(i['timestamp'], 'isoformat') else str(i['timestamp'])
        } for i in incidents], f, indent=2)

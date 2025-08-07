import json
from datetime import datetime
from typing import List, Dict, Any

def load_incidents(path: str) -> List[Dict[str, Any]]:
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

def match_incidents(detected: List[Dict[str, Any]], ground: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Match by timestamp, scanner_id, and incident type
    detected_set = set((i['timestamp'], i.get('scanner_id'), i['incident']) for i in detected)
    ground_set = set((i['timestamp'], i.get('scanner_id'), i['incident']) for i in ground)
    true_positives = detected_set & ground_set
    false_positives = detected_set - ground_set
    false_negatives = ground_set - detected_set
    return {
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'precision': len(true_positives) / (len(true_positives) + len(false_positives) + 1e-9),
        'recall': len(true_positives) / (len(true_positives) + len(false_negatives) + 1e-9),
        'f1': 2 * len(true_positives) / (2 * len(true_positives) + len(false_positives) + len(false_negatives) + 1e-9)
    }

if __name__ == '__main__':
    detected = load_incidents('output/incident_log.json')
    ground = load_incidents('incident_log.json')
    report = match_incidents(detected, ground)
    print(f"True Positives: {len(report['true_positives'])}")
    print(f"False Positives: {len(report['false_positives'])}")
    print(f"False Negatives: {len(report['false_negatives'])}")
    print(f"Precision: {report['precision']:.2f}")
    print(f"Recall: {report['recall']:.2f}")
    print(f"F1 Score: {report['f1']:.2f}")
    # Print details for review
    print("\nSample True Positives:")
    for tp in list(report['true_positives'])[:5]:
        print(tp)
    print("\nSample False Positives:")
    for fp in list(report['false_positives'])[:5]:
        print(fp)
    print("\nSample False Negatives:")
    for fn in list(report['false_negatives'])[:5]:
        print(fn)

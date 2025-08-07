import pandas as pd
import json
from collections import Counter
from sklearn.metrics import precision_score, recall_score, f1_score

def load_detected(path):
    df = pd.read_csv(path)
    # Normalize columns for matching
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    df['incident'] = df['incident'].astype(str)
    df['scanner_id'] = df['scanner_id'].astype(str)
    df['product'] = df.get('product', pd.Series(['']*len(df))).astype(str)
    return df

def load_ground_truth(path):
    with open(path, 'r') as f:
        gt = json.load(f)
    # Normalize for matching
    for i in gt:
        i['timestamp'] = pd.to_datetime(i['timestamp']).strftime('%Y-%m-%dT%H:%M:%SZ')
        i['incident'] = str(i['incident'])
        i['scanner_id'] = str(i['scanner_id'])
        i['product'] = str(i.get('product', ''))
    return gt

def match_incidents(detected, ground_truth):
    # Match by timestamp, scanner_id, incident, product
    detected_set = set((row['timestamp'], row['scanner_id'], row['incident'], row['product']) for _, row in detected.iterrows())
    gt_set = set((i['timestamp'], i['scanner_id'], i['incident'], i['product']) for i in ground_truth)
    tp = detected_set & gt_set
    fp = detected_set - gt_set
    fn = gt_set - detected_set
    return tp, fp, fn

def report(tp, fp, fn):
    print(f"True Positives: {len(tp)}")
    print(f"False Positives: {len(fp)}")
    print(f"False Negatives: {len(fn)}")
    precision = len(tp) / (len(tp) + len(fp)) if (len(tp) + len(fp)) > 0 else 0
    recall = len(tp) / (len(tp) + len(fn)) if (len(tp) + len(fn)) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    print(f"Precision: {precision:.2f}")
    print(f"Recall: {recall:.2f}")
    print(f"F1 Score: {f1:.2f}")

if __name__ == "__main__":
    detected_path = "incidents-results-4.csv"
    ground_truth_path = "incident_log.json"
    detected = load_detected(detected_path)
    ground_truth = load_ground_truth(ground_truth_path)
    tp, fp, fn = match_incidents(detected, ground_truth)
    report(tp, fp, fn)

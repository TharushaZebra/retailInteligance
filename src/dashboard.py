import streamlit as st
import pandas as pd
import joblib
import requests
from datetime import datetime
from feature_extraction import extract_features

st.set_page_config(page_title="Retail Incident Intelligence Dashboard", layout="wide")
st.title("Retail Incident Intelligence Dashboard")

MODEL_PATH = 'output/xgboost_best_model.joblib'
API_URL = 'http://localhost:8000/validate'

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

st.sidebar.header("Validation Data Upload")
uploaded_file = st.sidebar.file_uploader("Upload validation dataset (JSON)", type=["json"])

if uploaded_file:
    raw_events = pd.read_json(uploaded_file)
    st.write("### Uploaded Events", raw_events.head())
    # Feature engineering automation
    # 1. Extract features
    features = extract_features(raw_events.to_dict(orient="records"))
    df = pd.DataFrame(features)
    # 2. Session-level aggregation (as in feature_engineering.py)
    session_features = df.groupby('scanner_id').agg({
        'event_type': 'count',
        'product_id': 'nunique',
        'queue_length': 'mean',
        'equipment_status': lambda x: (x == 'failure').sum(),
    }).reset_index()
    session_features.columns = ['scanner_id', 'event_count', 'unique_products', 'avg_queue_length', 'failures']
    # 3. Merge session features
    df = df.merge(session_features, on='scanner_id', how='left')
    # 4. Encode categorical columns to numeric
    X = df.drop(['timestamp'], axis=1, errors='ignore')
    for col in X.select_dtypes(include=['object']).columns:
        X[col] = X[col].astype('category').cat.codes
    # 5. Check for required features
    required_features = ['event_type', 'scanner_id', 'product_id', 'barcode_data', 'rfid_tag', 'camera_label', 'queue_length', 'equipment_status', 'event_count', 'unique_products', 'avg_queue_length', 'failures']
    missing_features = [f for f in required_features if f not in X.columns]
    if missing_features:
        st.error(f"Missing required features for model: {missing_features}. Please ensure your data includes all necessary columns.")
    else:
        # Predict incidents (ML)
        preds = model.predict(X)
        ml_incidents = df.iloc[preds == 1].copy()
        def infer_incident(row):
            if row.get('equipment_status') == 'failure':
                return 'scanner_failure'
            if row.get('queue_length', 0) >= 8:
                return 'queue_buildup'
            if row.get('event_type') == 'rfid_read' and row.get('product_id'):
                return 'unscanned_item'
            if row.get('event_type') == 'camera_image' and row.get('product_id'):
                return 'scanner_avoidance'
            return 'incident'
        ml_incidents['incident'] = ml_incidents.apply(infer_incident, axis=1)
        if 'product_id' in ml_incidents.columns:
            ml_incidents = ml_incidents.rename(columns={'product_id': 'product'})
        # Rule-based detection
        rule_incidents = []
        # Product swap: barcode != actual
        if 'barcode_data' in df.columns and 'actual' in df.columns:
            swaps = df[(df['barcode_data'] != df['actual']) & df['barcode_data'].notnull() & df['actual'].notnull()]
            for _, row in swaps.iterrows():
                rule_incidents.append({
                    'timestamp': row['timestamp'],
                    'scanner_id': row['scanner_id'],
                    'incident': 'product_swap',
                    'barcode': row['barcode_data'],
                    'actual': row['actual']
                })
        # Queue buildup: queue_length >= 8
        if 'queue_length' in df.columns:
            buildups = df[df['queue_length'] >= 8]
            for _, row in buildups.iterrows():
                rule_incidents.append({
                    'timestamp': row['timestamp'],
                    'scanner_id': row['scanner_id'],
                    'incident': 'queue_buildup',
                    'queue_length': row['queue_length']
                })
        # Scanner avoidance: camera_image with product_id
        if 'event_type' in df.columns and 'product_id' in df.columns:
            avoid = df[(df['event_type'] == 'camera_image') & df['product_id'].notnull()]
            for _, row in avoid.iterrows():
                rule_incidents.append({
                    'timestamp': row['timestamp'],
                    'scanner_id': row['scanner_id'],
                    'incident': 'scanner_avoidance',
                    'product': row['product_id']
                })
        # Scanner failure: equipment_status == 'failure'
        if 'equipment_status' in df.columns:
            failures = df[df['equipment_status'] == 'failure']
            for _, row in failures.iterrows():
                rule_incidents.append({
                    'timestamp': row['timestamp'],
                    'scanner_id': row['scanner_id'],
                    'incident': 'scanner_failure'
                })
        # Combine ML and rule-based incidents
        columns_to_show = ['timestamp', 'scanner_id', 'incident', 'product', 'queue_length', 'barcode', 'actual']
        all_incidents = pd.concat([
            ml_incidents[ml_incidents.columns.intersection(columns_to_show)],
            pd.DataFrame(rule_incidents)
        ], ignore_index=True)
        display_cols = all_incidents.columns.intersection(columns_to_show)
        st.write("### Detected Incidents", all_incidents[display_cols].fillna(''))
        st.metric("Total Incidents", len(all_incidents))
        st.download_button("Download Incidents as CSV", all_incidents[display_cols].fillna('').to_csv(index=False), "incidents.csv")

st.sidebar.header("Live Validation (API)")
live_json = st.sidebar.text_area("Paste live event JSON array here")
if st.sidebar.button("Validate Live Data") and live_json:
    try:
        # Parse and feature engineer live events
        live_events = pd.read_json(live_json)
        features = extract_features(live_events.to_dict(orient="records"))
        df = pd.DataFrame(features)
        session_features = df.groupby('scanner_id').agg({
            'event_type': 'count',
            'product_id': 'nunique',
            'queue_length': 'mean',
            'equipment_status': lambda x: (x == 'failure').sum(),
        }).reset_index()
        session_features.columns = ['scanner_id', 'event_count', 'unique_products', 'avg_queue_length', 'failures']
        df = df.merge(session_features, on='scanner_id', how='left')
        # Encode categorical columns to numeric
        X = df.drop(['timestamp'], axis=1, errors='ignore')
        for col in X.select_dtypes(include=['object']).columns:
            X[col] = X[col].astype('category').cat.codes
        # Check for required features
        required_features = ['event_type', 'scanner_id', 'product_id', 'barcode_data', 'rfid_tag', 'camera_label', 'queue_length', 'equipment_status', 'event_count', 'unique_products', 'avg_queue_length', 'failures']
        missing_features = [f for f in required_features if f not in X.columns]
        if missing_features:
            st.error(f"Missing required features for model: {missing_features}. Please ensure your live data includes all necessary columns.")
        else:
            # Send engineered features to API
            response = requests.post(API_URL, json={"events": df.to_dict(orient="records")})
            result = response.json()
            st.write("### Live Detected Incidents", pd.DataFrame(result['incidents']))
            st.metric("Live Total Incidents", result['count'])
    except Exception as e:
        st.error(f"API error: {e}")

st.sidebar.info("Model used: output/xgboost_best_model.joblib")

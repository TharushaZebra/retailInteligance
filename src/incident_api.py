from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import List, Dict, Any
import joblib
import pandas as pd
import uvicorn
from datetime import datetime

# Load model
model = joblib.load('output/xgboost_best_model.joblib')

app = FastAPI()

class Event(BaseModel):
    event_name: str
    timestamp: str
    # Add other fields as needed (product_id, etc.)
    # ...

class EventsRequest(BaseModel):
    events: List[Event]

@app.post('/validate')
def validate_events(request: EventsRequest):
    # Convert to DataFrame
    df = pd.DataFrame([e.dict() for e in request.events])
    # Preprocess timestamps robustly
    def safe_parse_timestamp(x):
        if isinstance(x, str):
            try:
                return datetime.fromisoformat(x.replace('Z', ''))
            except Exception:
                return None
        elif isinstance(x, datetime):
            return x
        else:
            return None
    df['timestamp'] = df['timestamp'].apply(safe_parse_timestamp)
    # Encode categorical columns to numeric
    X = df.drop(['event_name', 'timestamp'], axis=1, errors='ignore')
    for col in X.select_dtypes(include=['object']).columns:
        X[col] = X[col].astype('category').cat.codes
    # Predict incidents
    preds = model.predict(X)
    incidents = []
    for i, pred in enumerate(preds):
        if pred == 1:
            incidents.append({
                'event_name': df.iloc[i]['event_name'],
                'timestamp': df.iloc[i]['timestamp'].isoformat() if df.iloc[i]['timestamp'] else None
            })
    return {'incidents': incidents, 'count': len(incidents)}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

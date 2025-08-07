import json
import pandas as pd

from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import resample
import joblib

DATA_PATH = 'output/ml_training_data_advanced.json'

# Load advanced training data
df = pd.read_json(DATA_PATH)

# Oversample incident class
majority = df[df['incident_label'] == 0]
minority = df[df['incident_label'] == 1]
minority_upsampled = resample(minority, replace=True, n_samples=len(majority), random_state=42)
df_balanced = pd.concat([majority, minority_upsampled])

# Prepare features and labels
features = ['event_type', 'scanner_id', 'product_id', 'barcode_data', 'rfid_tag', 'camera_label', 'queue_length', 'equipment_status', 'event_count', 'unique_products', 'avg_queue_length', 'failures']
for col in features:
    if df_balanced[col].dtype == 'O':
        df_balanced[col] = df_balanced[col].astype(str)
        df_balanced[col] = pd.factorize(df_balanced[col])[0]
X = df_balanced[features]
y = df_balanced['incident_label']


# K-fold cross-validation
from sklearn.model_selection import StratifiedKFold
import numpy as np
kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
metrics = []
for fold, (train_idx, test_idx) in enumerate(kf.split(X, y)):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    clf = XGBClassifier(use_label_encoder=False, eval_metric='logloss', scale_pos_weight=1)
    clf.fit(X_train, y_train)
    # Save the last fold's model as model 2
    if fold == kf.get_n_splits(X, y) - 1:
        joblib.dump(clf, 'output/xgboost_model2.joblib')
        print('Model 2 saved to output/xgboost_model2.joblib')
    y_pred = clf.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)
    metrics.append(report['weighted avg'])
    print(f"Fold {fold+1}:")
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(cm)

# Log average metrics
avg_metrics = {k: np.mean([m[k] for m in metrics]) for k in metrics[0]}
print("\nAverage cross-validation metrics (weighted avg):")
for k, v in avg_metrics.items():
    print(f"{k}: {v:.3f}")

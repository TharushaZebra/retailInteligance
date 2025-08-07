import json
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn.metrics import classification_report
from sklearn.utils import resample
import numpy as np

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

# Grid search parameters
param_grid = {
    'n_estimators': [50, 100],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.2],
    'subsample': [0.8, 1.0],
    'colsample_bytree': [0.8, 1.0]
}

clf = XGBClassifier(use_label_encoder=False, eval_metric='logloss', scale_pos_weight=1)
kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
gs = GridSearchCV(clf, param_grid, cv=kf, scoring='f1_weighted', verbose=2, n_jobs=-1)
gs.fit(X, y)

print(f"Best parameters: {gs.best_params_}")
print(f"Best cross-validation F1 score: {gs.best_score_:.3f}")

# Log classification report for best estimator
y_pred = gs.predict(X)
print(classification_report(y, y_pred))

# Save the best model
import joblib
joblib.dump(gs.best_estimator_, 'output/xgboost_best_model.joblib')
print("Best model saved to output/xgboost_best_model.joblib")

import json
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder

DATA_PATH = 'output/ml_training_data.json'

# Load labeled data
with open(DATA_PATH, 'r') as f:
    data = json.load(f)

# Convert to DataFrame
# Drop timestamp for ML, encode categorical features
features = ['event_type', 'scanner_id', 'product_id', 'barcode_data', 'rfid_tag', 'camera_label', 'queue_length', 'equipment_status']
df = pd.DataFrame(data)


# Fill missing values: 'missing' for categorical, -1 for numeric
for col in features:
    if col == 'queue_length':
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(-1)
    else:
        df[col] = df[col].fillna('missing')

# Encode categorical features
encoders = {}
for col in ['event_type', 'scanner_id', 'product_id', 'barcode_data', 'rfid_tag', 'camera_label', 'equipment_status']:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    encoders[col] = le

# Prepare X and y
X = df[features]
y = df['incident_label']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# Train Random Forest with class_weight='balanced'
clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
clf.fit(X_train, y_train)

# Predict and validate
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))


# Feature importance
importances = clf.feature_importances_
print("Feature importances:")
for feat, imp in zip(features, importances):
    print(f"{feat}: {imp:.3f}")

# Confusion matrix for director-level validation
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(cm)

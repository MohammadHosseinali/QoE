import sqlite3
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, mean_squared_error, r2_score
import joblib
import sys

db_path = 'db.sqlite'
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM results;", conn)
conn.close()

# Clean and convert signal values to numerical
def clean_signal_value(value):
    import re
    match = re.search(r"-?\d+", value)
    return float(match.group(0)) if match else None

for col in ['RSSI', 'SINR', 'RSRQ', 'RSRP']:
    df[col] = df[col].apply(clean_signal_value)

# Define MOS classes (1 to 5 based on the thresholds)
def mos_to_class(mos):
    if mos < 1:
        return 1
    elif mos < 2:
        return 2
    elif mos < 3:
        return 3
    elif mos < 4:
        return 4
    else:
        return 5

df['MOS_Class'] = df['MOS'].apply(mos_to_class)

# Features and target
X = df[['RSSI', 'SINR', 'RSRQ', 'RSRP']]
y = df['MOS_Class']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=543)

# Train a Decision Tree Classifier
if 'DT' in sys.argv:
    classifier = DecisionTreeClassifier(random_state=42)
elif 'RF' in sys.argv:
    classifier = RandomForestClassifier(random_state=42)
elif 'LR' in sys.argv:
    classifier = LogisticRegression(random_state=42, max_iter=1000, multi_class='multinomial', solver='lbfgs')

classifier.fit(X_train, y_train)

# Test the model
y_pred = classifier.predict(X_test)

print(classification_report(y_test, y_pred))

joblib.dump(classifier, 'decision_tree_model.pkl')




r2 = r2_score(y_test, y_pred)

rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"R² Score: {r2}")
print(f"RMSE: {rmse}")
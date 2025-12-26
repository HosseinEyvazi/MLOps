import joblib
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

# 1. Load Data
data = fetch_california_housing(as_frame=True)
df = data.frame

# 2. SELECT ONLY THE 3 FEATURES YOU USE IN THE APP
# The order here MUST match the order in app.py: [med_inc, house_age, ave_rooms]
selected_features = ['MedInc', 'HouseAge', 'AveRooms']
X = df[selected_features]
y = data.target

print(f"Training data shape: {X.shape}") 
# Should be (20640, 3) -> This fixes your error!

# 3. Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Create Pipeline
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42))
])

# 5. Train
print("Training new 3-feature model...")
pipeline.fit(X_train, y_train)

# 6. Save as a DICTIONARY (to match your app's robust logic)
# We save it as a dict so your app's "Case B" logic works perfectly.
artifact = {
    "model": pipeline,
    "features": selected_features,
    "description": "Reduced model using only Income, Age, and Rooms"
}

joblib.dump(artifact, "california_housing_model.pkl")
print("✅ Success! Overwrote 'california_housing_model.pkl' with the new compatible model.")

import joblib
import numpy as np
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# 1. Initialize FastAPI App
app = FastAPI()

# 2. Setup Templates Directory
templates = Jinja2Templates(directory="templates")

# 3. Robust Model Loading Logic
MODEL_PATH = "california_housing_model.pkl"
model = None

print("--------------------------------------------------")
if os.path.exists(MODEL_PATH):
    try:
        # Load the artifact
        artifact = joblib.load(MODEL_PATH)
        print(f"📂 Artifact Loaded. Type: {type(artifact)}")

        # CASE A: The artifact IS the model (has a predict method)
        if hasattr(artifact, "predict"):
            model = artifact
            print("✅ Model loaded successfully (Direct Object).")

        # CASE B: The artifact is a DICTIONARY (What you have now)
        elif isinstance(artifact, dict):
            print(f"ℹ️  Artifact is a Dictionary. Keys found: {list(artifact.keys())}")
            
            # Auto-detect common key names
            if "model" in artifact:
                model = artifact["model"]
                print("✅ Found key 'model'. Model loaded.")
            elif "pipeline" in artifact:
                model = artifact["pipeline"]
                print("✅ Found key 'pipeline'. Model loaded.")
            elif "regressor" in artifact:
                model = artifact["regressor"]
                print("✅ Found key 'regressor'. Model loaded.")
            else:
                print("❌ ERROR: Could not find a known key ('model', 'pipeline') in the dictionary.")
                print("👉 PLEASE READ THE KEYS PRINTED ABOVE AND UPDATE THE CODE.")
        
        else:
            print("❌ ERROR: Artifact is neither a model nor a dictionary.")

    except Exception as e:
        print(f"❌ Critical Error loading model: {e}")
else:
    print(f"⚠️ Warning: {MODEL_PATH} not found.")
print("--------------------------------------------------")


# --- Route 1: Home Page (GET /) ---
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# --- Route 2: Prediction Endpoint (GET /predict) ---
@app.get("/predict", response_class=HTMLResponse)
async def predict(
    request: Request,
    med_inc: float,
    house_age: float,
    ave_rooms: float
):
    # Check if model loaded correctly
    if model is None:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error_message": "Server Error: Model could not be loaded. Check terminal logs."
        })

    # Prepare Data
    input_data = np.array([[med_inc, house_age, ave_rooms]])

    try:
        # Make Prediction
        prediction = model.predict(input_data)
        result_value = round(prediction[0], 2)
        result_text = f"${result_value}k"
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error_message": f"Prediction Error: {str(e)}"
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "prediction_text": result_text,
        "med_inc": med_inc,
        "house_age": house_age,
        "ave_rooms": ave_rooms
    })

# --- RUN BUTTON SUPPORT ---
if __name__ == "__main__":
    # This allows you to press "Run" in VS Code
    uvicorn.run(app, host="127.0.0.1", port=8000)

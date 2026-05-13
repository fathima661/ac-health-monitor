import os
import joblib
import numpy as np
import pandas as pd
from collections import deque

# ==========================================
# Paths
# ==========================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_DIR = os.path.join(BASE_DIR, "model")

MODEL_PATH = os.path.join(MODEL_DIR, "model_final.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler_final.pkl")
FEATURES_PATH = os.path.join(MODEL_DIR, "features_final.pkl")
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder_final.pkl")

# ==========================================
# Load Artifacts
# ==========================================

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
features = joblib.load(FEATURES_PATH)
label_encoder = joblib.load(LABEL_ENCODER_PATH)

# ==========================================
# Rolling History
# ==========================================

TEMP_HISTORY = deque(maxlen=5)
VIB_HISTORY = deque(maxlen=5)

# ==========================================
# Severity Mapping
# ==========================================

SEVERITY_MAP = {
    "NORMAL": 0,
    "WARNING": 1,
    "CRITICAL": 2
}


# ==========================================
# Sensor Status Logic
# ==========================================

def temperature_status(temp):
    if temp > 42:
        return "CRITICAL"
    elif temp > 36:
        return "WARNING"
    return "NORMAL"


def humidity_status(humidity):
    if humidity > 98:
        return "CRITICAL"
    elif humidity > 95:
        return "WARNING"
    return "NORMAL"


def vibration_status(vibration):
    if vibration > 10:
        return "CRITICAL"
    elif vibration > 2:
        return "WARNING"
    return "NORMAL"


# ==========================================
# Feature Engineering
# ==========================================

def calculate_features(temperature, humidity, vibration):

    TEMP_HISTORY.append(temperature)
    VIB_HISTORY.append(vibration)

    vib_roll_mean = np.mean(VIB_HISTORY)
    temp_roll_mean = np.mean(TEMP_HISTORY)

    vib_slope = 0
    temp_slope = 0
    vib_acceleration = 0

    if len(VIB_HISTORY) >= 2:
        vib_slope = VIB_HISTORY[-1] - VIB_HISTORY[-2]

    if len(TEMP_HISTORY) >= 2:
        temp_slope = TEMP_HISTORY[-1] - TEMP_HISTORY[-2]

    if len(VIB_HISTORY) >= 3:
        vib_acceleration = (
            VIB_HISTORY[-1]
            - 2 * VIB_HISTORY[-2]
            + VIB_HISTORY[-3]
        )

    data = {
        "Vibration": vibration,
        "Temperature": temperature,
        "Humidity": humidity,
        "vib_roll_mean": vib_roll_mean,
        "temp_roll_mean": temp_roll_mean,
        "vib_slope": vib_slope,
        "temp_slope": temp_slope,
        "vib_acceleration": vib_acceleration
    }

    return pd.DataFrame([data])


# ==========================================
# Main Prediction Function
# ==========================================

def predict_system(temperature, humidity, vibration):

    # --------------------------------------
    # Sensor Status
    # --------------------------------------

    temp_status = temperature_status(temperature)
    hum_status = humidity_status(humidity)
    vib_status = vibration_status(vibration)

    sensor_states = [
        temp_status,
        hum_status,
        vib_status
    ]

    # --------------------------------------
    # Feature Engineering
    # --------------------------------------

    df = calculate_features(
        temperature,
        humidity,
        vibration
    )

    X = df[features]

    X_scaled = scaler.transform(X)

    # --------------------------------------
    # ML Prediction
    # --------------------------------------

    prediction_encoded = model.predict(X_scaled)[0]

    prediction = label_encoder.inverse_transform(
        [prediction_encoded]
    )[0]

    # --------------------------------------
    # Risk Score
    # --------------------------------------

    probabilities = model.predict_proba(X_scaled)[0]

    risk_score = float(np.max(probabilities) * 100)

    # --------------------------------------
    # Hybrid Logic
    # --------------------------------------

    all_states = sensor_states + [prediction]

    final_status = max(
        all_states,
        key=lambda x: SEVERITY_MAP[x]
    )

    # --------------------------------------
    # Reasoning
    # --------------------------------------

    reasons = []

    if temp_status == "CRITICAL":
        reasons.append("Extreme compressor temperature detected")
    elif temp_status == "WARNING":
        reasons.append("Temperature level elevated")

    if hum_status == "CRITICAL":
        reasons.append("Critical humidity level detected")
    elif hum_status == "WARNING":
        reasons.append("Humidity level elevated")

    if vib_status == "CRITICAL":
        reasons.append("Severe compressor vibration detected")
    elif vib_status == "WARNING":
        reasons.append("Abnormal vibration trend detected")

    reason = " | ".join(reasons)

    # --------------------------------------
    # Final Output
    # --------------------------------------

    return {
        "sensor_values": {
            "temperature": temperature,
            "humidity": humidity,
            "vibration": vibration
        },

        "sensor_status": {
            "temperature_status": temp_status,
            "humidity_status": hum_status,
            "vibration_status": vib_status
        },

        "ml_prediction": prediction,

        "risk_score": round(risk_score, 2),

        "final_status": final_status,

        "reason": reason
    }
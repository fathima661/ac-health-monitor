import joblib
import numpy as np
import pandas as pd
import os
import logging

# ----------------------------
# Logging (IMPORTANT for production)
# ----------------------------
logger = logging.getLogger(__name__)

# ----------------------------
# Paths
# ----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "model", "anomaly_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "model", "scaler.pkl")

# ----------------------------
# Safe model loading
# ----------------------------
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
except Exception as e:
    logger.error(f"Model loading failed: {e}")
    raise RuntimeError("Model or scaler missing/corrupted")

# ----------------------------
# Configurable thresholds (NO HARDCODE)
# ----------------------------
VIB_MIN = float(os.getenv("VIB_MIN", 0.2))
VIB_MAX = float(os.getenv("VIB_MAX", 20))
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", 3))


def predict_ac_status(temp, hum, vib, history):
    """
    Production-grade AC anomaly prediction
    """

    try:
        # ----------------------------
        # 1. Validation
        # ----------------------------
        if temp is None or vib is None:
            return {
                "state": "ERROR",
                "prediction": None,
                "score": None,
                "reason": "Missing values"
            }

        if np.isnan(temp) or np.isnan(vib):
            return {
                "state": "ERROR",
                "prediction": None,
                "score": None,
                "reason": "NaN detected"
            }

        # ----------------------------
        # 2. OFF detection
        # ----------------------------
        if vib == 0:
            #history.clear()
            return {
                "state": "OFF",
                "prediction": None,
                "score": None,
                "reason": "No vibration → AC OFF"
            }

        # ----------------------------
        # 3. Noise filtering (CONFIG BASED)
        # ----------------------------
        if vib < VIB_MIN or vib > VIB_MAX:
            return {
                "state": "INVALID",
                "prediction": None,
                "score": None,
                "reason": "Sensor noise / out of range"
            }

        # ----------------------------
        # 4. Store history (SAFE LIMIT)
        # ----------------------------
        history.append((temp, vib))

        if len(history) > WINDOW_SIZE:
            history.pop(0)

        if len(history) < WINDOW_SIZE:
            return {
                "state": "WARMUP",
                "prediction": None,
                "score": None,
                "reason": "Collecting enough data"
            }

        temps = [t for t, _ in history]
        vibs = [v for _, v in history]

        # ----------------------------
        # 5. Feature Engineering
        # ----------------------------
        temp_roll = np.mean(temps)
        vib_roll = np.mean(vibs)

        temp_diff = temps[-1] - temps[-2]
        vib_diff = vibs[-1] - vibs[-2]

        X = pd.DataFrame([{
            "temperature": temp,
            "vibration": vib,
            "temp_roll": temp_roll,
            "vib_roll": vib_roll,
            "temp_diff": temp_diff,
            "vib_diff": vib_diff
        }])

        # ----------------------------
        # 6. Scaling + Prediction (SAFE)
        # ----------------------------
        X_scaled = scaler.transform(X)

        pred = model.predict(X_scaled)[0]
        score = float(model.decision_function(X_scaled)[0])

        # ----------------------------
        # 7. Explanation (IMPROVED)
        # ----------------------------
        reason = "Normal operation"

        if abs(vib_diff) > 0.5:
            reason = "Sudden vibration spike detected"
        elif abs(temp_diff) > 2:
            reason = "Temperature fluctuation detected"
        elif pred == -1:
            reason = "Pattern deviates from normal behavior"

        return {
            "state": "RUNNING",
            "prediction": "NORMAL" if pred == 1 else "ANOMALY",
            "score": score,
            "reason": reason
        }

    except Exception as e:
        logger.error(f"Prediction failure: {e}")
        return {
            "state": "ERROR",
            "prediction": None,
            "score": None,
            "reason": "Internal prediction error"
        }
from fastapi import FastAPI, HTTPException, Request, Header
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from app.services.predict import predict_ac_status
import logging
import redis
import json
import os
from fastapi.middleware.cors import CORSMiddleware
from time import time

last_call = {}

# ----------------------------
# Environment & Auth Setup
# ----------------------------
API_KEY = os.getenv("API_KEY", "supersecret123")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_TTL = int(os.getenv("REDIS_TTL", 3600))
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", 3))

# ----------------------------
# Logging (File + Console)
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ----------------------------
# App Init
# ----------------------------
app = FastAPI(title="AC Predict API Production", version="1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Redis Setup (Hardened)
# ----------------------------
try:
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,
        socket_timeout=2,
        socket_connect_timeout=2
    )
    r.ping()
    logger.info("Redis connected securely")
except Exception as e:
    logger.error(f"Redis connection failed: {e}")
    raise RuntimeError("Redis is required for production")

# ----------------------------
# Schemas
# ----------------------------
class SensorInput(BaseModel):
    device_id: str = Field(..., min_length=1)
    temperature: float = Field(..., ge=0, le=100)
    humidity: float = Field(..., ge=0, le=100)
    vibration: float = Field(..., ge=0, le=100)

class PredictionResponse(BaseModel):
    timestamp: str
    device_id: str
    temperature: float
    humidity: float
    vibration: float
    state: str | None
    prediction: str | None
    score: float | None
    reason: str | None

# ----------------------------
# Helpers
# ----------------------------
def verify_api_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized device")

def redis_key(device_id): return f"ac_history:{device_id}"
def latest_key(device_id): return f"latest:{device_id}"

def get_history(device_id):
    try:
        data = r.get(redis_key(device_id))
        return json.loads(data) if data else []
    except Exception as e:
        logger.error(f"Redis read error: {e}")
        return []

def save_history(device_id, history):
    try:
        history = history[-WINDOW_SIZE:]
        r.setex(redis_key(device_id), REDIS_TTL, json.dumps(history))
    except Exception as e:
        logger.error(f"Redis write error: {e}")

def send_alert(device_id, result):
    # This is where you'd hook into Email/SMS/WhatsApp APIs later
    logger.warning(f"🚨 ALERT: {device_id} → {result.get('reason')}")

# ----------------------------
# Endpoints
# ----------------------------

@app.get("/health")
def health():
    return {"status": "ok", "redis": "connected"}

@app.get("/latest/{device_id}", response_model=PredictionResponse)
def get_latest(device_id: str):
    data = r.get(latest_key(device_id))
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    return json.loads(data)

@app.post("/ingest")
def ingest(data: SensorInput, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    try:
        history = get_history(data.device_id)
        result = predict_ac_status(
            data.temperature,
            data.humidity,
            data.vibration,
            history
        )
        save_history(data.device_id, history)

        latest_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_id": data.device_id,
            "temperature": data.temperature,
            "humidity": data.humidity,
            "vibration": data.vibration,
            "state": result.get("state"),
            "prediction": result.get("prediction"),
            "score": result.get("score"),
            "reason": result.get("reason")
        }

        r.set(latest_key(data.device_id), json.dumps(latest_payload))

        if result.get("prediction") == "ANOMALY":
            send_alert(data.device_id, result)

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"[{data.device_id}] Ingest failed: {e}")
        raise HTTPException(status_code=500, detail="Ingest error")

@app.post("/predict", response_model=PredictionResponse)
def predict(data: SensorInput):
    """Keep this for manual UI testing/interaction"""
    
    try:
        history = get_history(data.device_id)
        result = predict_ac_status(
            data.temperature,
            data.humidity,
            data.vibration,
            history
        )
        save_history(data.device_id, history)

        latest_payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "device_id": data.device_id,
            "temperature": data.temperature,
            "humidity": data.humidity,
            "vibration": data.vibration,
            "state": result.get("state"),
            "prediction": result.get("prediction"),
            "score": result.get("score"),
            "reason": result.get("reason")
        }
        
        r.set(latest_key(data.device_id), json.dumps(latest_payload))
        return PredictionResponse(**latest_payload)
    except Exception as e:
        logger.error(f"[{data.device_id}] Prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Prediction error")

@app.get("/")
def home():
    return {"message": "AC Predict Production API is online"}


@app.get("/favicon.ico")
def favicon():
    return {}
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.services.predict import predict_system

app = FastAPI(
    title="AC Predict API",
    version="1.0.0"
)

# ==========================================
# Templates
# ==========================================

templates = Jinja2Templates(directory="app/templates")

# ==========================================
# Request Model
# ==========================================

class SensorInput(BaseModel):
    temperature: float
    humidity: float
    vibration: float


# ==========================================
# Frontend Route
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


# ==========================================
# Prediction API
# ==========================================

@app.post("/predict")
async def predict(data: SensorInput):

    result = predict_system(
        temperature=data.temperature,
        humidity=data.humidity,
        vibration=data.vibration
    )

    return result
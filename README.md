# ⚡ AC Health Monitor

### IoT-Based Predictive Maintenance System with Machine Learning

An end-to-end **IoT + AI-powered predictive maintenance system** designed to monitor the health of air conditioning units using real-time sensor data and detect anomalies before failure occurs.

This project integrates **hardware (ESP8266 + sensors + solar power)** with a **Machine Learning backend** and a **real-time dashboard**, enabling intelligent and proactive maintenance.

---

## 🚀 Overview

Traditional maintenance systems are reactive, addressing issues only after failure. This project implements a **predictive maintenance approach**, where sensor data is continuously collected, analyzed, and used to detect abnormal patterns.

The system combines:

* 🔌 IoT hardware (ESP8266 + sensors)
* ☀️ Solar-powered system
* ☁️ Cloud data logging (ThingSpeak)
* 🧠 Machine Learning (Isolation Forest)
* ⚡ FastAPI backend
* 🌐 Interactive dashboard

---

## 🎯 Objectives

* Monitor AC performance in real time
* Detect anomalies before system failure
* Reduce maintenance cost and downtime
* Build a scalable IoT-based monitoring system
* Apply Machine Learning for predictive analysis

---

# 🔌 Hardware Setup

## Components Used

* ESP8266 NodeMCU
* DHT11 Sensor (Temperature & Humidity)
* SW-420 Vibration Sensor
* Solar Panel
* Solar Power Management Module
* 3.7V Li-ion Battery

---

## ⚙️ Physical Build

* Junction box used to safely house ESP8266 and power module
* PVC conduit pipes used for wire protection and organization
* CAT6 cable used for extending sensor connections
* Separate casing used to house:

  * SW-420 vibration sensor
  * DHT11 sensor

---

## ⚡ Power Flow Diagram

```
☀️ Solar Panel
      ↓
⚡ Power Module
      ↓
🔋 Battery
      ↓
📡 ESP8266
      ↓
🌡 Sensors
```

---

# 🧭 System Architecture (Visual)

```
        ┌──────────────┐
        │  Sensors     │
        │ Temp / Vib   │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │  ESP8266     │
        │ (WiFi Node)  │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ ThingSpeak   │
        │ Cloud Storage│
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ FastAPI      │
        │ Backend      │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ ML Model     │
        │ Isolation    │
        │ Forest       │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ Dashboard UI │
        └──────────────┘
```

---

# 🔄 System Flow

```
Sensors → ESP8266 → ThingSpeak → Backend → ML → Dashboard
```

### Step-by-step Flow

1. Sensors collect temperature, humidity, and vibration
2. ESP8266 sends data via WiFi
3. Data stored in ThingSpeak cloud
4. Backend retrieves data
5. ML model analyzes patterns
6. Dashboard displays system health

---

# 📊 Dataset Description

## Fields

* Temperature (°C) – from DHT11
* Humidity (%) – from DHT11
* Vibration – from SW-420
* Status – system condition label

---

## ⚠️ Important Note on Status Field

The **Status field is generated using predefined thresholds**, which leads to biased labeling.

### Threshold Logic

| Sensor      | Normal | Warning | Critical |
| ----------- | ------ | ------- | -------- |
| Temperature | ≤ 35°C | 35–40°C | > 40°C   |
| Humidity    | ≤ 60%  | 60–70%  | > 70%    |
| Vibration   | ≤ 1.5  | 1.5–3   | > 3      |

---

## 🚨 Limitation

* Majority of data points labeled **Critical**
* Dataset is **imbalanced**
* Not suitable for supervised learning

---

## ✅ Approach Used

* Ignore Status field
* Use **Isolation Forest (unsupervised ML)**
* Detect anomalies using behavior patterns

---

## 🔍 Special Condition

```
Vibration = 0 → AC is OFF
```

Handled separately in backend logic.

---

# 🧠 Machine Learning Model

## Algorithm Used

* Isolation Forest

## Why Isolation Forest?

* Works without labeled data
* Efficient for anomaly detection
* Suitable for real-time systems

---

## 🔍 Feature Engineering

* `temperature`
* `vibration`
* `temp_roll`
* `vib_roll`
* `temp_diff`
* `vib_diff`

---

# ⚙️ Backend System

* Built using FastAPI

### Handles:

* Data ingestion
* Prediction
* API responses

### Uses Redis for:

* Temporary storage
* Maintaining sensor history

---

# 🌐 Frontend Dashboard

### Features

* Real-time sensor monitoring
* System status display
* Live temperature graph
* ML confidence bar
* Manual & live modes

---

# 🔄 System States

| State    | Description                |
| -------- | -------------------------- |
| OFF      | AC is not running          |
| WARMUP   | Initial data collection    |
| RUNNING  | Normal operation           |
| WARNING  | Performance degrading      |
| CRITICAL | Immediate attention needed |
| INVALID  | Sensor noise               |

---

# 🛠 Tech Stack

### Hardware

* ESP8266 NodeMCU
* DHT11 Sensor
* SW-420 Sensor
* Solar Power System

### Backend

* Python
* FastAPI
* Redis

### Machine Learning

* Scikit-learn
* NumPy
* Pandas

### Frontend

* HTML / CSS / JavaScript
* Chart.js

---

# 📁 Project Structure

```
AC_PREDICT/
│
├── app/
│   ├── main.py
│   └── services/
│       └── predict.py
│
├── model/
│   ├── anomaly_model.pkl
│   └── scaler.pkl
│
├── frontend/
│   └── index.html
│
├── .env
├── .gitignore
└── README.md
```

---

# ▶️ How to Run

```
git clone https://github.com/fathima661/ac-health-monitor.git
cd ac-health-monitor

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

redis-server

uvicorn app.main:app --reload
```

Open:

```
frontend/index.html
```

---

# 📸 Screenshots

Add images here:

```
assets/dashboard.png  
assets/hardware.jpg  
```

---

# 🎤 Viva Explanation (Use this)

“This project is an IoT-based predictive maintenance system for AC units.
We use sensors connected to ESP8266 to collect real-time data.
Data is sent to the cloud and processed using a FastAPI backend.

Since labeled data was unreliable, we used Isolation Forest for anomaly detection.
The system detects abnormal behavior and displays results in a real-time dashboard.”

---

# ⚠️ Limitations

* Humidity not used in ML model
* Confidence score is approximate
* Uses polling instead of real-time streaming

---

# 🚀 Future Enhancements

* WebSocket real-time updates
* Explainable AI
* SMS / Email alerts
* Cloud deployment
* Model retraining

---

# 👨‍💻 Contributors

* Harinarayanan M
* Nithin N
* Fathima Shaji

---

# 📜 License

For academic and research purposes only.

---

# ⭐ Conclusion

This project demonstrates a **complete real-world integration of IoT and Machine Learning** to enable predictive maintenance and intelligent monitoring systems.

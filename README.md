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

## 🔌 Hardware Setup

### Components Used

* ESP8266 NodeMCU (WiFi microcontroller)
* DHT11 Sensor (Temperature & Humidity)
* SW-420 Vibration Sensor
* Solar Panel
* Solar Power Management Module
* 3.7V Li-ion Battery

---

### ⚙️ Physical Build

* Junction box used to safely house ESP8266 and power module
* PVC conduit pipes used for wire protection and organization
* CAT6 cable used for extending sensor connections
* Separate casing used to house:

  * SW-420 vibration sensor
  * DHT11 temperature & humidity sensor

---

### ⚡ Power Flow

Solar Panel → Power Module → Battery → ESP8266 → Sensors

---

## 🔄 System Architecture

```
Sensors → ESP8266 → ThingSpeak → FastAPI Backend → ML Model → Dashboard
```

### Data Flow Explanation

1. Sensors collect real-time data
2. ESP8266 processes and sends data via WiFi
3. Data is uploaded to ThingSpeak cloud
4. Backend retrieves and processes data
5. ML model performs anomaly detection
6. Results are displayed on dashboard

---

## 📊 Dataset Description

### Fields

* Temperature (°C) – from DHT11
* Humidity (%) – from DHT11
* Vibration – from SW-420 sensor
* Status – system condition label

---

### ⚠️ Important Note on Status Field

The **Status field is generated using predefined thresholds**, which leads to biased labeling.

#### Threshold Logic:

| Sensor      | Normal | Warning | Critical |
| ----------- | ------ | ------- | -------- |
| Temperature | ≤ 35°C | 35–40°C | > 40°C   |
| Humidity    | ≤ 60%  | 60–70%  | > 70%    |
| Vibration   | ≤ 1.5  | 1.5–3   | > 3      |

---

### 🚨 Limitation

* Majority of data points labeled as **Critical**
* Dataset is **imbalanced**
* Not suitable for supervised learning

---

### ✅ Approach Used

* Ignore the **Status field**
* Use **unsupervised learning (Isolation Forest)**
* Detect anomalies based on patterns instead of labels

---

### 🔍 Special Condition

* **Vibration = 0 → AC is OFF**
* Handled separately in system logic

---

### 📡 Data Source

* ESP8266 NodeMCU
* DHT11 Sensor
* SW-420 Sensor
* Data logged using ThingSpeak

---

## 🧠 Machine Learning Model

### Algorithm Used

* Isolation Forest

### Why Isolation Forest?

* Works without labeled data
* Efficient for anomaly detection
* Suitable for real-time systems

---

## 🔍 Feature Engineering

The model uses time-based features:

* `temperature`
* `vibration`
* `temp_roll` (rolling average)
* `vib_roll` (rolling average)
* `temp_diff` (rate of change)
* `vib_diff` (rate of change)

---

## ⚙️ Backend System

* Built using FastAPI

* Handles:

  * Data ingestion
  * Prediction
  * API responses

* Uses Redis for:

  * Temporary storage
  * Maintaining sensor history

---

## 🌐 Frontend Dashboard

Features:

* Real-time sensor monitoring
* System status display (Normal / Warning / Critical)
* Live temperature graph
* ML confidence indicator
* Manual & live modes

---

## 🔄 System States

| State    | Description                  |
| -------- | ---------------------------- |
| OFF      | AC is not running            |
| WARMUP   | Initial data collection      |
| RUNNING  | Normal operation             |
| WARNING  | Performance degrading        |
| CRITICAL | Immediate attention required |
| INVALID  | Sensor noise                 |

---

## 🛠 Tech Stack

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

## 📁 Project Structure

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

## ▶️ How to Run

### 1. Clone repo

```
git clone https://github.com/fathima661/ac-health-monitor.git
cd ac-health-monitor
```

### 2. Create virtual environment

```
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Run Redis

```
redis-server
```

### 5. Start backend

```
uvicorn app.main:app --reload
```

### 6. Open dashboard

Open `frontend/index.html`

---

## ⚠️ Limitations

* Humidity not included in ML model
* Confidence score is heuristic
* Uses polling instead of real-time streaming

---

## 🚀 Future Enhancements

* Explainable AI (reason for anomaly)
* WebSocket real-time updates
* Alert system (SMS / Email / WhatsApp)
* Cloud deployment
* Auto model retraining

---

## 📸 Screenshots

*Add your system images here*

---

## 👨‍💻 Contributors

* Harinarayanan M
* Nithin N
* Fathima Shaji

---

## 📜 License

For academic and research purposes only.

---

## ⭐ Conclusion

This project demonstrates a **real-world application of IoT and Machine Learning** in predictive maintenance. By integrating hardware, cloud communication, and intelligent analytics, the system provides a scalable solution for monitoring and maintaining AC systems efficiently.

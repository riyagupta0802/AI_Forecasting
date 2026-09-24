# NETORACLE

**AI-Based Network Attack Forecasting & Early Warning System**

An intelligent cybersecurity operations platform that analyzes network traffic flow telemetry to detect cyberattack anomalies and forecast multi-stage attack escalation.

## Project Details

- **Problem Title:** AI based Network Attack Forecasting from Network Traffic Data
- **Theme:** Blockchain & Cybersecurity
- **Category:** Software
- **Team:** HEX HIVE

## System Flow

**Network Traffic Data → Pattern Analysis → Data Processing → AI/ML Models → Attack & Transition Forecasting → Early Warning & Action**

NETORACLE is an advanced AI-based cybersecurity early-warning and network attack forecasting system. Unlike traditional Intrusion Detection Systems (IDS) that mainly provide reactive alerts, NETORACLE aims to go beyond detection:

1. **Analyze** incoming network flow telemetry.
2. **Detect** suspicious anomalous patterns.
3. **Classify** underlying attack types (`BENIGN`, `PortScan`, `Bot`, `DDoS`).
4. **Predict & Forecast** probable next attack stages using Cyber Kill Chain progression dynamics.
5. **Estimate** confidence and calibrated threat risk levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
6. **Provide** proactive early warnings and actionable mitigation advisories.

---

## Current Status: Phase 6 Completed

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Architecture, FastAPI backend, React+Vite SPA, bilingual i18n | ✅ Completed |
| **Phase 2** | SOC Cybersecurity Dashboard UI, 7 core pages, telemetry, bilingual toggle | ✅ Completed |
| **Phase 3** | FastAPI Backend + Frontend API integration | ✅ Completed |
| **Phase 4** | CICIDS2017 dataset + preprocessing pipeline | ✅ Completed |
| **Phase 5** | AI-Based Network Attack Detection using Random Forest (99% Accuracy) | ✅ Completed |
| **Phase 6** | Real Attack Forecasting using Multi-Class Stage Classifier + Empirical Transition Dynamics (98% Accuracy) | ✅ Completed |

---

## Phase 6: Real Attack Forecasting

Phase 6 implements genuine network attack stage forecasting connected directly to the Phase 5 detection pipeline:

```text
Network Traffic Flow Telemetry
            ↓
Preprocessing & Feature Normalization (78 features)
            ↓
Phase 5 Binary Attack Detection (BENIGN vs ATTACK)
            ↓
Phase 6 Multi-Class Stage Classification (BENIGN, PortScan, Bot, DDoS)
            ↓
Cyber Kill Chain State Transition Forecaster (Empirical Markov Transition Matrix)
            ↓
Predicted Next Attack Stage, Calibrated Confidence, Risk Level & Trajectory
            ↓
HEX HIVE SOC Dashboard (AttackForecastCard)
```

### Dataset & Feature Information

- **Dataset:** CICIDS2017 flow summary sample (`ml/data/sample/cicids2017_sample.csv`)
- **Records:** 500 network flows
- **Feature Space:** 78 continuous numerical flow features (Flow Duration, Total Fwd/Bwd Packets, Flow Bytes/s, Flow IAT Mean/Std/Max/Min, Packet Length Variance, Flag Counts, etc.)
- **Target Classes:**
  - `0: BENIGN` (290 samples) — Baseline operational traffic
  - `1: Bot` (40 samples) — C2 Botnet infection & staging
  - `2: DDoS` (110 samples) — Volumetric denial-of-service flood
  - `3: PortScan` (60 samples) — Reconnaissance & vulnerability probing
- **Temporal Characteristics & Limitations:**
  The available 500-sample dataset represents flow-level summary aggregates without a wall-clock timestamp column. Rather than fabricating artificial temporal timestamps, the system implements the strongest defensible forecasting baseline: a trained 98%-accurate Multi-Class Stage Classifier paired with empirical Cyber Kill Chain state transition dynamics. The modular architecture is designed to ingest 3D sequence tensors `(batch_size, timesteps, features)` for future LSTM/GRU integration.

### Machine Learning Models & Evaluated Metrics

- **Stage Classifier Architecture:** `RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)`
- **Evaluation Split:** Stratified 80/20 train/test split ($N=400$ training, $N=100$ held-out test)
- **Held-Out Test Set Performance (`ml/models/forecast_metrics.json`):**
  - **Overall Accuracy:** `98.00%`
  - **Macro Precision:** `99.17%`
  - **Macro Recall:** `93.75%`
  - **Macro F1-Score:** `96.00%`
  - **Per-Class Metrics:**
    - `BENIGN`: Precision 96.67%, Recall 100%, F1 98.31% (Support: 58)
    - `Bot`: Precision 100%, Recall 75%, F1 85.71% (Support: 8)
    - `DDoS`: Precision 100%, Recall 100%, F1 100% (Support: 22)
    - `PortScan`: Precision 100%, Recall 100%, F1 100% (Support: 12)
  - **Confusion Matrix:**
    $$\begin{bmatrix} 58 & 0 & 0 & 0 \\ 2 & 6 & 0 & 0 \\ 0 & 0 & 22 & 0 \\ 0 & 0 & 0 & 12 \end{bmatrix}$$

### Transition Progression Mapping

- `BENIGN` $\to$ Stays `BENIGN` (88%) or alerts on early `PortScan` probe (12%) $\to$ **LOW RISK**
- `PortScan` (Reconnaissance) $\to$ Forecasts `Bot` C2 Staging (55%) or `DDoS` (35%) $\to$ **HIGH RISK**
- `Bot` (C2 Staging) $\to$ Forecasts `DDoS` Volumetric Flood (72%) or sustained Botnet (20%) $\to$ **CRITICAL RISK**
- `DDoS` (Execution) $\to$ Forecasts mitigation return to `BENIGN` (65%) or sustained flood (35%) $\to$ **LOW RISK**

---

## API Endpoints

### Phase 6 Forecasting Endpoints

- `GET /api/forecast/status` — Returns active ML forecast, identified state, projected next stage, confidence, risk level, trajectory nodes, and limitations.
- `GET /api/forecast/metrics` — Returns real test-set evaluation metrics (Accuracy, Precision, Recall, F1, Confusion Matrix, Top Features).
- `POST /api/forecast/predict` — Executes end-to-end detection and forecasting for a provided flow feature vector or preset sample (`benign`, `portscan`, `bot`, `ddos`).

### Existing Preserved Endpoints

- `GET /api/health` — Backend health check.
- `GET /api/system/status` — System architectural status.
- `GET /api/network/summary` — Network telemetry overview.
- `GET /api/traffic/sample` — Time-series packet flow telemetry.
- `GET /api/data/status` — Phase 4 dataset and preprocessing pipeline status.
- `GET /api/ml/status` — Phase 5 binary attack classifier status.
- `GET /api/ml/metrics` — Phase 5 binary classification evaluation metrics.
- `POST /api/ml/predict` — Phase 5 binary attack classification inference.

---

## How to Run Locally

### 1. Backend (FastAPI)

```bash
cd backend
# Activate virtual environment
.\.venv\Scripts\Activate.ps1
# Start Uvicorn server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev -- --port 5173
```

### 3. Retrain Forecasting Model

```bash
# In repository root
.\backend\.venv\Scripts\python.exe ml/forecasting/train.py
```
# NETORACLE

**AI-Based Network Attack Forecasting & Early Warning System**

An intelligent cybersecurity operations platform that analyzes network traffic flow telemetry to detect cyberattack anomalies, forecast multi-stage attack escalation, and estimate threat escalation windows.

## Project Details

- **Problem Title:** AI based Network Attack Forecasting from Network Traffic Data
- **Theme:** Blockchain & Cybersecurity
- **Category:** Software
- **Team:** HEX HIVE

## System Flow

**Network Traffic Data → Preprocessing → Attack Detection → Stage Forecasting → Time-to-Escalation → Early Warning & Action**

NETORACLE is an advanced AI-based cybersecurity early-warning and network attack forecasting system. Unlike traditional Intrusion Detection Systems (IDS) that mainly provide reactive alerts, NETORACLE aims to go beyond detection:

1. **Analyze** incoming network flow telemetry.
2. **Detect** suspicious anomalous patterns (`BENIGN` vs `ATTACK`).
3. **Classify** underlying multi-stage attack types (`BENIGN`, `PortScan`, `Bot`, `DDoS`).
4. **Predict & Forecast** probable next attack stages using Cyber Kill Chain progression dynamics.
5. **Estimate Time-to-Escalation** using real-time flow velocity calibration and supervised regression.
6. **Provide** calibrated threat risk levels (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`) and actionable early advisories.

---

## Current Status: Phase 7 Completed

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Architecture, FastAPI backend, React+Vite SPA, bilingual i18n | ✅ Completed |
| **Phase 2** | SOC Cybersecurity Dashboard UI, 7 core pages, telemetry, bilingual toggle | ✅ Completed |
| **Phase 3** | FastAPI Backend + Frontend API integration | ✅ Completed |
| **Phase 4** | CICIDS2017 dataset + preprocessing pipeline | ✅ Completed |
| **Phase 5** | AI-Based Network Attack Detection using Random Forest (99% Accuracy) | ✅ Completed |
| **Phase 6** | Real Attack Forecasting using Multi-Class Stage Classifier + Transition Dynamics (98% Accuracy) | ✅ Completed |
| **Phase 7** | Real Time-to-Escalation using Velocity-Calibrated Regression (MAE: 8.38s, R²: 0.9566) | ✅ Completed |

---

## Phase 6 & Phase 7 End-to-End Pipeline

```text
Network Traffic Flow Telemetry
            ↓
Preprocessing & Feature Normalization (78 features)
            ↓
Phase 5 Binary Attack Detection (BENIGN vs ATTACK) — 99.0% Accuracy
            ↓
Phase 6 Multi-Class Stage Classification (BENIGN, PortScan, Bot, DDoS) — 98.0% Accuracy
            ↓
Phase 6 Cyber Kill Chain Transition Forecaster (Empirical Markov Transition Matrix)
            ↓
Phase 7 Time-to-Escalation Engine (Telemetry Velocity Index + RandomForestRegressor)
            ↓
Calibrated Escalation Window (seconds/minutes), Threat Risk Level & Velocity Metric
            ↓
HEX HIVE SOC Dashboard (AttackForecastCard & AttackForecastPage)
```

---

## Phase 7: Real Time-to-Escalation

### Definition of Escalation
Escalation is defined as the transition from a lower-severity pre-attack condition to a higher-severity, higher-impact attack stage:
- **PortScan (Reconnaissance, Severity: Medium):** Escalates to `Bot` (C2 Foothold / Staging) or direct `DDoS` (Volumetric Flood).
- **Bot (C2 Staging, Severity: High):** Escalates to `DDoS` (Coordinated Botnet Flood Command Execution).
- **DDoS (Peak Severity: Critical):** Already at peak volumetric saturation; escalation time is `0s (Active Impact)`.
- **BENIGN (Severity: Low):** Regular operational baseline; status is `Not Escalating`.

### Temporal Data Characteristics & Methodology
- **Dataset Examined:** `ml/data/sample/cicids2017_sample.csv` (500 records $\times$ 78 continuous numerical features).
- **Available Temporal Telemetry:** Flow duration (`Flow Duration` in microseconds), inter-arrival time metrics (`Flow IAT Mean/Std/Max/Min`, `Fwd IAT`, `Bwd IAT`), packet rates (`Flow Packets/s`), byte velocities (`Flow Bytes/s`), and active/idle cycles.
- **Honest Limitations:** The 500-sample slice provides flow-level aggregates rather than a continuous multi-hour packet stream with wall-clock timestamps. Fabricating artificial timestamps would be scientifically invalid.
- **Implemented Methodology:** A supervised `RandomForestRegressor` trained on flow velocity and temporal features combined with a real-time **Telemetry Velocity Index** ($V$). When packet/byte velocity is elevated, the model shortens the projected escalation window; under stealthy/low-rate conditions, the window broadens.

### Supervised Escalation Model Metrics (`ml/models/escalation_metrics.json`)
- **Model Architecture:** `RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)`
- **Evaluation Split:** Stratified 80/20 train/test split ($N=400$ training, $N=100$ held-out test)
- **Held-out Test MAE (Mean Absolute Error):** **`8.38 seconds`**
- **Held-out Test RMSE:** **`33.83 seconds`**
- **$R^2$ Score:** **`0.9566`**
- **Top Predictive Features:** `Packet Length Variance`, `Max Packet Length`, `Fwd Packet Length Std/Min`, `Total Length of Fwd Packets`, `Average Packet Size`.

### Configurable Threat Risk Thresholds
- **CRITICAL:** $\le 60\text{ seconds}$ to escalation
- **HIGH:** $61\text{ to } 180\text{ seconds}$
- **MODERATE:** $181\text{ to } 360\text{ seconds}$
- **LOW:** $> 360\text{ seconds}$ or Not Escalating (BENIGN)

---

## API Endpoints

### Phase 7 Escalation Endpoints
- `GET /api/escalation/status` — Returns active threat escalation status, estimated seconds/minutes, formatted window, risk level, velocity index, and limitations.
- `GET /api/escalation/metrics` — Returns real evaluated test-set metrics (MAE: 8.38s, RMSE: 33.83s, $R^2$: 0.9566, top features, risk thresholds).
- `POST /api/escalation/predict` — Executes end-to-end Detection $\to$ Forecasting $\to$ Time-to-Escalation for a telemetry vector or sample preset (`benign`, `portscan`, `bot`, `ddos`).

### Phase 6 Forecasting Endpoints
- `GET /api/forecast/status` — Returns active ML forecast, identified state, projected next stage, confidence, risk level, trajectory nodes, and dynamic `time_to_escalation`.
- `GET /api/forecast/metrics` — Returns test metrics for stage classification (98% accuracy).
- `POST /api/forecast/predict` — Executes end-to-end detection and forecasting.

### Phase 1–5 Preserved Endpoints
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
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev -- --port 5173
```

### 3. Retrain Escalation Model

```bash
# In repository root
.\backend\.venv\Scripts\python.exe ml/escalation/train.py
```
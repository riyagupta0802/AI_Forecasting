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
Phase 8 Real Attack Story Engine (Event Correlation, Chronological Timeline & 5 SOC Answers)
            ↓
Phase 9 Real Early Warning Engine (Multi-Source Evidence, Decision Matrix & Alert Triage)
            ↓
HEX HIVE SOC Dashboard (EarlyWarningCard) & Dedicated Triage Page (EarlyWarningsPage)
```

---

## Phase 9: Real Early Warning Engine

### Purpose & Early Warning Definition
An Early Warning represents:
> *"Available evidence indicates an elevated or potentially escalating security condition that deserves attention."*  
> (It does not guarantee that a full breach has succeeded or that a future attack is absolute certainty.)

### Warning Decision Rules & Severity Matrix
Severity levels are derived deterministically from multi-source pipeline evidence:
- **CRITICAL (`VOLUMETRIC_DISRUPTION`):** Active volumetric denial-of-service (`DDoS`) targeting web endpoints (ports 80/443), OR imminent escalation ($\le 60\text{ seconds}$) with high velocity ($V \ge 1.5\text{x}$).
- **HIGH (`MALICIOUS_STAGING`):** Active command & control or botnet communication (`Bot`) targeting known C2 ports (6667, 4444), OR short escalation countdown ($61\text{s} - 180\text{s}$).
- **MEDIUM (`SUSPICIOUS_RECONNAISSANCE`):** Systematic multi-port reconnaissance probe (`PortScan`) across multiple endpoints, OR moderate escalation window ($181\text{s} - 360\text{s}$).
- **LOW (`POTENTIAL_ESCALATION`):** Anomalous flow telemetry detected with low velocity or an extended escalation window ($> 360\text{s}$).
- **INFO (`BASELINE_OBSERVATION`):** Operational baseline telemetry (`BENIGN`), no active intrusion indicators detected.

### Multi-Source Evidence Compilation
Every early warning is backed by four distinct, verifiable evidence vectors:
1. **Detection Evidence:** Binary prediction and confidence from Phase 5 Random Forest classifier.
2. **Forecast Evidence:** Identified stage and Kill Chain transition probability from Phase 6 model.
3. **Escalation Evidence:** Calibrated escalation window, velocity index, and risk level from Phase 7 regressor.
4. **Correlated Event Evidence:** Cluster count, target service ports, and TCP flags from Phase 8 correlator.

### Deduplication & Warning Lifecycle
- **Deduplication:** Alerts compute a cryptographic fingerprint hash based on warning type, severity, states, and target ports to eliminate repetitive alert spam.
- **Lifecycle:**
  - `NEW`: Initial alert generation for a novel threat condition.
  - `ACTIVE`: Persistent threat condition across telemetry intervals.
  - `RESOLVED`: Telemetry returns to normal `BENIGN` operational baseline.
- **Session History:** In-memory ring buffer (up to 50 alerts) enabling SOC analysts to audit alert progressions and lifecycle transitions.

### Scientific Limitations & Disclosures
Early warnings are synthesized from deterministic rules applied to empirical telemetry from the 500-sample CICIDS2017 aggregate dataset. Warnings indicate elevated security risk based on empirical patterns and do not claim absolute certainty. All limitations are explicitly disclosed on the dashboard.

---

## Phase 8: Real Attack Story & Event Correlation

### The 5 Core SOC Incident Questions Answered
1. **"What happened?"** — Initial detected network anomaly or operational baseline stability with real destination port targets.
2. **"What happened next?"** — Correlated multi-stage progression across destination ports and services.
3. **"What is happening now?"** — Current active threat posture classified by Phase 5 binary detection and stage identification.
4. **"What may happen next?"** — Machine learning Kill Chain progression forecasted by Phase 6 Markov/RF transition dynamics.
5. **"How is the threat escalating?"** — Calibrated time window until higher-severity escalation estimated by Phase 7 regressor.

### Correlation & Timeline Architecture
- **Normalized Events (`ml/attack_story/events.py`):** 500 flow records from `cicids2017_sample.csv` normalized into `NetworkSecurityEvent` dataclasses with real flow durations, packet counts, byte volumes, destination ports, TCP flags (`SYN`, `ACK`), and accumulated relative time offsets (`relative_time_s`).
- **Cluster Correlation (`ml/attack_story/correlation.py`):** `EventCorrelator` groups events into `CorrelatedAttackCluster` structures based on empirical intrusion category, service port groups (e.g. multi-port sweep for `PortScan`, IRC C2 on 6667 / Metasploit on 4444 for `Bot`, HTTP/HTTPS saturation for `DDoS`), and sequential continuity.
- **Chronological Timeline (`ml/attack_story/timeline.py`):** `ChronologicalTimelineBuilder` synthesizes `TimelineNode` milestones linking historical clusters, the active threat state, the Phase 6 forecast node, and the Phase 7 escalation window node.
- **Narrative Synthesis (`ml/attack_story/story.py`):** `AttackStoryEngine` composes the grounded SOC security incident narrative. Phrasing strictly adheres to evidence-grounded terminology (`observed`, `detected`, `correlated`, `forecasted`, `estimated`).

### Temporal Data Scope & Disclosed Limitations
The Attack Story engine operates exclusively on genuine flow telemetry from the 500-sample CICIDS2017 aggregate dataset. Temporal sequence offsets are accumulated deterministically from microsecond durations (`relative_time_s`). No synthetic wall-clock dates, fake IP addresses, or ungrounded attack stages are fabricated.

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

### Phase 9 Early Warning Endpoints
- `GET /api/warnings/status` — Returns warning engine readiness, active warning status, history count, and limitations.
- `GET /api/warnings` — Returns active early warnings, multi-source evidence breakdown, and session history with optional filters (`severity`, `warning_type`, `status`, `context`, `limit`).
- `POST /api/warnings/evaluate` — Evaluates current telemetry or scenario preset (`portscan`, `bot`, `ddos`, `benign`, `auto`) and returns actionable warning decision.

### Phase 8 Attack Story Endpoints
- `GET /api/attack-story/status` — Returns attack story readiness, ingested flow event count, cluster count, active posture, and limitations.
- `GET /api/attack-story` — Returns correlated event timeline, 5-question SOC incident narrative, cluster breakdowns, and flow telemetry with optional filters (`category`, `severity`, `context`, `limit`).
- `POST /api/attack-story/generate` — Generates an on-demand context-driven incident narrative and timeline for a specified threat context.

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
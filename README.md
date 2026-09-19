# HEX HIVE

**AI-Based Network Attack Forecasting & Early Warning System**

An intelligent cybersecurity operations platform that analyzes network traffic flow telemetry to detect cyberattack anomalies and forecast multi-stage attack escalation.

---

## System Flow

$$\text{Network Traffic} \longrightarrow \text{Data Processing} \longrightarrow \text{Random Forest Attack Detection} \longrightarrow \text{BENIGN / ATTACK} \longrightarrow \text{Dashboard}$$

---

## Current Status: Phase 5 Completed

### Completed Phases

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Architecture, FastAPI backend foundation, React+Vite SPA, initial bilingual i18n | ✅ Completed |
| **Phase 2** | SOC Cybersecurity Dashboard UI, 7 core pages, custom SVG telemetry, bilingual toggle | ✅ Completed |
| **Phase 3** | FastAPI Backend + Frontend API integration, `/api/system/status`, `/api/traffic/sample` | ✅ Completed |
| **Phase 4** | Network Traffic Dataset + Preprocessing Pipeline, `/api/data/status`, CICIDS2017 | ✅ Completed |
| **Phase 5** | AI-Based Network Attack Detection, Random Forest Classifier, Real Test Metrics, `/api/ml/*` | ✅ Completed |

---

## Phase 5: AI-Based Network Attack Detection

Phase 5 introduces active machine learning classification into HEX HIVE using a trained **RandomForestClassifier** to classify incoming network flow telemetry into **BENIGN** (normal) vs. **ATTACK** (malicious/suspicious).

### Architecture & Components

```
ml/
├── data/
│   ├── sample/
│   │   └── cicids2017_sample.csv   # Benchmark network flow data
│   └── processed/
│       ├── train_features.csv      # Scaled flow features (500 samples x 78 features)
│       ├── train_labels.csv        # Multi-class and binary mapped targets
│       └── preprocessing_meta.json # Scaler parameters and feature names
├── models/
│   ├── attack_classifier.joblib    # Serialized trained RandomForestClassifier
│   └── model_metrics.json          # Real test-set evaluation metrics & confusion matrix
├── predictions/
│   └── predict.py                  # High-performance AttackPredictor runtime engine
└── training/
    └── train.py                    # Stratified train/test split, training & evaluation runner
```

### Model Performance Metrics (Evaluated on Isolated Test Set, N=100)

All performance metrics are calculated on an isolated 20% test split ($N=100$) with a fixed seed (`random_state=42`) using real network flow data:

| Metric | Score | Note |
|---|---|---|
| **Accuracy** | **99.00%** | Overall correct classifications |
| **Precision** | **100.00%** | Zero false alarms ($FP=0$) |
| **Recall** | **97.62%** | 41 out of 42 attack vectors detected |
| **F1 Score** | **98.80%** | Harmonic mean of precision & recall |
| **ROC-AUC** | **0.9988** | High discriminative capability |

#### Confusion Matrix
- **True Negatives ($TN$):** `58` (Normal BENIGN traffic correctly identified)
- **False Positives ($FP$):** `0` (Zero false alarms on normal traffic)
- **False Negatives ($FN$):** `1` (Missed intrusion vector)
- **True Positives ($TP$):** `41` (Attacks correctly flagged)

### Running Training & Prediction

```powershell
# 1. Train and evaluate the Random Forest model:
python ml/training/train.py

# 2. Run standalone inference verification:
python ml/predictions/predict.py
```

---

## Backend API Endpoints

The FastAPI backend provides modular endpoints under `/api`:

| Method | Endpoint | Description | Phase |
|---|---|---|---|
| `GET` | `/api/health` | Health check (`status: "ok"`) | Phase 1 |
| `GET` | `/api/system/status` | System component status (`ml_model: "loaded"`) | Phase 3/5 |
| `GET` | `/api/network/summary` | Simulated telemetry summary metrics | Phase 3 |
| `GET` | `/api/forecast/status` | Attack forecasting placeholder (*Awaiting Model*) | Phase 3 |
| `GET` | `/api/traffic/sample` | Sample network traffic time-series points | Phase 3 |
| `GET` | `/api/data/status` | Dynamic dataset inventory & preprocessing state | Phase 4 |
| `GET` | `/api/ml/status` | Random Forest model availability & feature metadata | **Phase 5** |
| `GET` | `/api/ml/metrics` | Real test-set evaluation metrics & confusion matrix | **Phase 5** |
| `POST` | `/api/ml/predict` | Real-time binary attack detection inference | **Phase 5** |

### Example Response: `POST /api/ml/predict`

```json
{
  "prediction": "ATTACK",
  "is_attack": true,
  "confidence": 100.0,
  "probabilities": {
    "BENIGN": 0.0,
    "ATTACK": 1.0
  },
  "inference_latency_ms": 1.85,
  "model_type": "Random Forest",
  "features_evaluated": 78
}
```

---

## Getting Started

### Prerequisites
- **Node.js** (v18+) & **npm** (v9+)
- **Python** (v3.10+)

### Backend Setup (FastAPI)

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python -m venv .venv
     source .venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the development server:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

5. Access interactive Swagger API documentation at `http://127.0.0.1:8000/docs`.

### Frontend Setup (React + Vite)

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

4. Open your browser at `http://127.0.0.1:5173`.
   - Toggle language between **English** and **हिन्दी (Hindi)** with 100% dictionary parity.
   - Inspect the **AI Attack Detection** card to review real evaluated model metrics and test live classifications on benign vs. attack traffic flows.

---

## Roadmap

- **Phase 6:** Temporal Sequence Modeling (LSTM / GRU for next attack stage forecasting and time-to-escalation regression).
- **Phase 7:** Attack Story Correlation & Explainable AI (SHAP feature attribution).
- **Phase 8:** Real-time Packet Capture Ingestion & Production Security Hardening.

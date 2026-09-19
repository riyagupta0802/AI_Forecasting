# HEX HIVE

**Smart India Hackathon 2026**
- **Problem Title:** AI based Network Attack Forecasting from Network Traffic Data
- **Theme:** Blockchain & Cybersecurity
- **Category:** Software
- **Problem ID:** SIH26153

---

## Overview

**HEX HIVE** is an advanced AI-based cybersecurity early-warning and network attack forecasting system. Unlike traditional Intrusion Detection Systems (IDS) that only trigger reactive alerts when an attack is already in progress, HEX HIVE aims to go beyond detection:
1. **Analyze** incoming network flow telemetry.
2. **Detect** suspicious anomalous patterns.
3. **Classify** underlying attack types across multi-class distributions.
4. **Predict & Forecast** probable next attack stages.
5. **Estimate** critical time-to-escalation.
6. **Correlate** related security events into a coherent "Attack Story".
7. **Explain** model outputs via Explainable AI (XAI / SHAP).
8. **Provide** proactive early warnings and actionable mitigation advisories.

### System Flow

$$\text{Network Traffic Data} \longrightarrow \text{Pattern Analysis} \longrightarrow \text{Data Processing} \longrightarrow \text{AI / LSTM Models} \longrightarrow \text{Attack \& Time Prediction} \longrightarrow \text{Early Warning \& Action}$$

---

## Current Status: Phase 4 Completed

### Completed Phases

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Architecture, FastAPI backend foundation, React+Vite SPA, initial bilingual i18n | ✅ Completed |
| **Phase 2** | SOC Cybersecurity Dashboard UI, 7 core pages, custom SVG telemetry, bilingual toggle | ✅ Completed |
| **Phase 3** | FastAPI Backend + Frontend API integration, `/api/system/status`, `/api/traffic/sample` | ✅ Completed |
| **Phase 4** | Network Traffic Dataset + Data Preprocessing Pipeline, `/api/data/status`, CICIDS2017 | ✅ Completed |

---

## Phase 4: Network Traffic Dataset & Data Processing

Phase 4 establishes the automated dataset ingestion, cleaning, and preprocessing pipeline for HEX HIVE:

```
ml/
├── data/
│   ├── raw/                        # Raw PCAP dumps / large source datasets (not committed)
│   │   └── README.md
│   ├── sample/                     # Lightweight representative intrusion benchmark
│   │   └── cicids2017_sample.csv   # 500 records across BENIGN, DDoS, PortScan, Bot (79 flow columns)
│   └── processed/                  # Cleaned, scaled, ML-ready feature matrices
│       ├── train_features.csv      # 500 samples x 78 scaled continuous flow features
│       ├── train_labels.csv        # Encoded target attack classification labels (0..3)
│       └── preprocessing_meta.json # Scaler parameters, feature list, and class encodings
└── preprocessing/
    ├── data_loader.py              # Schema validation, path safety, column whitespace stripping
    ├── cleaner.py                  # Deduplication, inf replacement, NaN median imputation, X/y split
    ├── preprocessor.py             # Scikit-learn StandardScaler, LabelEncoder & JSON exporter
    └── preprocess.py               # Reproducible end-to-end CLI execution runner
```

### Dataset Characteristics (CICIDS2017)
- **Benchmark:** Canadian Institute for Cybersecurity CICIDS2017 flow data format.
- **Traffic Classes:**
  - `BENIGN`: Normal web, DNS, and encrypted traffic flows.
  - `DDoS`: High-volume packet floods with short inter-arrival times.
  - `PortScan`: Rapid sequential probing across destination ports with SYN flags.
  - `Bot`: Periodic command-and-control beaconing patterns.
- **Data Quality Corrections Handled:**
  - Standard CICIDS2017 column name whitespace stripping (`df.columns.str.strip()`).
  - Correction of infinite values (`np.inf` / `-np.inf` in `Flow Bytes/s` due to zero duration).
  - Missing value imputation using feature column medians (outlier-resilient).
  - Feature matrix ($X$) and target vector ($y$) separation without data leakage.

### Running the Preprocessing Pipeline

To execute the data processing pipeline and generate ML-ready artifacts:

```powershell
# From project root with virtual environment activated:
python ml/preprocessing/preprocess.py
```

Expected output:
```text
============================================================
HEX HIVE — Phase 4 Network Traffic Preprocessing Pipeline
============================================================
Input Dataset:  .../ml/data/sample/cicids2017_sample.csv
Output Directory: .../ml/data/processed
------------------------------------------------------------
Initial Records:        500
Duplicates Removed:     0
Infinite Values Fixed:  2
Missing Values Imputed: 4
Final Retained Records: 500
Total Clean Features:   78
------------------------------------------------------------
Saving processed data artifacts:
  [OK] Features saved to: train_features.csv (500 rows, 78 cols)
  [OK] Labels saved to:   train_labels.csv (500 rows)
  [OK] Metadata saved to: preprocessing_meta.json
------------------------------------------------------------
Detected Classes & Encoding:
  - BENIGN       (Code: 0) -> 290 instances
  - Bot          (Code: 1) -> 40 instances
  - DDoS         (Code: 2) -> 110 instances
  - PortScan     (Code: 3) -> 60 instances
============================================================
Phase 4 Preprocessing Pipeline COMPLETED SUCCESSFULLY!
============================================================
```

---

## Backend API Endpoints

The FastAPI backend exposes the following modular endpoints under `/api`:

| Method | Endpoint | Description | Phase |
|---|---|---|---|
| `GET` | `/api/health` | Service health status check | Phase 1 |
| `GET` | `/api/system/status` | System components runtime status | Phase 3 |
| `GET` | `/api/network/summary` | Simulated network telemetry summary metrics | Phase 3 |
| `GET` | `/api/forecast/status` | Attack forecasting engine status placeholder | Phase 3 |
| `GET` | `/api/traffic/sample` | Sample network traffic time-series data points | Phase 3 |
| `GET` | `/api/data/status` | Dynamic dataset inventory & preprocessing pipeline state | **Phase 4** |

### Example Response: `GET /api/data/status`

```json
{
  "status": "ready",
  "dataset": "CICIDS2017",
  "mode": "demo",
  "records_available": 500,
  "preprocessing": "ready",
  "processed_records": 500,
  "classes_detected": ["BENIGN", "Bot", "DDoS", "PortScan"]
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
   - Navigate to the **Network Traffic** view to inspect the live **Dataset & Preprocessing Status** card (`CICIDS2017`, `500` records, `78` clean features).

---

## Roadmap

- **Phase 5:** Attack Detection & Classification ML Models (RandomForest / XGBoost baseline).
- **Phase 6:** Temporal Sequence Modeling (LSTM / GRU for next-stage forecasting and time-to-escalation regression).
- **Phase 7:** Attack Story Correlation & Explainable AI (SHAP / XAI).
- **Phase 8:** Real-time Packet Capture Ingestion & Production Security Hardening.

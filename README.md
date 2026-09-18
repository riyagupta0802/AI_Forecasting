# HEX HIVE

**Smart India Hackathon 2026**
- **Problem Title:** AI based Network Attack Forecasting from Network Traffic Data
- **Theme:** Blockchain & Cybersecurity
- **Category:** Software
- **Project Code / ID:** SIH26153

---

## Overview

**HEX HIVE** is an advanced AI-based cybersecurity early-warning and network attack forecasting system. Unlike traditional Intrusion Detection Systems (IDS) that only detect attacks after or while they occur, HEX HIVE aims to go beyond detection:
1. **Analyze** incoming network traffic telemetry.
2. **Detect** suspicious anomalous patterns.
3. **Classify** underlying attack types.
4. **Predict & Forecast** probable next attack stages.
5. **Estimate** critical time-to-escalation.
6. **Correlate** related security events into a coherent "Attack Story".
7. **Explain** model outputs via Explainable AI (XAI / SHAP).
8. **Provide** proactive early warnings and actionable mitigation advisories.

### System Architecture Flow

```
Network Traffic Data
        ↓
Pattern Analysis & Feature Extraction
        ↓
Data Preprocessing Pipeline
        ↓
AI / Temporal LSTM & Ensemble Models
        ↓
Attack Stage & Time-to-Escalation Prediction
        ↓
Proactive Early Warning & Mitigation
```

---

## Phase 1 Scope (Current)

This repository contains the completed **Phase 1: Architecture & Foundation**:
- **Backend:** FastAPI modular application with CORS middleware, health checking (`GET /api/health`), and structured placeholders for future attack analysis routes and MongoDB integration.
- **Frontend:** React + Vite application with bilingual support (**English** and **Hindi / हिन्दी**), local persistence via `localStorage`, cybersecurity SaaS aesthetic, and connection diagnostics.
- **Machine Learning Layer:** Structured directory architecture ready for data ingestion, feature preprocessing, model definitions, training scripts, and inference pipelines.
- **Security & Configuration:** Environment variable-based configuration with `.env.example` templates, avoiding any hardcoded secrets.

*Note: In accordance with Phase 1 constraints, no ML models have been trained, no external datasets downloaded, and no active MongoDB connections initialized.*

---

## Directory Structure

```
HEX-HIVE/
│
├── frontend/
│   ├── src/
│   │   ├── assets/              # Static media assets & SVG logos
│   │   ├── components/          # Reusable UI components (Header, Badges, Switchers)
│   │   ├── pages/               # Application view pages
│   │   ├── layouts/             # Page structural layouts
│   │   ├── hooks/               # Custom React hooks (useLanguage)
│   │   ├── services/            # API communication services
│   │   ├── utils/               # App constants and helpers
│   │   ├── i18n/                # Localization dictionaries (en.js, hi.js, index.js)
│   │   ├── App.jsx              # Main App entry point
│   │   ├── main.jsx             # React DOM root render
│   │   └── index.css            # Cyber SaaS styling & design tokens
│   ├── .env.example             # Frontend environment variables template
│   ├── package.json             # Frontend dependencies & scripts
│   └── vite.config.js           # Vite build and dev server configuration
│
├── backend/
│   ├── app/
│   │   ├── core/                # Core configurations & settings
│   │   ├── routes/              # API route controllers (health, traffic, alerts, etc.)
│   │   ├── models/              # Database domain models (future MongoDB schemas)
│   │   ├── schemas/             # Pydantic request/response validation schemas
│   │   ├── services/            # Business & forecasting logic services
│   │   ├── utils/               # Helper utilities & logging
│   │   ├── db/                  # Database connectivity stub
│   │   └── main.py              # FastAPI entry point & middleware setup
│   ├── requirements.txt         # Python dependencies
│   └── .env.example             # Backend environment variables template
│
├── ml/
│   ├── data/                    # Dataset directory placeholder (CICIDS, etc.)
│   ├── preprocessing/           # Feature scaling, encodings, and pipeline scripts
│   ├── models/                  # Architecture definitions (LSTM, XGBoost, etc.)
│   ├── training/                # Training pipelines and loss tracking
│   └── predictions/             # Inference and forecasting engines
│
├── README.md                    # Project documentation
└── .gitignore                   # Git ignore specifications
```

---

## Getting Started

### Prerequisites
- **Node.js** (v18+) & **npm** (v9+)
- **Python** (v3.10+)

---

### Backend Setup (FastAPI)

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
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

4. Create environment file:
   ```bash
   cp .env.example .env
   ```

5. Run the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

6. Verify backend health endpoint:
   - URL: `http://localhost:8000/api/health`
   - Expected Response:
     ```json
     {
       "status": "ok",
       "project": "HEX HIVE"
     }
     ```

---

### Frontend Setup (React + Vite)

1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create environment file:
   ```bash
   cp .env.example .env
   ```

4. Start the Vite development server:
   ```bash
   npm run dev
   ```

5. Open your browser at `http://localhost:5173`.
   - Toggle language between **English** and **हिन्दी (Hindi)**.
   - Verify that your selection persists upon page refresh.
   - Inspect the backend connectivity card to confirm live communication with the FastAPI health endpoint.

---

## Future Phase Roadmap

- **Phase 2:** Dataset ingestion (e.g., CICIDS2017/2018), exploratory analysis, and network traffic packet feature extraction pipeline.
- **Phase 3:** Machine learning modeling — Multi-class attack classification (XGBoost/RandomForest) and temporal sequence prediction (LSTM/GRU).
- **Phase 4:** Time-to-escalation estimation, Attack Story event correlation, and SHAP explainability layer.
- **Phase 5:** MongoDB persistent store, real-time alerting, live telemetry feeds, and full interactive dashboard in both English and Hindi.


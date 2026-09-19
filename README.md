# NETORACLE

**AI-Based Network Attack Forecasting & Early Warning System**

An intelligent cybersecurity operations platform that analyzes network traffic flow telemetry to detect cyberattack anomalies and forecast multi-stage attack escalation.

## HackShastra

- **Problem Title:** AI based Network Attack Forecasting from Network Traffic Data
- **Theme:** Blockchain & Cybersecurity
- **Category:** Software
- **Team:** HEX HIVE

## System Flow

**Network Traffic Data → Pattern Analysis → Data Processing → AI/ML Models → Attack & Time Prediction → Early Warning & Action**

NETORACLE is an advanced AI-based cybersecurity early-warning and network attack forecasting system. Unlike traditional Intrusion Detection Systems (IDS) that mainly provide reactive alerts, NETORACLE aims to go beyond detection:

1. **Analyze** incoming network flow telemetry.
2. **Detect** suspicious anomalous patterns.
3. **Classify** underlying attack types.
4. **Predict & Forecast** probable next attack stages.
5. **Estimate** time-to-escalation.
6. **Correlate** related security events into an "Attack Story".
7. **Explain** model outputs using Explainable AI (XAI / SHAP).
8. **Provide** proactive early warnings and actionable mitigation advisories.

---

## Current Status: Phase 5 Completed

| Phase | Description | Status |
|---|---|---|
| **Phase 1** | Architecture, FastAPI backend, React+Vite SPA, bilingual i18n | ✅ Completed |
| **Phase 2** | SOC Cybersecurity Dashboard UI, 7 core pages, telemetry, bilingual toggle | ✅ Completed |
| **Phase 3** | FastAPI Backend + Frontend API integration | ✅ Completed |
| **Phase 4** | CICIDS2017 dataset + preprocessing pipeline | ✅ Completed |
| **Phase 5** | AI-Based Network Attack Detection using Random Forest | ✅ Completed |

---

## Phase 5: AI-Based Network Attack Detection

Phase 5 introduces active machine learning classification using a trained **RandomForestClassifier** to classify incoming network flow telemetry into:

- **BENIGN** — normal traffic
- **ATTACK** — malicious or suspicious traffic

### Architecture

```text
ml/
├── data/
│   ├── sample/
│   │   └── cicids2017_sample.csv
│   └── processed/
│       ├── train_features.csv
│       ├── train_labels.csv
│       └── preprocessing_meta.json
├── models/
│   ├── attack_classifier.joblib
│   └── model_metrics.json
├── predictions/
│   └── predict.py
└── training/
    └── train.py
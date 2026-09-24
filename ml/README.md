# HEX HIVE — Machine Learning & Forecasting Architecture

This directory contains the machine learning pipelines for network attack detection, progression forecasting, and time-to-escalation estimation in the HEX HIVE / NETORACLE platform.

## Directory Structure

```text
ml/
├── data/
│   ├── sample/
│   │   └── cicids2017_sample.csv       # 500-sample benchmark dataset
│   └── processed/
│       ├── train_features.csv          # 78 continuous numerical flow features
│       ├── train_labels.csv            # Encoded multi-class targets (0..3)
│       └── preprocessing_meta.json     # Normalization parameters & feature schema
├── preprocessing/
│   ├── data_loader.py                  # Dataset loading & format validation
│   ├── cleaner.py                      # Nan/Inf handling & deduplication
│   ├── preprocessor.py                 # StandardScaler & LabelEncoder
│   └── preprocess.py                   # Phase 4 end-to-end preprocessing runner
├── models/
│   ├── attack_classifier.joblib        # Phase 5 Binary Random Forest classifier (99% acc)
│   ├── model_metrics.json              # Phase 5 Binary test metrics
│   ├── forecast_stage_classifier.joblib# Phase 6 Multi-Class Random Forest classifier (98% acc)
│   ├── forecast_metrics.json           # Phase 6 Multi-Class test metrics & confusion matrix
│   ├── escalation_model.joblib         # Phase 7 Supervised Escalation Regressor (MAE: 8.38s)
│   └── escalation_metrics.json         # Phase 7 Regression metrics (MAE, RMSE, R²)
├── training/
│   └── train.py                        # Phase 5 Binary training script
├── predictions/
│   └── predict.py                      # Phase 5 Binary inference engine
├── forecasting/
│   ├── __init__.py                     # Module exports
│   ├── preprocessing.py                # Sequence tensor & tabular feature alignment
│   ├── model.py                        # AttackForecastingModel & Kill Chain transitions
│   ├── train.py                        # Phase 6 Multi-Class training script
│   └── predict.py                      # AttackForecaster end-to-end inference engine
├── escalation/
│   ├── __init__.py                     # Module exports
│   ├── preprocessing.py                # Temporal velocity feature extraction
│   ├── model.py                        # TimeToEscalationEngine & risk thresholds
│   ├── train.py                        # Phase 7 Supervised regression training script
│   └── predict.py                      # EscalationPredictor end-to-end inference engine
├── attack_story/
│   ├── __init__.py                     # Module exports
│   ├── events.py                       # NetworkSecurityEvent schema & dataset normalizer
│   ├── correlation.py                  # EventCorrelator & CorrelatedAttackCluster
│   ├── timeline.py                     # ChronologicalTimelineBuilder & TimelineNode
│   └── story.py                        # AttackStoryEngine (5 SOC questions synthesis)
└── warning/
    ├── __init__.py                     # Module exports
    ├── models.py                       # EarlyWarning & EvidenceItem dataclasses
    ├── rules.py                        # Deterministic severity matrix & decision logic
    ├── formatter.py                    # Title, message, and evidence text synthesizers
    └── engine.py                       # EarlyWarningEngine (Lifecycle & deduplication)
```

## Machine Learning Capabilities

### Phase 5 — Binary Attack Detection
- **Target:** Classify traffic into `BENIGN` (0) vs `ATTACK` (1).
- **Model:** `RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)`.
- **Test Metrics:** 99.0% Accuracy, 100% Precision, 97.6% Recall, 0.988 F1-Score, 0.9988 ROC-AUC.

### Phase 6 — Real Attack Forecasting
- **Pipeline:** Preprocessing $\to$ Phase 5 Binary Detection $\to$ Phase 6 Stage Classification $\to$ Kill Chain Transition Progression.
- **Classes:** `BENIGN` (0), `Bot` (1), `DDoS` (2), `PortScan` (3).
- **Stage Model:** `RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)`.
- **Test Metrics:** 98.0% Accuracy, 99.17% Macro Precision, 93.75% Macro Recall, 96.00% Macro F1.
- **Transition Forecaster:** Projects next probable stage, calibrated confidence, risk level, and visual trajectory based on empirical Cyber Kill Chain progression dynamics.

### Phase 7 — Real Time-to-Escalation
- **Pipeline:** Detection $\to$ Stage Forecasting $\to$ Flow Velocity Extraction $\to$ Escalation Window Estimation.
- **Model:** `RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)` + Dynamic Telemetry Velocity Index.
- **Test Metrics:** MAE: `8.38 seconds`, RMSE: `33.83 seconds`, $R^2$: `0.9566`.
- **Escalation Windows:**
  - `PortScan` $\to$ Reconnaissance to foothold: ~120s to 360s (velocity-modulated).
  - `Bot` $\to$ C2 staging to botnet flood: ~45s to 180s (velocity-modulated).
  - `DDoS` $\to$ 0s (Already at peak impact).
  - `BENIGN` $\to$ Not escalating (Baseline stable).

### Phase 8 — Real Attack Story & Event Correlation
- **Pipeline:** Flow Telemetry $\to$ Detection $\to$ Cluster Correlation $\to$ Kill Chain Timeline $\to$ Phase 6 Forecast $\to$ Phase 7 Escalation $\to$ 5 SOC Answers.
- **Data Grounding:** Real CICIDS2017 aggregate flow records (`cicids2017_sample.csv`). Relative timeline offsets derived deterministically from microsecond `Flow Duration` accumulations (`relative_time_s`) without synthetic dates or fabricated IP addresses.
- **Correlation Logic:**
  - `PortScan`: Multi-port sweep pattern across dynamic high ports (e.g. 22608, 10086, 17019, 30946).
  - `Bot`: Port 6667 (Standard IRC C2), Port 4444 (Metasploit default listener), Ports 8080/8000.
  - `DDoS`: Volumetric packet saturation targeting web server ports 80/443.
  - `BENIGN`: Standard baseline traffic on ports 80, 443, 8080, 22, 53.
- **Core Narrative Questions Answered:**
  1. *What happened?* (Initial detected anomaly or baseline stability)
  2. *What happened next?* (Correlated event progression across destination ports)
  3. *What is happening now?* (Current Phase 5 detected threat)
  4. *What may happen next?* (Phase 6 Kill Chain forecast transition)
  5. *How is the threat escalating?* (Phase 7 velocity-calibrated escalation window)

### Phase 9 — Real Early Warning Engine
- **Pipeline:** Detection $\to$ Forecasting $\to$ Escalation $\to$ Correlated Clusters $\to$ Decision Matrix $\to$ Deduplicated Warnings $\to$ Triage Evidence.
- **Evidence-Grounded Rules:**
  - `CRITICAL`: Active volumetric attack (`DDoS`) or imminent high-velocity escalation ($\le 60\text{s}, V \ge 1.5\text{x}$).
  - `HIGH`: Active botnet C2 staging (`Bot`) or short escalation countdown ($61\text{s} - 180\text{s}$).
  - `MEDIUM`: Systematic multi-port reconnaissance probe (`PortScan`) or moderate escalation ($181\text{s} - 360\text{s}$).
  - `LOW`: Low-velocity anomalous telemetry or extended escalation horizon ($> 360\text{s}$).
  - `INFO`: Normal baseline operational telemetry (`BENIGN`), zero active threats.
- **Deduplication:** Hash fingerprinting prevents repetitive alerting on unchanged threat conditions.
- **Lifecycle Tracking:** Manages alert transitions across `NEW`, `ACTIVE`, and `RESOLVED` states with an auditable in-memory session buffer.


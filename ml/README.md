# HEX HIVE — Machine Learning & Forecasting Architecture

This directory contains the machine learning pipelines for network attack detection and progression forecasting in the HEX HIVE / NETORACLE platform.

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
│   └── forecast_metrics.json           # Phase 6 Multi-Class test metrics & confusion matrix
├── training/
│   └── train.py                        # Phase 5 Binary training script
├── predictions/
│   └── predict.py                      # Phase 5 Binary inference engine
└── forecasting/
    ├── __init__.py                     # Module exports
    ├── preprocessing.py                # Sequence tensor & tabular feature alignment
    ├── model.py                        # AttackForecastingModel & Kill Chain transitions
    ├── train.py                        # Phase 6 Multi-Class training script
    └── predict.py                      # AttackForecaster end-to-end inference engine
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

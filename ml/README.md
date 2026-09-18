# HEX HIVE - Machine Learning Layer Architecture

This directory is designated for the AI/ML forecasting pipelines that will be developed in subsequent phases of the HEX HIVE project.

## Pipeline Lifecycle

```
ml/data/            Raw & Processed Network Traffic Datasets (e.g., CICIDS2017)
       ↓
ml/preprocessing/   Feature extraction, scaling, flow window generation, label encoding
       ↓
ml/models/          Neural architecture definitions (LSTM, GRU, XGBoost, Attention models)
       ↓
ml/training/        Model training loops, hyperparameter tuning, loss optimization & checkpoints
       ↓
ml/predictions/     Inference engines, attack sequence forecasting, escalation time estimation & SHAP
```

## Directory Structure Overview

- `data/`: Ingestion point for network packet captures (PCAP), flow records, and benchmark intrusion detection datasets.
- `preprocessing/`: Tokenizers, statistical extractors (packet rate, byte entropy, TCP flag distributions), and normalization scalers.
- `models/`: PyTorch & scikit-learn/XGBoost model definitions for multi-stage attack detection and sequence forecasting.
- `training/`: Training orchestration, cross-validation scripts, MLflow/logging integrations.
- `predictions/`: Real-time prediction services, time-to-escalation estimators, and Explainable AI (SHAP) explainers.

*Note: In Phase 1, this directory contains architectural blueprints only. No weights, datasets, or mock predictions are present.*


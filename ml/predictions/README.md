# Inference, Forecasting & Explainability

## Purpose
Contains the runtime inference pipelines called by the backend service to generate live attack forecasts and explainable insights.

## Future Components
1. **Forecasting Engine**:
   - Accepts windowed network features from live traffic.
   - Generates ranked probabilities of next possible attack stages.
   - Calculates time-to-escalation confidence intervals.
2. **Explainable AI (SHAP / TreeExplainer / Integrated Gradients)**:
   - Identifies the top network features (e.g., SYN flag flood, anomalous payload size, unusual destination port clustering) that caused the alert.
   - Translates model explanations into human-readable rationale for security analysts.


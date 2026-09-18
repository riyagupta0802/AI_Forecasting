# ML Model Architectures

## Purpose
Houses model class declarations, network definitions, and loss criteria.

## Planned Model Architectures (Phases 3+)
1. **Temporal Sequence Forecaster (LSTM / GRU / Transformer)**:
   - Evaluates consecutive network traffic windows to forecast the next probable attack state or transition.
2. **Attack Classifier (XGBoost / Random Forest)**:
   - High-precision classification of anomalous behaviors into specific intrusion classes.
3. **Escalation Regressor**:
   - Neural regression network estimating the estimated time (in seconds/minutes) before a reconnaissance event escalates into exfiltration or impact.


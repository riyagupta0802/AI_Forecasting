# Data Preprocessing & Feature Engineering

## Purpose
Contains the preprocessing pipelines responsible for converting raw network packet flows into structured feature matrices suitable for machine learning models.

## Future Components
1. **Flow Aggregator**: Aggregates raw packet captures into bidirectional flow features (duration, flow bytes/s, flow packets/s, inter-arrival times).
2. **Feature Scaler**: Robust and MinMax scalers to normalize continuous traffic metrics.
3. **Sequence Windowing**: Sliding window generator for temporal time-series models (e.g., sequences of length $T$ for LSTM input).
4. **Label Encoder**: Maps attack category labels to standardized multi-class IDs.


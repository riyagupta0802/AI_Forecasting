# NETORACLE Local Test Datasets

This directory contains standardized local benchmark datasets for NETORACLE network attack detection, forecasting, and explainability testing.

## Files

### `netoracle_demo_traffic.csv`
- **Description:** NETORACLE Local Test Dataset derived from the CICIDS2017 intrusion benchmark.
- **Records:** 500 flow telemetry records.
- **Features:** 78 continuous numerical features (Flow Duration, Fwd/Bwd Packet Statistics, Header Lengths, Flow Bytes/s, Packet Inter-Arrival Times, TCP Flags, Window Sizes).
- **Contents:** Input features only. Zero precomputed predictions, confidence scores, or labels.
- **Source Notice:** Sourced from standardized Canadian Institute for Cybersecurity (CIC) IDS 2017 flow data for offline local prototype validation.


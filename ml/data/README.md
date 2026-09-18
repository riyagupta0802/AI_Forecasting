# Network Traffic Data Directory

## Purpose
This directory stores network traffic datasets used for model training, validation, and benchmarking.

## Anticipated Datasets (Phases 2+)
- **CICIDS2017 / CSE-CIC-IDS2018**: Standard benchmark containing benign traffic along with real-world contemporary cyberattacks (Brute Force, DoS, DDoS, Web Attacks, Infiltration, Botnets, PortScan).
- **Custom PCAP / NetFlow captures**: Captured network packets for live forecasting evaluation.

## Storage Guidelines
- Raw source data files (.pcap, .csv, .parquet) should not be committed to version control.
- Ensure all datasets adhere to the `.gitignore` rules.


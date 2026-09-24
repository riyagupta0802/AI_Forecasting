"""Event Normalization and Data Ingestion for HEX HIVE Phase 8 Attack Story.

Extracts raw flow telemetry from the CICIDS2017 benchmark dataset and standardizes
each flow into an immutable NetworkSecurityEvent dataclass.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SAMPLE_CSV_PATH = REPO_ROOT / "ml" / "data" / "sample" / "cicids2017_sample.csv"

# Port to common service mappings for threat context enrichment
PORT_SERVICE_MAP = {
    80: "HTTP (Web Service)",
    443: "HTTPS (Encrypted Web)",
    22: "SSH (Secure Shell)",
    53: "DNS (Domain Resolution)",
    8080: "HTTP-Alt (Proxy / Web App)",
    8000: "HTTP-Dev (Web Application)",
    6667: "IRC (Standard Botnet C2)",
    4444: "Metasploit Default C2 Listener",
    21: "FTP (File Transfer)",
    3306: "MySQL Database",
    5432: "PostgreSQL Database",
}

SEVERITY_MAP = {
    "BENIGN": "LOW",
    "PortScan": "MEDIUM",
    "Bot": "HIGH",
    "DDoS": "CRITICAL",
}


@dataclass
class NetworkSecurityEvent:
    """Normalized security telemetry event derived from network flow observation."""

    event_id: str
    sequence_index: int
    destination_port: int
    service_name: str
    protocol: str
    duration_ms: float
    packet_count: int
    byte_count: int
    flow_packets_sec: float
    flow_bytes_sec: float
    syn_flag_count: int
    ack_flag_count: int
    attack_category: str
    severity: str
    relative_time_s: float
    description: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert event dataclass to dictionary."""
        return asdict(self)


def _resolve_service_name(port: int) -> str:
    """Resolve human-readable service identifier for a port number."""
    if port in PORT_SERVICE_MAP:
        return PORT_SERVICE_MAP[port]
    if port > 1024:
        return f"Port {port} (High / Dynamic Port)"
    return f"Port {port} (Well-Known Service)"


def _build_event_description(category: str, port: int, service: str, pkts: int, dur_ms: float) -> str:
    """Construct factual, evidence-based event description from flow metrics."""
    if category == "BENIGN":
        return f"Standard network flow to {service} with {pkts} packets over {dur_ms:.1f}ms."
    elif category == "PortScan":
        return f"Targeted probe packet dispatched to {service}; flow concluded in {dur_ms:.1f}ms."
    elif category == "Bot":
        return f"Persistent C2 heartbeat beaconing on {service} exchanging {pkts} packets."
    elif category == "DDoS":
        return f"High-velocity volumetric flood packet stream targeting {service} ({pkts} pkts)."
    return f"Flow to {service} with {pkts} packets."


def load_normalized_events(
    csv_path: Optional[Path] = None,
    limit: Optional[int] = None,
    category_filter: Optional[str] = None,
    severity_filter: Optional[str] = None,
) -> List[NetworkSecurityEvent]:
    """Ingest and normalize raw flow records into a sequence of NetworkSecurityEvent objects.

    Args:
        csv_path: Optional override path to dataset CSV.
        limit: Optional maximum number of events to load.
        category_filter: Optional filter ('BENIGN', 'PortScan', 'Bot', 'DDoS').
        severity_filter: Optional filter ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL').

    Returns:
        List of normalized NetworkSecurityEvent objects sorted by relative time offset.
    """
    path = csv_path or SAMPLE_CSV_PATH
    if not path.is_file():
        return []

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    events: List[NetworkSecurityEvent] = []
    accumulated_offset_s = 0.0

    for idx, row in df.iterrows():
        label = str(row.get("Label", "BENIGN")).strip()
        port = int(row.get("Destination Port", 80))
        dur_us = float(row.get("Flow Duration", 1000.0))
        dur_ms = round(dur_us / 1000.0, 2)
        dur_s = dur_us / 1_000_000.0

        accumulated_offset_s += max(0.01, dur_s)

        fwd_pkts = int(row.get("Total Fwd Packets", 1))
        bwd_pkts = int(row.get("Total Backward Packets", 0))
        total_pkts = fwd_pkts + bwd_pkts

        fwd_bytes = float(row.get("Total Length of Fwd Packets", 0.0))
        bwd_bytes = float(row.get("Total Length of Bwd Packets", 0.0))
        total_bytes = int(fwd_bytes + bwd_bytes)

        pkts_sec = float(row.get("Flow Packets/s", 0.0))
        bytes_sec = float(row.get("Flow Bytes/s", 0.0))

        # Sanitize infinity in rate metrics
        if np.isinf(pkts_sec) or np.isnan(pkts_sec):
            pkts_sec = 0.0
        if np.isinf(bytes_sec) or np.isnan(bytes_sec):
            bytes_sec = 0.0

        syn_flags = int(row.get("SYN Flag Count", 0))
        ack_flags = int(row.get("ACK Flag Count", 0))

        service = _resolve_service_name(port)
        severity = SEVERITY_MAP.get(label, "LOW")

        # Apply optional filters
        if isinstance(category_filter, str) and category_filter.strip() and category_filter.strip().upper() != "ALL":
            if label.upper() != category_filter.strip().upper():
                continue
        if isinstance(severity_filter, str) and severity_filter.strip() and severity_filter.strip().upper() != "ALL":
            if severity.upper() != severity_filter.strip().upper():
                continue

        description = _build_event_description(label, port, service, total_pkts, dur_ms)

        event = NetworkSecurityEvent(
            event_id=f"EVT-{idx + 1:04d}",
            sequence_index=int(idx),
            destination_port=port,
            service_name=service,
            protocol="TCP",  # TCP flag profiles dominate CICIDS flow telemetry
            duration_ms=dur_ms,
            packet_count=total_pkts,
            byte_count=total_bytes,
            flow_packets_sec=round(pkts_sec, 1),
            flow_bytes_sec=round(bytes_sec, 1),
            syn_flag_count=syn_flags,
            ack_flag_count=ack_flags,
            attack_category=label,
            severity=severity,
            relative_time_s=round(accumulated_offset_s, 2),
            description=description,
        )
        events.append(event)

        if limit is not None and len(events) >= limit:
            break

    return events

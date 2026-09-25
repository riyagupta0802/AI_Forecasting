"""Formatting and feature description helpers for HEX HIVE Phase 11 Explainable AI.

Translates technical CICIDS2017 continuous network flow telemetry into intuitive
human-readable descriptions, and formats local and global SHAP contributions
with careful, non-causal phrasing.
"""

from typing import Dict, Tuple, List
from ml.explainability.models import FeatureContribution

FRIENDLY_FEATURE_MAP: Dict[str, Tuple[str, str]] = {
    "Destination Port": (
        "Destination Service Port",
        "Target network transport port receiving incoming flow packets.",
    ),
    "Flow Duration": (
        "Total Flow Duration",
        "Total elapsed duration of the network connection in microseconds.",
    ),
    "Total Fwd Packets": (
        "Forward Packet Count",
        "Total number of packets transmitted from client source to destination.",
    ),
    "Total Backward Packets": (
        "Backward Packet Count",
        "Total number of response packets sent from destination back to source.",
    ),
    "Total Length of Fwd Packets": (
        "Total Forward Payload Volume",
        "Aggregate byte size of all packets transmitted from source to destination.",
    ),
    "Total Length of Bwd Packets": (
        "Total Backward Payload Volume",
        "Aggregate byte size of all response packets returned to source.",
    ),
    "Fwd Packet Length Max": (
        "Maximum Forward Packet Size",
        "Largest single packet payload transmitted in the forward direction.",
    ),
    "Fwd Packet Length Min": (
        "Minimum Forward Packet Size",
        "Smallest packet payload transmitted in the forward direction.",
    ),
    "Fwd Packet Length Mean": (
        "Mean Forward Packet Size",
        "Average payload size of packets sent from source to destination.",
    ),
    "Fwd Packet Length Std": (
        "Forward Packet Size Variance",
        "Standard deviation of packet lengths transmitted in the forward direction.",
    ),
    "Bwd Packet Length Max": (
        "Maximum Backward Packet Size",
        "Largest single response packet payload returned by the destination.",
    ),
    "Bwd Packet Length Min": (
        "Minimum Backward Packet Size",
        "Smallest response packet payload returned by the destination.",
    ),
    "Bwd Packet Length Mean": (
        "Mean Backward Packet Size",
        "Average payload size of response packets sent back from destination.",
    ),
    "Bwd Packet Length Std": (
        "Backward Packet Size Variance",
        "Standard deviation of packet lengths returned by the destination.",
    ),
    "Flow Bytes/s": (
        "Flow Byte Transfer Velocity",
        "Data throughput rate in bytes per second across the flow lifetime.",
    ),
    "Flow Packets/s": (
        "Flow Packet Transmission Rate",
        "Packet transmission frequency per second across the flow lifetime.",
    ),
    "Flow IAT Mean": (
        "Mean Packet Inter-Arrival Time",
        "Average microsecond interval between consecutive packets in the flow.",
    ),
    "Flow IAT Std": (
        "Packet Inter-Arrival Time Variance",
        "Standard deviation of timing intervals between consecutive flow packets.",
    ),
    "Flow IAT Max": (
        "Maximum Packet Inter-Arrival Time",
        "Longest duration observed between consecutive packets in the flow.",
    ),
    "Flow IAT Min": (
        "Minimum Packet Inter-Arrival Time",
        "Shortest microsecond interval between consecutive packets in the flow.",
    ),
    "Fwd IAT Total": (
        "Forward Inter-Arrival Time Total",
        "Cumulative time between forward packets sent from client to server.",
    ),
    "Fwd IAT Mean": (
        "Forward Mean Inter-Arrival Time",
        "Average time interval between consecutive forward packets.",
    ),
    "Bwd IAT Mean": (
        "Backward Mean Inter-Arrival Time",
        "Average time interval between consecutive backward response packets.",
    ),
    "Fwd PSH Flags": (
        "Forward Push Flag Count",
        "Frequency of TCP PSH flags requesting immediate data delivery.",
    ),
    "Bwd PSH Flags": (
        "Backward Push Flag Count",
        "Frequency of TCP PSH flags sent by destination responder.",
    ),
    "Fwd URG Flags": (
        "Forward Urgent Flag Count",
        "Count of packets with TCP URG flag asserted in forward direction.",
    ),
    "Fwd Header Length": (
        "Forward Protocol Header Bytes",
        "Total header byte size for TCP/IP packets sent in forward direction.",
    ),
    "Bwd Header Length": (
        "Backward Protocol Header Bytes",
        "Total header byte size for TCP/IP packets sent in backward direction.",
    ),
    "Packet Length Min": (
        "Minimum Overall Packet Length",
        "Smallest packet length observed across all bidirectional traffic.",
    ),
    "Packet Length Max": (
        "Maximum Overall Packet Length",
        "Largest packet length observed across all bidirectional traffic.",
    ),
    "Packet Length Mean": (
        "Mean Overall Packet Length",
        "Average packet length in bytes across the entire bidirectional flow.",
    ),
    "Packet Length Std": (
        "Overall Packet Length Variance",
        "Standard deviation of packet lengths across bidirectional traffic.",
    ),
    "Packet Length Variance": (
        "Packet Length Variance Metric",
        "Statistical variance of packet sizes reflecting payload uniformity.",
    ),
    "FIN Flag Count": (
        "TCP FIN Flag Count",
        "Number of connection termination FIN flags observed in the flow.",
    ),
    "SYN Flag Count": (
        "TCP SYN Flag Count",
        "Number of connection synchronization SYN flags initiating sessions.",
    ),
    "RST Flag Count": (
        "TCP RST Flag Count",
        "Number of connection reset RST flags aborting connections.",
    ),
    "PSH Flag Count": (
        "TCP PSH Flag Count",
        "Number of push flags requesting immediate socket buffer flush.",
    ),
    "ACK Flag Count": (
        "TCP ACK Flag Count",
        "Number of acknowledgment ACK flags confirming receipt of packets.",
    ),
    "URG Flag Count": (
        "TCP URG Flag Count",
        "Number of urgent flags indicating out-of-band data delivery.",
    ),
    "Average Packet Size": (
        "Average Composite Packet Size",
        "Calculated average byte size per packet across the entire flow.",
    ),
    "Avg Fwd Segment Size": (
        "Average Forward Segment Size",
        "Mean TCP segment length transmitted in the forward direction.",
    ),
    "Avg Bwd Segment Size": (
        "Average Backward Segment Size",
        "Mean TCP segment length transmitted in the backward direction.",
    ),
    "Init_Win_bytes_forward": (
        "Initial TCP Window Size (Forward)",
        "Receive window size in bytes advertised in client initial SYN handshake.",
    ),
    "Init_Win_bytes_backward": (
        "Initial TCP Window Size (Backward)",
        "Receive window size in bytes advertised by responder in SYN-ACK packet.",
    ),
    "act_data_pkt_fwd": (
        "Actual Data Packet Count (Fwd)",
        "Count of forward packets carrying at least 1 byte of application payload.",
    ),
    "min_seg_size_forward": (
        "Minimum Forward Segment Size",
        "Minimum TCP header and segment size observed in forward direction.",
    ),
    "Active Mean": (
        "Mean Active Time Duration",
        "Mean time in microseconds the flow was actively transmitting before idling.",
    ),
    "Idle Mean": (
        "Mean Idle Time Duration",
        "Mean time in microseconds the flow remained idle without packet transmission.",
    ),
}


def get_friendly_feature_meta(feature_name: str) -> Tuple[str, str]:
    """Retrieve friendly display name and security description for a feature name."""
    clean_name = feature_name.strip()
    if clean_name in FRIENDLY_FEATURE_MAP:
        return FRIENDLY_FEATURE_MAP[clean_name]

    # Clean generic fallback
    friendly = clean_name.replace("_", " ").title()
    desc = f"Observed flow telemetry metric for {friendly}."
    return friendly, desc


def format_explanation_summary(
    prediction: str,
    confidence: float,
    top_features: List[FeatureContribution],
) -> str:
    """Generate a responsible, human-readable summary of model feature contributions."""
    if not top_features:
        return f"NETORACLE classified this traffic flow as {prediction} with {confidence:.1f}% confidence."

    # Identify primary positive contributors (pushed toward the prediction)
    toward_feats = [f for f in top_features if f.direction == "toward_prediction"]
    away_feats = [f for f in top_features if f.direction == "away_from_prediction"]

    top_names = [f.friendly_name for f in (toward_feats[:3] if toward_feats else top_features[:3])]
    names_str = ", ".join(top_names)

    summary_text = (
        f"NETORACLE classified this traffic as {prediction} ({confidence:.1f}% confidence) "
        f"primarily because the following network characteristics had the strongest influence "
        f"on the model's decision: {names_str}."
    )

    if away_feats:
        contrary_name = away_feats[0].friendly_name
        summary_text += (
            f" Counter-indicators like {contrary_name} partially moderated the confidence."
        )

    return summary_text


def format_technical_summary(
    base_value: float,
    predicted_value: float,
    top_features: List[FeatureContribution],
) -> str:
    """Format technical mathematical decomposition of TreeExplainer SHAP contributions."""
    sum_top_shap = sum(f.shap_value for f in top_features)
    return (
        f"SHAP Decomposition: Base value E[f(x)] = {base_value:.4f}. "
        f"Top {len(top_features)} features aggregate SHAP contribution = {sum_top_shap:+.4f}. "
        f"Model margin output f(x) = {predicted_value:.4f}."
    )


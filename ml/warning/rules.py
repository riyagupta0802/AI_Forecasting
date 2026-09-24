"""Deterministic decision rules and severity thresholds for Phase 9 Early Warning Engine.

Implements transparent, evidence-grounded rules mapping multi-source telemetry
(Detection, Forecast, Escalation, Correlated Clusters) to standardized severity
levels (CRITICAL, HIGH, MEDIUM, LOW, INFO) and warning types.
"""

from typing import Dict, Any, List, Optional, Tuple


# Configurable time and velocity thresholds
THRESHOLD_CRITICAL_SECONDS = 60
THRESHOLD_HIGH_SECONDS = 180
THRESHOLD_MEDIUM_SECONDS = 360
THRESHOLD_CRITICAL_VELOCITY = 1.5

# Known high-risk service ports from dataset grounding
KNOWN_C2_PORTS = {6667, 4444}  # IRC Botnet C2, Metasploit default
KNOWN_WEB_PORTS = {80, 443}    # HTTP, HTTPS web flood targets


def evaluate_warning_decision(
    detection_state: str,
    detection_confidence: float,
    forecast_state: str,
    predicted_state: str,
    forecast_confidence: float,
    escalation_seconds: Optional[int],
    velocity_index: float,
    is_escalating: bool,
    target_ports: List[int],
    cluster_count: int,
) -> Tuple[str, str, str, str]:
    """Evaluate pipeline telemetry against deterministic security rules.

    Returns:
        Tuple of (severity, warning_type, rule_id, rationale)
    """
    port_set = set(target_ports)

    # 1. CRITICAL: Volumetric disruption or imminent high-velocity escalation (<= 60s)
    if forecast_state == "DDoS":
        return (
            "CRITICAL",
            "VOLUMETRIC_DISRUPTION",
            "RULE_CRITICAL_VOLUMETRIC_PEAK",
            "Active volumetric saturation flood targeting web endpoints. Telemetry indicates maximum capacity strain.",
        )
    if is_escalating and escalation_seconds is not None and escalation_seconds <= THRESHOLD_CRITICAL_SECONDS:
        return (
            "CRITICAL",
            "POTENTIAL_ESCALATION",
            "RULE_CRITICAL_IMMINENT_ESCALATION",
            f"Escalation countdown ({escalation_seconds}s) is below critical threshold (<= {THRESHOLD_CRITICAL_SECONDS}s) with elevated flow velocity ({velocity_index}x).",
        )

    # 2. HIGH: C2 staging, Bot communication, or rapid escalation (61s - 180s)
    if forecast_state == "Bot" or (detection_state.upper() == "ATTACK" and bool(port_set.intersection(KNOWN_C2_PORTS))):
        return (
            "HIGH",
            "MALICIOUS_STAGING",
            "RULE_HIGH_C2_STAGING",
            f"Active host compromise or botnet C2 staging detected on service ports {sorted(list(port_set.intersection(KNOWN_C2_PORTS)) or [6667])}.",
        )
    if is_escalating and escalation_seconds is not None and escalation_seconds <= THRESHOLD_HIGH_SECONDS:
        return (
            "HIGH",
            "POTENTIAL_ESCALATION",
            "RULE_HIGH_ESCALATION_WINDOW",
            f"Forecasted progression to '{predicted_state}' estimated within {escalation_seconds}s (<= {THRESHOLD_HIGH_SECONDS}s).",
        )

    # 3. MEDIUM: Systematic host/port reconnaissance or moderate escalation (181s - 360s)
    if forecast_state == "PortScan" or (detection_state.upper() == "ATTACK" and len(target_ports) >= 5):
        return (
            "MEDIUM",
            "SUSPICIOUS_RECONNAISSANCE",
            "RULE_MEDIUM_RECON_SWEEP",
            f"Systematic reconnaissance sweep observed across {len(target_ports)} destination ports.",
        )
    if is_escalating and escalation_seconds is not None and escalation_seconds <= THRESHOLD_MEDIUM_SECONDS:
        return (
            "MEDIUM",
            "POTENTIAL_ESCALATION",
            "RULE_MEDIUM_ESCALATION_WINDOW",
            f"Threat exhibits forward escalation indicator toward '{predicted_state}' within {escalation_seconds}s.",
        )

    # 4. LOW: Detected anomaly without imminent escalation indicators
    if detection_state.upper() == "ATTACK":
        return (
            "LOW",
            "POTENTIAL_ESCALATION",
            "RULE_LOW_ANOMALOUS_PROBE",
            "Anomalous packet flow detected; escalation telemetry indicates extended timeline or low flow velocity.",
        )
    if is_escalating and escalation_seconds is not None and escalation_seconds > THRESHOLD_MEDIUM_SECONDS:
        return (
            "LOW",
            "POTENTIAL_ESCALATION",
            "RULE_LOW_EXTENDED_WINDOW",
            f"Distant escalation window ({escalation_seconds}s > {THRESHOLD_MEDIUM_SECONDS}s) indicates low immediate urgency.",
        )

    # 5. INFO: Baseline operational telemetry
    return (
        "INFO",
        "BASELINE_OBSERVATION",
        "RULE_INFO_NORMAL_BASELINE",
        "Operational telemetry matches expected baseline distributions. Detection models report zero active intrusions.",
    )

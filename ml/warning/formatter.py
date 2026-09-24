"""Message, title, and recommended attention formatters for Early Warnings.

Produces evidence-grounded, non-sensationalized incident titles, explanations,
and SOC analyst triage guidance based strictly on verified telemetry and model predictions.
"""

from typing import List, Dict, Any, Optional
from ml.warning.models import EvidenceItem


def format_warning_title(warning_type: str, severity: str, current_state: str, predicted_state: str) -> str:
    """Generate a concise, professional title for the early warning alert."""
    if warning_type == "VOLUMETRIC_DISRUPTION":
        return "Critical Volumetric Inundation & Capacity Saturation"
    elif warning_type == "MALICIOUS_STAGING":
        return f"Malicious Command & Control Staging Observed ({current_state})"
    elif warning_type == "SUSPICIOUS_RECONNAISSANCE":
        return f"Systematic Network Reconnaissance Sweep Detected ({current_state})"
    elif warning_type == "POTENTIAL_ESCALATION":
        return f"Threat Escalation Window Projected ({current_state} -> {predicted_state})"
    elif warning_type == "BASELINE_OBSERVATION":
        return "Operational Network Baseline Stable - Zero Active Threats"
    return f"Security Advisory: {current_state} Activity ({severity})"


def format_warning_message(
    warning_type: str,
    severity: str,
    current_state: str,
    predicted_state: str,
    escalation_window: str,
    rule_rationale: str,
) -> str:
    """Generate a detailed explanation of the security condition and contributing factors."""
    if severity == "INFO":
        return "All monitored endpoints exhibit normal flow behavior within baseline statistical tolerances. No intrusion signals detected."

    base = f"The Early Warning Engine has detected an elevated security condition classified as {severity}. {rule_rationale}"
    if current_state != predicted_state and predicted_state != "BENIGN":
        base += f" Telemetry indicates progression toward '{predicted_state}' with an estimated escalation window of {escalation_window}."
    return base


def format_recommended_attention(severity: str, warning_type: str, current_state: str, target_ports: List[int]) -> str:
    """Synthesize evidence-grounded SOC triage guidance."""
    ports_str = ", ".join(str(p) for p in target_ports[:4])
    if target_ports and len(target_ports) > 4:
        ports_str += f" (+{len(target_ports) - 4} more)"

    if severity == "CRITICAL":
        return f"Immediate SOC Tier-2 engagement recommended. Investigate high-volume ingress saturation on ports {ports_str or '80/443'} and inspect upstream edge rate limiters."
    elif severity == "HIGH":
        return f"Priority triage recommended. Review destination endpoints {ports_str or '6667/4444'} for unauthorized persistence or botnet communication beaconing."
    elif severity == "MEDIUM":
        return f"Elevated monitoring advised. Track source subnet addresses probing ports {ports_str or 'dynamic range'} for subsequent authentication attempts or vulnerability exploitation."
    elif severity == "LOW":
        return "Routine observation recommended. Validate that low-velocity anomalous packets do not exceed standard baseline thresholds."
    return "Standard operational monitoring active. No intervention required."


def compile_evidence_items(
    detection_res: Dict[str, Any],
    forecast_res: Dict[str, Any],
    escalation_res: Dict[str, Any],
    clusters: List[Any],
    target_ports: List[int],
) -> List[EvidenceItem]:
    """Compile verifiable evidence items across all pipeline stages."""
    evidence: List[EvidenceItem] = []

    # 1. Detection Evidence (Phase 5)
    det_status = detection_res.get("prediction", "BENIGN")
    det_conf = detection_res.get("confidence", 0.0)
    det_desc = (
        f"Phase 5 Random Forest classifier identified flow as {det_status} with {det_conf * 100:.1f}% confidence."
        if det_status == "ATTACK"
        else f"Phase 5 binary classifier confirmed normal baseline traffic with {det_conf * 100:.1f}% confidence."
    )
    evidence.append(
        EvidenceItem(
            evidence_type="detection",
            headline=f"Binary Intrusion Classifier: {det_status}",
            description=det_desc,
            source="Phase 5 Random Forest Classifier",
            confidence=det_conf,
            metrics={"prediction": det_status, "confidence": det_conf},
        )
    )

    # 2. Forecast Evidence (Phase 6)
    fc_state = forecast_res.get("current_state", "BENIGN")
    fc_pred = forecast_res.get("predicted_stage", "BENIGN")
    fc_conf = forecast_res.get("confidence", 0.0)
    fc_desc = (
        f"Phase 6 multi-class stage model identified active stage '{fc_state}' and projected transition toward '{fc_pred}' with {fc_conf * 100:.1f}% calibrated transition probability."
        if fc_state != "BENIGN"
        else "Phase 6 multi-class model confirmed baseline operations with low probability of near-term intrusion."
    )
    evidence.append(
        EvidenceItem(
            evidence_type="forecast",
            headline=f"Kill Chain Progression: {fc_state} -> {fc_pred}",
            description=fc_desc,
            source="Phase 6 Multi-Class Stage Classifier & Transition Forecaster",
            confidence=fc_conf,
            metrics={"current_stage": fc_state, "projected_stage": fc_pred, "confidence": fc_conf},
        )
    )

    # 3. Escalation Evidence (Phase 7)
    esc_status = escalation_res.get("status", "Not Escalating")
    esc_window = escalation_res.get("formatted_time", "Not Escalating")
    esc_vel = escalation_res.get("velocity_index", 1.0)
    esc_desc = (
        f"Phase 7 supervised regression model estimates escalation window: {esc_window} (Velocity factor: {esc_vel:.2f}x, Risk: {escalation_res.get('risk_level', 'LOW')})."
        if escalation_res.get("is_escalating")
        else f"Escalation analysis reports status: {esc_status}. Telemetry velocity is baseline ({esc_vel:.2f}x)."
    )
    evidence.append(
        EvidenceItem(
            evidence_type="escalation",
            headline=f"Time-to-Escalation Window: {esc_window}",
            description=esc_desc,
            source="Phase 7 Velocity-Calibrated Regressor",
            confidence=escalation_res.get("confidence", 85.0) / 100.0 if escalation_res.get("confidence") else None,
            metrics={
                "status": esc_status,
                "window": esc_window,
                "seconds": escalation_res.get("estimated_time_seconds"),
                "velocity_index": esc_vel,
            },
        )
    )

    # 4. Correlated Event Evidence (Phase 8)
    cluster_count = len(clusters)
    ports_slice = target_ports[:6]
    corr_desc = (
        f"Phase 8 event correlator assembled {cluster_count} campaign cluster(s) targeting ports {ports_slice}."
        if cluster_count > 0
        else "No anomalous multi-stage clustering detected; single-flow baseline confirmed."
    )
    evidence.append(
        EvidenceItem(
            evidence_type="correlation",
            headline=f"Correlated Event Clusters: {cluster_count} identified",
            description=corr_desc,
            source="Phase 8 Event Correlator & Timeline Builder",
            confidence=None,
            metrics={"cluster_count": cluster_count, "sample_target_ports": ports_slice},
        )
    )

    return evidence

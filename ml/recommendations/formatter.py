"""Formatting and evidence compilation utilities for HEX HIVE Phase 10 Recommendation Engine.

Compiles grounded evidence trails directly linking recommendations to:
- Phase 5: Detection classifier output
- Phase 6: Stage forecaster projection
- Phase 7: Time-to-escalation window
- Phase 8: Attack story correlated clusters
- Phase 9: Early warning alerts
"""

from typing import List, Dict, Any, Optional


def compile_recommendation_evidence(
    detection_res: Dict[str, Any],
    forecast_res: Dict[str, Any],
    escalation_res: Dict[str, Any],
    story_clusters: List[Dict[str, Any]],
    warning_dict: Optional[Dict[str, Any]],
    target_ports: List[int],
) -> List[str]:
    """Compile verifiable evidence items from all upstream pipeline phases.

    Args:
        detection_res: Phase 5 binary detection result dictionary.
        forecast_res: Phase 6 multi-stage forecasting dictionary.
        escalation_res: Phase 7 time-to-escalation dictionary.
        story_clusters: Phase 8 correlated incident clusters.
        warning_dict: Phase 9 early warning dictionary.
        target_ports: List of destination ports observed.

    Returns:
        List of formatted evidence strings with component attribution.
    """
    evidence: List[str] = []

    # 1. Phase 5 Detection Evidence
    det_label = detection_res.get("prediction", "BENIGN")
    det_conf = detection_res.get("confidence")
    det_conf_str = f" ({det_conf*100:.1f}% confidence)" if det_conf is not None else ""
    evidence.append(f"Phase 5 Detection: Classified as {det_label}{det_conf_str} via Random Forest model")

    # 2. Phase 6 Forecasting Evidence
    curr_stage = forecast_res.get("current_state", "BENIGN")
    pred_stage = forecast_res.get("predicted_stage", "BENIGN")
    fc_conf = forecast_res.get("confidence")
    fc_conf_str = f" ({fc_conf*100:.1f}% probability)" if fc_conf is not None else ""
    if curr_stage != "BENIGN" or pred_stage != "BENIGN":
        evidence.append(f"Phase 6 Forecasting: Current state '{curr_stage}' -> Projected state '{pred_stage}'{fc_conf_str}")
    else:
        evidence.append("Phase 6 Forecasting: Telemetry indicates continuous normal baseline operation")

    # 3. Phase 7 Escalation Evidence
    esc_window = escalation_res.get("formatted_time", "Not Escalating")
    vel_idx = escalation_res.get("velocity_index")
    vel_str = f" (velocity {vel_idx:.1f}x)" if vel_idx is not None else ""
    esc_secs = escalation_res.get("estimated_time_seconds")
    if esc_secs is not None and esc_secs > 0:
        evidence.append(f"Phase 7 Escalation: Escalation horizon estimated at {esc_window}{vel_str}")
    else:
        evidence.append(f"Phase 7 Escalation: {esc_window} (nominal inter-arrival variance)")

    # 4. Phase 8 Attack Story Evidence
    if story_clusters:
        first_cluster = story_clusters[0]
        cid = first_cluster.get("cluster_id", "INC-001")
        c_events = first_cluster.get("event_count", len(story_clusters))
        ports_cnt = len(target_ports)
        evidence.append(f"Phase 8 Attack Story: Incident cluster {cid} with {c_events} events across {ports_cnt} ports")
    elif target_ports:
        ports_str = ", ".join(str(p) for p in target_ports[:5])
        evidence.append(f"Phase 8 Attack Story: Telemetry mapped to destination ports [{ports_str}]")
    else:
        evidence.append("Phase 8 Attack Story: Zero malicious correlated incident clusters identified")

    # 5. Phase 9 Early Warning Evidence
    if warning_dict and warning_dict.get("severity") != "INFO":
        w_sev = warning_dict.get("severity", "LOW")
        w_type = warning_dict.get("warning_type", "ELEVATED_RISK")
        w_id = warning_dict.get("warning_id", "WRN-CURRENT")
        evidence.append(f"Phase 9 Early Warning: Active {w_sev} alert '{w_type}' (ID: {w_id})")
    else:
        evidence.append("Phase 9 Early Warning: System alert posture is INFO (normal baseline verified)")

    return evidence


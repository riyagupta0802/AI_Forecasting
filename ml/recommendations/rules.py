"""Deterministic defensive security recommendation rules for HEX HIVE Phase 10.

Evaluates multi-source telemetry from:
- Phase 5: Binary Attack Detection (BENIGN vs ATTACK, confidence)
- Phase 6: Attack Stage Forecasting (current stage, projected next stage, probability)
- Phase 7: Time-to-Escalation (countdown seconds, velocity factor, escalation urgency)
- Phase 8: Attack Story (correlated event clusters, probed destination ports)
- Phase 9: Early Warning Engine (active severity, warning type, alert fingerprint)

Produces contextual, defensive recommendations with transparent rule traceability.
"""

from typing import List, Dict, Any, Optional, Tuple


def evaluate_recommendation_rules(
    detection_state: str,
    detection_confidence: float,
    current_stage: str,
    predicted_stage: str,
    forecast_confidence: float,
    escalation_seconds: Optional[int],
    escalation_window: str,
    velocity_index: float,
    warning_severity: str,
    warning_type: str,
    target_ports: List[int],
    cluster_count: int,
) -> List[Dict[str, Any]]:
    """Evaluate deterministic rules to determine appropriate defensive recommendations.

    Args:
        detection_state: 'ATTACK' or 'BENIGN'.
        detection_confidence: Model confidence from Phase 5 (0.0 to 1.0).
        current_stage: Active stage ('PortScan', 'Bot', 'DDoS', 'BENIGN').
        predicted_stage: Projected stage ('PortScan', 'Bot', 'DDoS', 'BENIGN').
        forecast_confidence: Multi-class stage probability from Phase 6.
        escalation_seconds: Estimated seconds to escalation from Phase 7.
        escalation_window: Formatted escalation window string.
        velocity_index: Rate of threat progression (1.0 = nominal baseline).
        warning_severity: Alert tier from Phase 9 ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO').
        warning_type: Categorized warning trigger from Phase 9.
        target_ports: List of destination ports observed in telemetry.
        cluster_count: Number of correlated attack story clusters from Phase 8.

    Returns:
        List of rule decision dictionaries with defensive actions, reasons, and metadata.
    """
    rules: List[Dict[str, Any]] = []
    ports_str = ", ".join(str(p) for p in target_ports[:6]) if target_ports else "standard service ports"

    # =========================================================================
    # CASE 1: VOLUMETRIC ATTACK / CRITICAL ESCALATION (DDoS / Imminent Outage)
    # =========================================================================
    if (
        current_stage == "DDoS"
        or warning_severity == "CRITICAL"
        or (escalation_seconds is not None and escalation_seconds <= 60 and velocity_index >= 1.5)
    ):
        rules.append({
            "rule_id": "REC-RULE-DDOS-RATE-LIMIT",
            "priority": "CRITICAL",
            "category": "Contain",
            "title": "Engage Upstream Flow Rate Limiting on Perimeter Gateways",
            "action": (
                f"Consider enabling upstream rate-limiting policies and perimeter traffic scrubbing "
                f"on external ingress interfaces targeting service ports [{ports_str}]."
            ),
            "reason": (
                f"Active high-volume traffic surge detected ({current_stage}) with velocity factor "
                f"{velocity_index:.1f}x. Immediate ingress bandwidth mitigation is required to maintain service availability."
            ),
            "target_asset": "Perimeter-Ingress-Gateway",
            "source": "rule/ddos_perimeter_containment_v1",
        })

        rules.append({
            "rule_id": "REC-RULE-DDOS-ESCALATE-SOC",
            "priority": "CRITICAL",
            "category": "Escalate",
            "title": "Escalate Incident to Network Operations & Tier-2 Bridge",
            "action": (
                "Security operator should notify Network Operations (NetOps) and initiate the "
                "incident response conference bridge to coordinate ISP-level BGP blackholing or upstream scrubbing."
            ),
            "reason": (
                f"Telemetry indicates volumetric saturation risks with escalation window '{escalation_window}'. "
                f"Adversary volume threatens edge uplink capacity."
            ),
            "target_asset": "SOC-Incident-Bridge",
            "source": "rule/soc_emergency_escalation_v1",
        })

        rules.append({
            "rule_id": "REC-RULE-DDOS-PRESERVE-NETFLOW",
            "priority": "HIGH",
            "category": "Preserve",
            "title": "Preserve NetFlow Telemetry & Packet Header Captures",
            "action": (
                "Consider initiating packet header snapshots and archiving NetFlow telemetry "
                "from edge routers to secure non-volatile storage before circular buffer overwrite."
            ),
            "reason": (
                "Accurate forensic attribution and post-incident scrubbing rule tuning require "
                "unaltered packet headers recorded during peak flow volume."
            ),
            "target_asset": "Forensic-Storage-Repository",
            "source": "rule/forensic_evidence_preservation_v1",
        })

    # =========================================================================
    # CASE 2: C2 COMMUNICATION / ACTIVE BOTNET STAGING (Bot / High Escalation)
    # =========================================================================
    elif (
        current_stage == "Bot"
        or warning_severity == "HIGH"
        or (escalation_seconds is not None and 61 <= escalation_seconds <= 180)
    ):
        rules.append({
            "rule_id": "REC-RULE-BOT-ISOLATE-ENDPOINT",
            "priority": "HIGH",
            "category": "Isolate",
            "title": "Consider Isolating Compromised Host Endpoint",
            "action": (
                "Consider applying a host-level network quarantine or moving the affected internal endpoint "
                "to an isolated containment VLAN after verifying suspicious outbound C2 beaconing activity."
            ),
            "reason": (
                f"Persistent command-and-control communication characteristics identified ({current_stage}) "
                f"with projected escalation stage '{predicted_stage}'. Quarantine prevents lateral movement."
            ),
            "target_asset": "Internal-Endpoint-Host",
            "source": "rule/c2_endpoint_quarantine_v1",
        })

        rules.append({
            "rule_id": "REC-RULE-BOT-INVESTIGATE-AUTH",
            "priority": "HIGH",
            "category": "Investigate",
            "title": "Inspect Host Authentication & Process Execution Telemetry",
            "action": (
                "Security operator should inspect active sockets, running child processes, "
                "and recent privileged authentication logs on the flagged endpoint."
            ),
            "reason": (
                f"Early warning {warning_type} indicates malicious execution staging. "
                "Operator validation ensures unauthorized persistence scripts are promptly identified."
            ),
            "target_asset": "Host-Process-Monitor",
            "source": "rule/host_telemetry_investigation_v1",
        })

        rules.append({
            "rule_id": "REC-RULE-BOT-REVIEW-EGRESS",
            "priority": "MEDIUM",
            "category": "Review",
            "title": "Review Egress Firewall Rules for Destination IPs",
            "action": (
                "Consider reviewing egress firewall access lists to block unauthorized outbound socket connections "
                "to foreign IP addresses and known dynamic DNS providers."
            ),
            "reason": (
                "Adversary bot infrastructure relies on outbound egress channels. "
                "Severing external communication channels suppresses command execution."
            ),
            "target_asset": "Perimeter-Egress-Firewall",
            "source": "rule/egress_filtering_review_v1",
        })

    # =========================================================================
    # CASE 3: ADVERSARY RECONNAISSANCE / SYSTEMATIC PROBES (PortScan / Probing)
    # =========================================================================
    elif (
        current_stage == "PortScan"
        or warning_severity == "MEDIUM"
        or (escalation_seconds is not None and 181 <= escalation_seconds <= 360)
        or (detection_state == "ATTACK" and len(target_ports) >= 5)
    ):
        rules.append({
            "rule_id": "REC-RULE-SCAN-REVIEW-FIREWALL",
            "priority": "MEDIUM",
            "category": "Review",
            "title": "Review Access Rules for Scanned Service Ports",
            "action": (
                f"Consider verifying perimeter firewall ingress access rules for target ports [{ports_str}] "
                f"and evaluate adding temporary drop rules for the scanning source CIDR block."
            ),
            "reason": (
                f"Systematic reconnaissance detected across {len(target_ports)} service ports. "
                f"Restricting unauthenticated ingress limits attacker surface visibility."
            ),
            "target_asset": "Perimeter-Firewall-ACL",
            "source": "rule/recon_firewall_review_v1",
        })

        rules.append({
            "rule_id": "REC-RULE-SCAN-INCREASE-MONITORING",
            "priority": "MEDIUM",
            "category": "Monitor",
            "title": "Increase Telemetry Sampling Granularity on Monitored Gateways",
            "action": (
                "Consider increasing NetFlow export granularity and enabling verbose TCP flag logging "
                "on edge perimeter ingress interfaces."
            ),
            "reason": (
                f"Adversary port scanning routinely precedes vulnerability exploitation "
                f"(forecasted stage: '{predicted_stage}'). Granular telemetry aids rapid correlation."
            ),
            "target_asset": "Edge-Flow-Collector",
            "source": "rule/telemetry_granularity_boost_v1",
        })

        rules.append({
            "rule_id": "REC-RULE-SCAN-INVESTIGATE-EXPOSURE",
            "priority": "LOW",
            "category": "Investigate",
            "title": "Inspect Targeted Internal Services for Unpatched Exposure",
            "action": (
                f"Security operator should audit daemon listeners on scanned ports [{ports_str}] "
                f"to confirm running services are up to date and unnecessary ports are closed."
            ),
            "reason": (
                "Port scans seek unpatched or legacy service endpoints. "
                "Verifying daemon patch status minimizes successful post-reconnaissance exploitation."
            ),
            "target_asset": "Internal-Service-Daemons",
            "source": "rule/service_exposure_audit_v1",
        })

    # =========================================================================
    # CASE 4: NORMAL BASELINE TELEMETRY (BENIGN / Baseline Operational)
    # =========================================================================
    else:
        rules.append({
            "rule_id": "REC-RULE-BASELINE-MONITOR",
            "priority": "LOW",
            "category": "Monitor",
            "title": "Maintain Standard Baseline Telemetry Monitoring",
            "action": (
                "Continue standard continuous monitoring of network flow telemetry; "
                "no immediate containment, host isolation, or ACL modification is required."
            ),
            "reason": (
                f"Inspected traffic adheres to normal baseline operational parameters "
                f"(detection: {detection_state}, confidence {detection_confidence*100:.1f}%). "
                "No active adversarial progression detected."
            ),
            "target_asset": "Core-Network-Monitoring",
            "source": "rule/baseline_operational_monitoring_v1",
        })

        rules.append({
            "rule_id": "REC-RULE-BASELINE-AUDIT",
            "priority": "LOW",
            "category": "Review",
            "title": "Perform Routine Health & Access Policy Review",
            "action": (
                "Security operator may conduct scheduled routine audits of firewall rules "
                "and verify anomaly threshold baselines remain calibrated."
            ),
            "reason": (
                "Proactive maintenance during quiescent baseline periods ensures high model detection accuracy "
                "and prevents configuration drift."
            ),
            "target_asset": "Security-Policy-Management",
            "source": "rule/routine_hygiene_audit_v1",
        })

    return rules


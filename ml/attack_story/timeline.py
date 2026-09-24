"""Chronological Timeline Assembly for HEX HIVE Phase 8 Attack Story.

Connects observed correlated event clusters, current Phase 5 detection posture,
Phase 6 transition forecasting, and Phase 7 escalation timing into a unified security timeline.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from ml.attack_story.correlation import CorrelatedAttackCluster


@dataclass
class TimelineNode:
    """A distinct milestone entry on the chronological attack timeline."""

    node_id: str
    sequence_order: int
    timestamp_label: str
    title: str
    stage: str
    severity: str
    event_type: str  # 'observed_cluster', 'current_detection', 'forecast_stage', 'escalation_window'
    description: str
    target_ports: List[int]
    is_current: bool
    is_forecast: bool
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ChronologicalTimelineBuilder:
    """Constructs a clean chronological timeline bridging historical events and predictive forecasts."""

    def build_timeline(
        self,
        clusters: List[CorrelatedAttackCluster],
        current_state: str,
        forecast_context: Optional[Dict[str, Any]] = None,
        escalation_context: Optional[Dict[str, Any]] = None,
    ) -> List[TimelineNode]:
        """Synthesize correlated clusters with ML detection, forecasting, and escalation."""
        nodes: List[TimelineNode] = []
        seq = 1

        # 1. Add historical/observed correlated clusters
        for cluster in clusters:
            is_active_stage = (cluster.attack_stage == current_state)
            time_lbl = f"+{cluster.start_time_s:.1f}s"
            title = self._get_cluster_title(cluster.attack_stage, cluster.event_count)

            node = TimelineNode(
                node_id=f"TL-{seq:02d}",
                sequence_order=seq,
                timestamp_label=time_lbl,
                title=title,
                stage=cluster.attack_stage,
                severity=cluster.severity,
                event_type="observed_cluster",
                description=cluster.correlation_rationale,
                target_ports=cluster.target_ports,
                is_current=is_active_stage,
                is_forecast=False,
                details={
                    "event_count": cluster.event_count,
                    "duration_s": cluster.duration_s,
                    "total_packets": cluster.total_packets,
                    "target_services": cluster.target_services,
                },
            )
            nodes.append(node)
            seq += 1

        # 2. Add Phase 6 Forecast Projection Node if available
        if forecast_context and forecast_context.get("forecast_available"):
            next_stage = forecast_context.get("predicted_next_stage", "BENIGN")
            conf = forecast_context.get("confidence", 85.0)
            risk = forecast_context.get("risk_level", "HIGH")
            expl = forecast_context.get("explanation", "Projected next transition stage.")

            forecast_node = TimelineNode(
                node_id=f"TL-{seq:02d}",
                sequence_order=seq,
                timestamp_label="Projected Next",
                title=f"Forecasted Attack Progression: {next_stage}",
                stage=next_stage,
                severity=risk,
                event_type="forecast_stage",
                description=expl,
                target_ports=[],
                is_current=False,
                is_forecast=True,
                details={
                    "confidence": conf,
                    "model": forecast_context.get("model", "Multi-Class StageClassifier"),
                    "transition_probabilities": forecast_context.get("transition_probabilities", {}),
                },
            )
            nodes.append(forecast_node)
            seq += 1

        # 3. Add Phase 7 Time-to-Escalation Window Node if available
        if escalation_context and escalation_context.get("available") and escalation_context.get("is_escalating"):
            est_time = escalation_context.get("formatted_time", "Unknown")
            cond = escalation_context.get("escalation_condition", "Escalation to higher-severity stage")
            esc_risk = escalation_context.get("risk_level", "HIGH")

            esc_node = TimelineNode(
                node_id=f"TL-{seq:02d}",
                sequence_order=seq,
                timestamp_label=f"Escalation Window (~{est_time})",
                title=f"Estimated Escalation: {est_time}",
                stage=escalation_context.get("predicted_state", "Escalation"),
                severity=esc_risk,
                event_type="escalation_window",
                description=f"Condition: {cond}. Velocity index: {escalation_context.get('velocity_index', 1.0)}x.",
                target_ports=[],
                is_current=False,
                is_forecast=True,
                details={
                    "estimated_time_seconds": escalation_context.get("estimated_time_seconds"),
                    "velocity_index": escalation_context.get("velocity_index"),
                    "method": escalation_context.get("method"),
                },
            )
            nodes.append(esc_node)

        return nodes

    def _get_cluster_title(self, stage: str, count: int) -> str:
        """Derive clear title for a correlated timeline stage."""
        if stage == "PortScan":
            return f"Reconnaissance Port Probing ({count} flows)"
        elif stage == "Bot":
            return f"Command & Control Staging Observed ({count} flows)"
        elif stage == "DDoS":
            return f"Volumetric Flood Attack Active ({count} flows)"
        return f"Operational Baseline Network Traffic ({count} flows)"


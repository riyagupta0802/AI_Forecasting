"""Core Security Recommendation Engine for HEX HIVE Phase 10.

Consumes multi-phase telemetry from Phase 5 (Detection), Phase 6 (Forecasting),
Phase 7 (Escalation), Phase 8 (Attack Story), and Phase 9 (Early Warning Engine)
to synthesize contextual, evidence-backed defensive security recommendations.
Supports alert deduplication, in-memory lifecycle state management (PENDING,
ACKNOWLEDGED, RESOLVED), and operator status overrides.
"""

from collections import deque
from datetime import datetime, timezone
import hashlib
import logging
from typing import Dict, Any, List, Optional

from ml.recommendations.models import (
    SecurityRecommendation,
    RecommendationsSummary,
    RecommendationEvaluationResult,
    RecommendationStatus,
    RecommendationPriority,
)
from ml.recommendations.rules import evaluate_recommendation_rules
from ml.recommendations.formatter import compile_recommendation_evidence
from ml.warning import early_warning_engine

logger = logging.getLogger("HEX_HIVE.Recommendation.Engine")


class RecommendationEngine:
    """Evaluates multi-source security intelligence and issues actionable defensive recommendations."""

    def __init__(self):
        self._recommendations_store: Dict[str, SecurityRecommendation] = {}
        self._history: deque = deque(maxlen=50)
        self._rec_seq: int = 1
        self.limitations_note = (
            "Security recommendations are advisory defensive actions derived deterministically "
            "from Phase 5 detection, Phase 6 forecasting, Phase 7 escalation, Phase 8 attack story, "
            "and Phase 9 early warnings on the CICIDS2017 benchmark telemetry. "
            "Recommendations provide guidance for human security operators and do not execute "
            "automated network changes or guarantee complete breach prevention."
        )

    def evaluate(
        self,
        sample_context: str = "auto",
        category_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
        event_limit: int = 50,
    ) -> RecommendationEvaluationResult:
        """Evaluate security pipeline outputs and generate defensive recommendations.

        Args:
            sample_context: Preset scenario ('auto', 'benign', 'portscan', 'bot', 'ddos').
            category_filter: Optional filter for attack category.
            severity_filter: Optional filter for severity.
            event_limit: Max flow events to process.

        Returns:
            RecommendationEvaluationResult containing recommendations and statistical summary.
        """
        # Step 1: Ingest Phase 9 Early Warning evaluation (which orchestrates Phases 5-8)
        warning_eval = early_warning_engine.evaluate(
            sample_context=sample_context,
            category_filter=category_filter,
            severity_filter=severity_filter,
            event_limit=event_limit,
        )

        active_warning = warning_eval.active_warning
        warning_dict = active_warning.to_dict() if active_warning else None
        warning_sev = active_warning.severity if active_warning else "INFO"
        warning_type = active_warning.warning_type if active_warning else "NORMAL_BASELINE"

        # Step 2: Extract upstream features from Phase 8 story engine
        story = early_warning_engine._active_warning  # warning engine already coordinated
        # Retrieve rich data from the warning engine's internal coordination
        from ml.attack_story.story import attack_story_engine
        story_data = attack_story_engine.generate_story(
            category_filter=category_filter,
            severity_filter=severity_filter,
            sample_context=sample_context,
            event_limit=event_limit,
        )

        forecast_res = story_data.get("forecast", {})
        escalation_res = story_data.get("escalation", {})
        clusters = story_data.get("clusters", [])
        events = story_data.get("events_sample", [])

        detection_res = forecast_res.get("detection", {})
        det_state = detection_res.get("prediction", "BENIGN")
        det_conf = float(detection_res.get("confidence", 0.99))

        curr_stage = forecast_res.get("current_state", "BENIGN")
        pred_stage = forecast_res.get("predicted_stage", "BENIGN")
        fc_conf = float(forecast_res.get("confidence", 0.88))

        esc_seconds = escalation_res.get("estimated_time_seconds")
        esc_window = escalation_res.get("formatted_time", "Not Escalating")
        esc_vel = float(escalation_res.get("velocity_index", 1.0))

        # Destination ports
        target_ports: List[int] = []
        if active_warning and active_warning.target_ports:
            target_ports = list(active_warning.target_ports)
        else:
            for c in clusters:
                target_ports.extend(c.get("destination_ports", []))
            if not target_ports:
                for ev in events:
                    p = ev.get("destination_port")
                    if p and p not in target_ports:
                        target_ports.append(p)
        target_ports = sorted(list(set(target_ports)))

        # Step 3: Evaluate deterministic recommendation rules
        rule_decisions = evaluate_recommendation_rules(
            detection_state=det_state,
            detection_confidence=det_conf,
            current_stage=curr_stage,
            predicted_stage=pred_stage,
            forecast_confidence=fc_conf,
            escalation_seconds=esc_seconds,
            escalation_window=esc_window,
            velocity_index=esc_vel,
            warning_severity=warning_sev,
            warning_type=warning_type,
            target_ports=target_ports,
            cluster_count=len(clusters),
        )

        # Step 4: Compile verifiable evidence trail
        evidence_list = compile_recommendation_evidence(
            detection_res=detection_res,
            forecast_res=forecast_res,
            escalation_res=escalation_res,
            story_clusters=clusters,
            warning_dict=warning_dict,
            target_ports=target_ports,
        )

        now_iso = datetime.now(timezone.utc).isoformat()
        current_recommendations: List[SecurityRecommendation] = []

        # Step 5: Lifecycle management & deduplication
        # If returning to BENIGN, transition existing active attack recommendations to RESOLVED
        if curr_stage == "BENIGN" and warning_sev == "INFO":
            for stored_rec in self._recommendations_store.values():
                if stored_rec.priority in ("CRITICAL", "HIGH", "MEDIUM") and stored_rec.status != RecommendationStatus.RESOLVED.value:
                    stored_rec.status = RecommendationStatus.RESOLVED.value
                    stored_rec.updated_at = now_iso

        for r_meta in rule_decisions:
            rule_id = r_meta["rule_id"]
            asset = r_meta["target_asset"]
            priority = r_meta["priority"]

            # Compute deduplication fingerprint
            fingerprint = hashlib.md5(
                f"{rule_id}:{asset}:{priority}:{curr_stage}:{pred_stage}".encode()
            ).hexdigest()

            # Check if this recommendation was already generated and preserved in store
            existing_rec = None
            for stored_id, rec_obj in self._recommendations_store.items():
                if rec_obj.fingerprint == fingerprint:
                    existing_rec = rec_obj
                    break

            if existing_rec:
                # Maintain operator's prior status acknowledgment or resolve state
                rec_id = existing_rec.id
                status = existing_rec.status
                # If an acknowledged rec escalates to CRITICAL, reopen to PENDING
                if existing_rec.priority != priority and priority == "CRITICAL":
                    status = RecommendationStatus.PENDING.value

                rec = SecurityRecommendation(
                    id=rec_id,
                    fingerprint=fingerprint,
                    priority=priority,
                    category=r_meta["category"],
                    title=r_meta["title"],
                    action=r_meta["action"],
                    reason=r_meta["reason"],
                    evidence=evidence_list,
                    source=r_meta["source"],
                    status=status,
                    target_asset=asset,
                    created_at=existing_rec.created_at,
                    updated_at=now_iso,
                    rule_id=rule_id,
                    attack_stage=curr_stage,
                    escalation_window=esc_window,
                    warning_severity=warning_sev,
                )
            else:
                rec_id = f"REC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{self._rec_seq:04d}"
                self._rec_seq += 1
                rec = SecurityRecommendation(
                    id=rec_id,
                    fingerprint=fingerprint,
                    priority=priority,
                    category=r_meta["category"],
                    title=r_meta["title"],
                    action=r_meta["action"],
                    reason=r_meta["reason"],
                    evidence=evidence_list,
                    source=r_meta["source"],
                    status=RecommendationStatus.PENDING.value,
                    target_asset=asset,
                    created_at=now_iso,
                    updated_at=now_iso,
                    rule_id=rule_id,
                    attack_stage=curr_stage,
                    escalation_window=esc_window,
                    warning_severity=warning_sev,
                )

            self._recommendations_store[rec.id] = rec
            current_recommendations.append(rec)

        # Step 6: Compute statistical summary across active recommendations
        summary = RecommendationsSummary()
        summary.total = len(current_recommendations)
        for r in current_recommendations:
            if r.status == RecommendationStatus.PENDING.value:
                summary.pending += 1
            elif r.status == RecommendationStatus.ACKNOWLEDGED.value:
                summary.acknowledged += 1
            elif r.status == RecommendationStatus.RESOLVED.value:
                summary.resolved += 1

            if r.priority == RecommendationPriority.CRITICAL.value:
                summary.critical_count += 1
            elif r.priority == RecommendationPriority.HIGH.value:
                summary.high_count += 1
            elif r.priority == RecommendationPriority.MEDIUM.value:
                summary.medium_count += 1
            elif r.priority == RecommendationPriority.LOW.value:
                summary.low_count += 1

        active_posture = warning_sev if warning_sev != "INFO" else "NORMAL_BASELINE"

        return RecommendationEvaluationResult(
            recommendations_available=len(current_recommendations) > 0,
            recommendations=current_recommendations,
            summary=summary,
            active_threat_posture=active_posture,
            generated_at=now_iso,
            limitations=self.limitations_note,
        )

    def update_recommendation_status(self, recommendation_id: str, new_status: str) -> Optional[SecurityRecommendation]:
        """Update operator status for a specific recommendation (e.g., ACKNOWLEDGED, RESOLVED).

        Args:
            recommendation_id: Target recommendation ID (e.g., 'REC-20260925-0001').
            new_status: Target status ('PENDING', 'ACKNOWLEDGED', 'RESOLVED').

        Returns:
            Updated SecurityRecommendation if found, None otherwise.
        """
        target_status = new_status.upper()
        if target_status not in (RecommendationStatus.PENDING.value, RecommendationStatus.ACKNOWLEDGED.value, RecommendationStatus.RESOLVED.value):
            raise ValueError(f"Invalid recommendation status: {new_status}. Allowed: PENDING, ACKNOWLEDGED, RESOLVED")

        rec = self._recommendations_store.get(recommendation_id)
        if not rec:
            return None

        rec.status = target_status
        rec.updated_at = datetime.now(timezone.utc).isoformat()
        return rec

    def get_recommendation_by_id(self, recommendation_id: str) -> Optional[SecurityRecommendation]:
        """Retrieve single recommendation by its unique ID."""
        return self._recommendations_store.get(recommendation_id)


# Global singleton engine instance
recommendation_engine = RecommendationEngine()


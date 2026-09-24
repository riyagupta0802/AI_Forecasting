"""Core Early Warning Engine for HEX HIVE Phase 9.

Combines outputs from Phase 5 (Detection), Phase 6 (Forecasting), Phase 7 (Escalation),
and Phase 8 (Attack Story Correlated Clusters) to evaluate security conditions,
apply deterministic severity rules, enforce deduplication, and track warning lifecycle.
"""

from collections import deque
from datetime import datetime, timezone
import hashlib
import logging
from typing import Dict, Any, List, Optional

from ml.warning.models import EarlyWarning, WarningEvaluationResult, EvidenceItem
from ml.warning.rules import evaluate_warning_decision
from ml.warning.formatter import (
    format_warning_title,
    format_warning_message,
    format_recommended_attention,
    compile_evidence_items,
)
from ml.attack_story.story import attack_story_engine

logger = logging.getLogger("HEX_HIVE.EarlyWarning.Engine")


class EarlyWarningEngine:
    """Evaluates multi-source security telemetry and issues actionable early warnings."""

    def __init__(self):
        self._history: deque = deque(maxlen=50)
        self._active_warning: Optional[EarlyWarning] = None
        self._warning_seq: int = 1
        self.limitations_note = (
            "Early Warnings are synthesized from deterministic rules applied to "
            "Phase 5 (binary detection), Phase 6 (stage forecasting), Phase 7 (time-to-escalation), "
            "and Phase 8 (correlated flow clusters) from the 500-sample CICIDS2017 aggregate dataset. "
            "Warnings indicate elevated or potentially escalating security conditions requiring attention, "
            "not absolute guarantees of future breach execution."
        )

    def evaluate(
        self,
        sample_context: str = "auto",
        category_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
        event_limit: int = 50,
    ) -> WarningEvaluationResult:
        """Evaluate current security posture and produce a comprehensive warning result.

        Args:
            sample_context: Preset scenario ('auto', 'benign', 'portscan', 'bot', 'ddos').
            category_filter: Optional event category filter.
            severity_filter: Optional severity filter.
            event_limit: Max flow events to process.

        Returns:
            WarningEvaluationResult containing active warning, evidence, and session history.
        """
        # Step 1: Ingest outputs from Phase 8 (which coordinates Phases 5, 6, and 7)
        story = attack_story_engine.generate_story(
            category_filter=category_filter,
            severity_filter=severity_filter,
            sample_context=sample_context,
            event_limit=event_limit,
        )

        forecast_res = story.get("forecast", {})
        escalation_res = story.get("escalation", {})
        clusters = story.get("clusters", [])
        events = story.get("events_sample", [])

        # Step 2: Extract decision inputs with graceful fallbacks
        detection_res = forecast_res.get("detection", {})
        det_state = detection_res.get("prediction", "BENIGN")
        det_conf = float(detection_res.get("confidence", 0.99))

        curr_state = forecast_res.get("current_state", story.get("current_state", "BENIGN"))
        pred_state = forecast_res.get("predicted_stage", "BENIGN")
        fc_conf = float(forecast_res.get("confidence", 0.88))

        esc_seconds = escalation_res.get("estimated_time_seconds")
        esc_window = escalation_res.get("formatted_time", "Not Escalating")
        esc_vel = float(escalation_res.get("velocity_index", 1.0))
        is_escalating = bool(escalation_res.get("is_escalating", False))

        # Extract target ports from clusters and events
        target_ports: List[int] = []
        for c in clusters:
            target_ports.extend(c.get("destination_ports", []))
        if not target_ports:
            for ev in events:
                port = ev.get("destination_port")
                if port and port not in target_ports:
                    target_ports.append(port)
        target_ports = sorted(list(set(target_ports)))

        # Step 3: Evaluate deterministic decision rules
        severity, warning_type, rule_id, rule_rationale = evaluate_warning_decision(
            detection_state=det_state,
            detection_confidence=det_conf,
            forecast_state=curr_state,
            predicted_state=pred_state,
            forecast_confidence=fc_conf,
            escalation_seconds=esc_seconds,
            velocity_index=esc_vel,
            is_escalating=is_escalating,
            target_ports=target_ports,
            cluster_count=len(clusters),
        )

        # Step 4: Synthesize titles, messages, and evidence
        title = format_warning_title(warning_type, severity, curr_state, pred_state)
        message = format_warning_message(warning_type, severity, curr_state, pred_state, esc_window, rule_rationale)
        rec_attention = format_recommended_attention(severity, warning_type, curr_state, target_ports)
        evidence = compile_evidence_items(detection_res, forecast_res, escalation_res, clusters, target_ports)

        # Step 5: Deduplication & Lifecycle Tracking
        ports_key = "-".join(str(p) for p in target_ports[:5])
        fingerprint = hashlib.md5(
            f"{warning_type}:{severity}:{curr_state}:{pred_state}:{ports_key}".encode()
        ).hexdigest()

        now_iso = datetime.now(timezone.utc).isoformat()
        warning_status = "NEW"

        if self._active_warning and self._active_warning.fingerprint == fingerprint:
            # Persistent condition: update lifecycle status to ACTIVE
            warning_id = self._active_warning.warning_id
            warning_status = "ACTIVE"
        else:
            # Different condition: if previous was active and this is normal baseline, resolve previous
            if self._active_warning and self._active_warning.severity != "INFO" and severity == "INFO":
                self._active_warning.status = "RESOLVED"
            warning_id = f"WRN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{self._warning_seq:04d}"
            self._warning_seq += 1

        warning = EarlyWarning(
            warning_id=warning_id,
            fingerprint=fingerprint,
            warning_type=warning_type,
            severity=severity,
            status=warning_status,
            title=title,
            message=message,
            timestamp=now_iso,
            current_state=curr_state,
            predicted_state=pred_state,
            escalation_window=esc_window,
            escalation_seconds=esc_seconds,
            confidence=fc_conf if curr_state != "BENIGN" else det_conf,
            target_ports=target_ports,
            evidence=evidence,
            recommended_attention=rec_attention,
            limitations=self.limitations_note,
        )

        self._active_warning = warning

        # Add to history if not an exact immediate duplicate
        if not self._history or self._history[-1].fingerprint != fingerprint:
            self._history.append(warning)

        # Overall risk level mirrors active warning severity
        has_active = severity in ("CRITICAL", "HIGH", "MEDIUM", "LOW")

        return WarningEvaluationResult(
            has_active_warning=has_active,
            active_warning=warning,
            warning_count=1 if has_active else 0,
            warnings=[warning] if has_active else [],
            session_history=list(self._history),
            overall_risk_level=severity,
            evaluated_at=now_iso,
            limitations=self.limitations_note,
        )

    def get_history(self) -> List[EarlyWarning]:
        """Return the recent in-memory warning history."""
        return list(self._history)


# Global singleton instance
early_warning_engine = EarlyWarningEngine()


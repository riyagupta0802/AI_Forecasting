"""Dataset Ingestion, Preprocessing, and Multi-Phase Analysis Engine for NETORACLE.

Connects the ingested network traffic dataset through:
1. Column Schema Validation (78 CICIDS2017 continuous features)
2. Phase 4 Preprocessing & StandardScaler transformation
3. Phase 5 Real Random Forest binary attack classification
4. Phase 6 Multi-class stage classification & Kill Chain forecasting
5. Phase 7 Time-to-Escalation velocity regression & estimation
6. Phase 8 Attack Story correlation & narrative generation
7. Phase 9 Early Warning evaluation on detected evidence
8. Phase 10 Defensive Recommendation generation
9. Phase 11 SHAP TreeExplainer feature attribution
"""

from datetime import datetime, timezone
import io
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd

from ml.predictions.predict import predictor
from ml.forecasting.predict import forecaster
from ml.escalation.model import TimeToEscalationEngine
from ml.explainability import attack_explainer
from ml.attack_story.events import NetworkSecurityEvent, _resolve_service_name, SEVERITY_MAP
from ml.attack_story.correlation import EventCorrelator
from ml.attack_story.timeline import ChronologicalTimelineBuilder
from ml.warning.rules import evaluate_warning_decision
from ml.warning.formatter import format_warning_title, format_warning_message, format_recommended_attention, compile_evidence_items
from ml.warning.models import EarlyWarning
from ml.recommendations.rules import evaluate_recommendation_rules
from ml.recommendations.formatter import compile_recommendation_evidence
from ml.recommendations.models import SecurityRecommendation, RecommendationsSummary

logger = logging.getLogger("NETORACLE.DatasetAnalyzer")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = REPO_ROOT / "ml" / "data"
META_PATH = DATA_DIR / "processed" / "preprocessing_meta.json"
LOCAL_SAMPLE_PATH = DATA_DIR / "sample" / "cicids2017_sample.csv"
CLASSIFIER_PATH = REPO_ROOT / "ml" / "models" / "attack_classifier.joblib"
STAGE_CLASSIFIER_PATH = REPO_ROOT / "ml" / "models" / "forecast_stage_classifier.joblib"
ESCALATION_MODEL_PATH = REPO_ROOT / "ml" / "models" / "escalation_model.joblib"


class DatasetAnalyzerService:
    """Production service orchestrating end-to-end dataset analysis through Phase 5–11."""

    def __init__(self):
        self.feature_names: List[str] = []
        self.scaler_mean: Optional[np.ndarray] = None
        self.scaler_scale: Optional[np.ndarray] = None
        self.classifier = None
        self.stage_classifier = None
        self.escalation_engine = TimeToEscalationEngine()
        self._load_metadata_and_models()

    def _load_metadata_and_models(self):
        """Load feature metadata, scaler statistics, and trained model artifacts."""
        try:
            if META_PATH.is_file():
                with open(META_PATH, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    self.feature_names = meta.get("features", [])
                    means = meta.get("scaler_mean", [])
                    scales = meta.get("scaler_scale", [])
                    if means and scales:
                        self.scaler_mean = np.array(means, dtype=float)
                        self.scaler_scale = np.array(scales, dtype=float)
                        self.scaler_scale[self.scaler_scale == 0] = 1.0

            if CLASSIFIER_PATH.is_file():
                self.classifier = joblib.load(CLASSIFIER_PATH)

            if STAGE_CLASSIFIER_PATH.is_file():
                self.stage_classifier = joblib.load(STAGE_CLASSIFIER_PATH)

            if ESCALATION_MODEL_PATH.is_file():
                self.escalation_engine.model = joblib.load(ESCALATION_MODEL_PATH)

            logger.info(
                "DatasetAnalyzer initialized with %d features. Classifier ready: %s. Stage ready: %s",
                len(self.feature_names),
                self.classifier is not None,
                self.stage_classifier is not None,
            )
        except Exception as e:
            logger.error("Error loading model artifacts: %s", e)

    def validate_columns(self, df: pd.DataFrame, filename: str = "dataset.csv") -> Dict[str, Any]:
        """Inspect and compare dataset columns with the required 78 Phase 5 model features.

        Args:
            df: Raw input DataFrame.
            filename: File name for display.

        Returns:
            Dictionary matching DatasetValidationResult schema.
        """
        # Clean column headers
        stripped_cols = [str(c).strip() for c in df.columns]
        df_cols_set = set(stripped_cols)

        available_features = [f for f in self.feature_names if f in df_cols_set]
        missing_features = [f for f in self.feature_names if f not in df_cols_set]
        extra_columns = [col for col in stripped_cols if col not in self.feature_names]

        is_compatible = len(missing_features) == 0

        if is_compatible:
            msg = f"Dataset validated ✓ Records: {len(df):,} Required features: available. Ready for analysis."
        else:
            msg = f"Dataset is not compatible with the current model. Missing {len(missing_features)} required features."

        return {
            "filename": filename,
            "record_count": len(df),
            "required_feature_count": len(self.feature_names),
            "available_required_count": len(available_features),
            "is_compatible": is_compatible,
            "available_features": available_features,
            "missing_features": missing_features,
            "extra_columns": extra_columns,
            "message": msg,
        }

    def preprocess_dataset(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Clean and scale raw dataset records using Phase 4 pipeline parameters.

        Args:
            df: Input raw DataFrame with clean column headers.

        Returns:
            Tuple of (raw_features_df, scaled_features_df).
        """
        # Ensure column whitespace is stripped
        df.columns = df.columns.str.strip()

        # Select the 78 required features
        X_raw = df[self.feature_names].copy()

        # Replace infinities and impute missing values with 0.0
        X_clean = X_raw.replace([np.inf, -np.inf], np.nan).fillna(0.0)

        # Apply StandardScaler transformation using stored parameters
        if self.scaler_mean is not None and self.scaler_scale is not None:
            raw_vals = X_clean.values.astype(float)
            scaled_vals = (raw_vals - self.scaler_mean) / self.scaler_scale
            df_scaled = pd.DataFrame(scaled_vals, columns=self.feature_names, index=df.index)
        else:
            df_scaled = X_clean

        return X_clean, df_scaled

    def analyze_dataset(
        self,
        df_or_path: Union[pd.DataFrame, str, Path],
        filename: str = "uploaded_dataset.csv",
        source_type: str = "Uploaded Dataset",
    ) -> Dict[str, Any]:
        """Execute the complete Phase 5–11 analysis pipeline on the provided dataset.

        Args:
            df_or_path: Input DataFrame or path to CSV file.
            filename: User-facing file label.
            source_type: 'Uploaded Dataset' or 'Local Test Dataset'.

        Returns:
            Structured dictionary matching AnalyzeResponse.
        """
        if not self.classifier:
            self._load_metadata_and_models()
            if not self.classifier:
                raise RuntimeError("Phase 5 Random Forest classifier is not loaded.")

        # 1. Load data
        if isinstance(df_or_path, (str, Path)):
            df = pd.read_csv(df_or_path)
        elif isinstance(df_or_path, pd.DataFrame):
            df = df_or_path.copy()
        else:
            raise ValueError(f"Unsupported data input: {type(df_or_path)}")

        if df.empty:
            raise ValueError("Dataset contains no records.")

        # 2. Validate columns
        validation = self.validate_columns(df, filename=filename)
        if not validation["is_compatible"]:
            raise ValueError(
                f"Dataset incompatible with model schema. Missing features: {', '.join(validation['missing_features'][:5])}..."
            )

        # 3. Preprocess and Scale
        X_clean, df_scaled = self.preprocess_dataset(df)
        total_records = len(df_scaled)

        # 4. Phase 5: Attack Detection (Random Forest Inference)
        preds = self.classifier.predict(df_scaled)
        probas = self.classifier.predict_proba(df_scaled)

        benign_count = int((preds == 0).sum())
        attack_count = int((preds == 1).sum())
        attack_percentage = round((attack_count / total_records) * 100, 2)
        avg_confidence = round(float(np.mean(np.max(probas, axis=1))) * 100, 1)

        # 5. Phase 6: Stage Classification & Transition Forecasting
        stage_names = {0: "BENIGN", 1: "Bot", 2: "DDoS", 3: "PortScan"}
        stage_distribution = {"BENIGN": benign_count, "Bot": 0, "DDoS": 0, "PortScan": 0}

        if self.stage_classifier is not None:
            stage_preds = self.stage_classifier.predict(df_scaled)
            for code, name in stage_names.items():
                stage_distribution[name] = int((stage_preds == code).sum())

        # Determine dominant attack stage (excluding BENIGN)
        attack_stage_counts = {k: v for k, v in stage_distribution.items() if k != "BENIGN"}
        dominant_attack_stage = None
        if attack_count > 0 and attack_stage_counts:
            dominant_attack_stage = max(attack_stage_counts, key=attack_stage_counts.get)
            if attack_stage_counts[dominant_attack_stage] == 0:
                dominant_attack_stage = "PortScan"
        else:
            dominant_attack_stage = "BENIGN"

        # Generate Phase 6 Transition Forecast
        forecast_confidence = avg_confidence
        if attack_count > 0:
            current_stage_name = dominant_attack_stage
            forecast_res = forecaster.forecasting_model.predict_transition(
                current_stage=current_stage_name,
                current_confidence=forecast_confidence,
                features_df=df_scaled,
            )
        else:
            current_stage_name = "BENIGN"
            forecast_res = {
                "forecast_available": True,
                "status": "active",
                "current_state": "BENIGN",
                "current_state_desc": "Normal Baseline Traffic",
                "predicted_next_stage": "Normal Traffic Operation",
                "predicted_next_stage_display": "BENIGN (Normal Baseline)",
                "confidence": avg_confidence,
                "risk_level": "LOW",
                "model": "StageClassifier + EmpiricalKillChainTransition",
                "explanation": "All evaluated records match standard benign network traffic baseline.",
            }

        # 6. Phase 7: Time-to-Escalation Estimation
        if attack_count > 0:
            attack_mask = preds == 1
            attack_df = df_scaled[attack_mask]
            predicted_stage = forecast_res.get("predicted_next_stage", "Botnet Propagation")

            escalation_res = self.escalation_engine.estimate(
                current_state=dominant_attack_stage,
                predicted_state=predicted_stage,
                confidence=forecast_confidence,
                features_df=attack_df,
            )
        else:
            escalation_res = {
                "available": True,
                "current_state": "BENIGN",
                "predicted_state": "BENIGN",
                "escalation_condition": "Baseline traffic; no active intrusion escalation pattern detected",
                "is_escalating": False,
                "formatted_time": "Not Escalating",
                "risk_level": "LOW",
                "confidence": avg_confidence,
                "velocity_index": 1.0,
                "method": "TelemetryVelocityCalibratedProgression",
                "explanation": "No escalating threat detected in dataset (100% benign flows).",
            }

        # 7. Phase 8: Attack Story from Actual Dataset Flows
        attack_story_res = self._build_attack_story(
            df_raw=df,
            preds=preds,
            probas=probas,
            dominant_stage=dominant_attack_stage,
            forecast_res=forecast_res,
            escalation_res=escalation_res,
        )

        # 8. Phase 9: Early Warning Engine
        early_warning_res = self._build_early_warning(
            attack_count=attack_count,
            dominant_stage=dominant_attack_stage,
            forecast_res=forecast_res,
            escalation_res=escalation_res,
            target_ports=attack_story_res.get("target_ports", [80, 443]),
        )

        # 9. Phase 10: Defensive Recommendations
        recommendations_res = self._build_recommendations(
            attack_count=attack_count,
            dominant_stage=dominant_attack_stage,
            forecast_res=forecast_res,
            escalation_res=escalation_res,
            target_ports=attack_story_res.get("target_ports", [80, 443]),
        )

        # 10. Phase 11: SHAP Explainability on Representative Sample
        explainability_res = self._build_explainability(
            df_scaled=df_scaled,
            preds=preds,
            probas=probas,
            attack_count=attack_count,
        )

        # 11. Calculate Overall Dynamic Risk Score (0–100)
        # Weight attack percentage and severity level
        if attack_count == 0:
            risk_score = 5
            risk_level = "LOW"
        else:
            base_risk = min(85, int(attack_percentage * 0.8))
            sev_multiplier = {"PortScan": 10, "Bot": 15, "DDoS": 20}.get(dominant_attack_stage, 10)
            risk_score = min(100, base_risk + sev_multiplier)
            if risk_score >= 70:
                risk_level = "CRITICAL"
            elif risk_score >= 50:
                risk_level = "HIGH"
            elif risk_score >= 30:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

        # 12. Build UI Sample Prediction rows (up to 30 records for inspection)
        sample_predictions = self._build_sample_predictions(df, preds, probas)

        analysis_timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "success": True,
            "dataset_name": filename,
            "source_type": source_type,
            "total_records": total_records,
            "benign_count": benign_count,
            "attack_count": attack_count,
            "attack_percentage": attack_percentage,
            "average_confidence": avg_confidence,
            "analysis_timestamp": analysis_timestamp,
            "model": "Phase 5 Random Forest Classifier (100 Trees, 78 Features)",
            "stage_distribution": stage_distribution,
            "dominant_attack_stage": dominant_attack_stage,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "sample_predictions": sample_predictions,
            "forecast": forecast_res,
            "escalation": escalation_res,
            "attack_story": attack_story_res,
            "early_warning": early_warning_res,
            "recommendations": recommendations_res,
            "explainability": explainability_res,
        }

    def _build_sample_predictions(
        self, df: pd.DataFrame, preds: np.ndarray, probas: np.ndarray, max_samples: int = 30
    ) -> List[Dict[str, Any]]:
        """Construct preview predictions from the analyzed records."""
        samples = []
        n = min(len(df), max_samples)

        dest_port_col = None
        duration_col = None
        packets_col = None

        for c in df.columns:
            sc = c.strip()
            if sc == "Destination Port":
                dest_port_col = c
            elif sc == "Flow Duration":
                duration_col = c
            elif sc == "Total Fwd Packets":
                packets_col = c

        for i in range(n):
            is_atk = bool(preds[i] == 1)
            b_prob = round(float(probas[i][0]) * 100, 1)
            a_prob = round(float(probas[i][1]) * 100, 1) if probas.shape[1] > 1 else 0.0
            conf = a_prob if is_atk else b_prob

            port_val = int(df[dest_port_col].iloc[i]) if dest_port_col else None
            dur_val = round(float(df[duration_col].iloc[i]) / 1000.0, 2) if duration_col else None
            pkt_val = int(df[packets_col].iloc[i]) if packets_col else None

            samples.append({
                "index": i + 1,
                "prediction": "ATTACK" if is_atk else "BENIGN",
                "is_attack": is_atk,
                "confidence": conf,
                "benign_probability": b_prob,
                "attack_probability": a_prob,
                "destination_port": port_val,
                "flow_duration": dur_val,
                "total_packets": pkt_val,
            })
        return samples

    def _build_attack_story(
        self,
        df_raw: pd.DataFrame,
        preds: np.ndarray,
        probas: np.ndarray,
        dominant_stage: str,
        forecast_res: Dict[str, Any],
        escalation_res: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Correlate actual dataset flows into a chronological attack story."""
        events: List[NetworkSecurityEvent] = []
        dest_ports: List[int] = []

        port_col = "Destination Port" if "Destination Port" in df_raw.columns else None
        dur_col = "Flow Duration" if "Flow Duration" in df_raw.columns else None
        fwd_pkt_col = "Total Fwd Packets" if "Total Fwd Packets" in df_raw.columns else None
        bwd_pkt_col = "Total Backward Packets" if "Total Backward Packets" in df_raw.columns else None
        fwd_bytes_col = "Total Length of Fwd Packets" if "Total Length of Fwd Packets" in df_raw.columns else None
        bwd_bytes_col = "Total Length of Bwd Packets" if "Total Length of Bwd Packets" in df_raw.columns else None

        cum_time_s = 0.0
        limit = min(len(df_raw), 50)

        for i in range(limit):
            port = int(df_raw[port_col].iloc[i]) if port_col else 80
            dur_ms = float(df_raw[dur_col].iloc[i]) / 1000.0 if dur_col else 100.0
            cum_time_s += max(0.01, dur_ms / 1000.0)

            fwd_pkts = int(df_raw[fwd_pkt_col].iloc[i]) if fwd_pkt_col else 1
            bwd_pkts = int(df_raw[bwd_pkt_col].iloc[i]) if bwd_pkt_col else 0
            total_pkts = fwd_pkts + bwd_pkts

            fwd_b = int(df_raw[fwd_bytes_col].iloc[i]) if fwd_bytes_col else 64
            bwd_b = int(df_raw[bwd_bytes_col].iloc[i]) if bwd_bytes_col else 0
            total_b = fwd_b + bwd_b

            is_atk = bool(preds[i] == 1)
            cat = dominant_stage if is_atk else "BENIGN"
            sev = SEVERITY_MAP.get(cat, "LOW")
            service = _resolve_service_name(port)

            if is_atk and port not in dest_ports:
                dest_ports.append(port)

            desc = f"{'Malicious' if is_atk else 'Standard'} flow targeting {service} ({total_pkts} pkts, {dur_ms:.1f}ms)."

            events.append(
                NetworkSecurityEvent(
                    event_id=f"EVT-{i+1:04d}",
                    sequence_index=i + 1,
                    destination_port=port,
                    service_name=service,
                    protocol="TCP",
                    duration_ms=dur_ms,
                    packet_count=total_pkts,
                    byte_count=total_b,
                    flow_packets_sec=round(total_pkts / max(0.001, dur_ms / 1000.0), 2),
                    flow_bytes_sec=round(total_b / max(0.001, dur_ms / 1000.0), 2),
                    syn_flag_count=1 if is_atk else 0,
                    ack_flag_count=1,
                    attack_category=cat,
                    severity=sev,
                    relative_time_s=round(cum_time_s, 2),
                    description=desc,
                )
            )

        correlator = EventCorrelator()
        clusters = correlator.correlate(events)

        timeline_builder = ChronologicalTimelineBuilder()
        timeline_nodes = timeline_builder.build_timeline(
            clusters=clusters,
            current_state=dominant_stage,
            forecast_context=forecast_res,
            escalation_context=escalation_res,
        )

        return {
            "story_available": True,
            "events_count": len(events),
            "clusters_count": len(clusters),
            "target_ports": dest_ports or [80, 443],
            "timeline": [node.to_dict() for node in timeline_nodes],
            "clusters": [cluster.to_dict() for cluster in clusters],
            "narrative_summary": f"Observed {len(events)} flow events across {len(clusters)} correlated cluster(s). Primary pattern: {dominant_stage}.",
        }

    def _build_early_warning(
        self,
        attack_count: int,
        dominant_stage: str,
        forecast_res: Dict[str, Any],
        escalation_res: Dict[str, Any],
        target_ports: List[int],
    ) -> Dict[str, Any]:
        """Synthesize early warning alerts from model predictions."""
        det_state = "ATTACK" if attack_count > 0 else "BENIGN"
        curr_state = dominant_stage if attack_count > 0 else "BENIGN"
        pred_state = forecast_res.get("predicted_next_stage", "BENIGN")
        fc_conf = float(forecast_res.get("confidence", 85.0)) / 100.0
        det_conf = fc_conf
        is_escalating = bool(escalation_res.get("is_escalating", False))
        esc_seconds = escalation_res.get("estimated_time_seconds")
        esc_window = escalation_res.get("formatted_time", "Not Escalating")
        esc_vel = float(escalation_res.get("velocity_index", 1.0))

        sev, w_type, rule_id, rationale = evaluate_warning_decision(
            detection_state=det_state,
            detection_confidence=det_conf,
            forecast_state=curr_state,
            predicted_state=pred_state,
            forecast_confidence=fc_conf,
            escalation_seconds=esc_seconds,
            velocity_index=esc_vel,
            is_escalating=is_escalating,
            target_ports=target_ports,
            cluster_count=1 if attack_count > 0 else 0,
        )

        title = format_warning_title(w_type, sev, curr_state, pred_state)
        msg = format_warning_message(w_type, sev, curr_state, pred_state, esc_window, rationale)
        recs = format_recommended_attention(sev, w_type, curr_state, target_ports)

        evidence = compile_evidence_items(
            detection_res={"prediction": det_state, "confidence": det_conf},
            forecast_res=forecast_res,
            escalation_res=escalation_res,
            clusters=[],
            target_ports=target_ports,
        )

        active_w_dict = {
            "severity": sev,
            "warning_type": w_type,
            "title": title,
            "message": msg,
            "rationale": rationale,
            "rule_id": rule_id,
            "recommended_attention": recs,
            "evidence": [e.to_dict() for e in evidence],
            "is_escalating": is_escalating,
        }

        return {
            "warning_available": True,
            "has_active_warning": attack_count > 0,
            "active_warning": active_w_dict,
            "severity": sev,
            "warning_type": w_type,
            "title": title,
            "message": msg,
            "rationale": rationale,
            "rule_id": rule_id,
            "recommended_attention": recs,
            "evidence": [e.to_dict() for e in evidence],
            "is_escalating": is_escalating,
        }

    def _build_recommendations(
        self,
        attack_count: int,
        dominant_stage: str,
        forecast_res: Dict[str, Any],
        escalation_res: Dict[str, Any],
        target_ports: List[int],
    ) -> Dict[str, Any]:
        """Generate defensive action playbooks based on actual detected conditions."""
        det_state = "ATTACK" if attack_count > 0 else "BENIGN"
        curr_state = dominant_stage if attack_count > 0 else "BENIGN"
        pred_state = forecast_res.get("predicted_next_stage", "BENIGN")
        fc_conf = float(forecast_res.get("confidence", 85.0)) / 100.0
        det_conf = fc_conf
        is_escalating = bool(escalation_res.get("is_escalating", False))
        esc_seconds = escalation_res.get("estimated_time_seconds")
        esc_window = escalation_res.get("formatted_time", "Not Escalating")
        esc_vel = float(escalation_res.get("velocity_index", 1.0))

        # Use warning evaluation context
        w_sev = "CRITICAL" if attack_count > 50 else ("HIGH" if attack_count > 0 else "INFO")
        w_type = f"{dominant_stage}_ELEVATED" if attack_count > 0 else "NORMAL_BASELINE"

        rule_recs = evaluate_recommendation_rules(
            detection_state=det_state,
            detection_confidence=det_conf,
            current_stage=curr_state,
            predicted_stage=pred_state,
            forecast_confidence=fc_conf,
            escalation_seconds=esc_seconds,
            escalation_window=esc_window,
            velocity_index=esc_vel,
            warning_severity=w_sev,
            warning_type=w_type,
            target_ports=target_ports,
            cluster_count=1 if attack_count > 0 else 0,
        )

        return {
            "recommendations_available": True,
            "total_recommendations": len(rule_recs),
            "recommendations": rule_recs,
            "target_ports": target_ports,
            "summary": f"Generated {len(rule_recs)} defensive recommendations for detected {curr_state} condition.",
        }

    def _build_explainability(
        self,
        df_scaled: pd.DataFrame,
        preds: np.ndarray,
        probas: np.ndarray,
        attack_count: int,
    ) -> Dict[str, Any]:
        """Run real SHAP TreeExplainer on the most representative flow from the dataset."""
        if attack_count > 0:
            # Pick the attack record with highest attack probability
            attack_indices = np.where(preds == 1)[0]
            if len(attack_indices) > 0:
                attack_probas = probas[attack_indices, 1]
                best_idx = attack_indices[np.argmax(attack_probas)]
            else:
                best_idx = 0
        else:
            best_idx = 0

        representative_flow = df_scaled.iloc[best_idx].values
        explanation = attack_explainer.explain_instance(features=representative_flow, top_n=6)
        return explanation.to_dict()


# Global singleton service
dataset_analyzer = DatasetAnalyzerService()

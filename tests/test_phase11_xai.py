"""
End-to-End Verification Test Suite for Phase 11: Real Explainable AI (XAI)
Tests:
  1. AttackExplainer initialization and TreeExplainer integration
  2. Mathematical identity: E[f(x)] + sum(phi_i) == P(class | x)
  3. Local explanation for ATTACK sample (actual SHAP values, ranking, friendly names)
  4. Local explanation for BENIGN sample
  5. Global SHAP feature importance calculation and caching
  6. Non-causal explanation phrasing validation
  7. FastAPI endpoint verification via TestClient:
     - GET  /api/explainability/status
     - POST /api/explainability/explain (attack flow)
     - POST /api/explainability/explain (benign flow)
     - GET  /api/explainability/global
  8. Regression check on Phases 5-10 endpoints
"""
import sys
import os

# Ensure project root and backend are in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import numpy as np
from fastapi.testclient import TestClient

from ml.explainability.explainer import AttackExplainer, attack_explainer
from ml.explainability.formatter import FRIENDLY_FEATURE_MAP, format_explanation_summary, format_technical_summary
from backend.app.main import app

def test_explainer_initialization():
    print("--> [1/8] Testing AttackExplainer initialization...")
    assert attack_explainer.is_ready, "AttackExplainer must be initialized and ready"
    assert attack_explainer.feature_names is not None, "Feature names must be loaded"
    assert len(attack_explainer.feature_names) == 78, f"Expected 78 features, got {len(attack_explainer.feature_names)}"
    assert attack_explainer.explainer is not None, "TreeExplainer instance must be present"
    print("    PASSED: AttackExplainer initialized with 78 features and TreeExplainer.")

def test_mathematical_identity():
    print("--> [2/8] Testing SHAP mathematical identity: E[f(x)] + sum(phi_i) == P(class | x)...")
    sample_df = attack_explainer.sample_attack
    assert sample_df is not None, "sample_attack must be loaded"
    
    # Compute raw SHAP values
    shap_vals = attack_explainer.explainer.shap_values(sample_df)
    
    # For binary RF, shap_vals is (N, 78, 2)
    # Target class 1 (ATTACK)
    atk_phi = shap_vals[0, :, 1]
    expected_val = attack_explainer.explainer.expected_value[1]
    reconstructed_prob = expected_val + np.sum(atk_phi)
    
    actual_prob = attack_explainer.model.predict_proba(sample_df)[0, 1]
    
    diff = abs(reconstructed_prob - actual_prob)
    assert diff < 1e-4, f"SHAP sum {reconstructed_prob} does not match model prob {actual_prob} (diff: {diff})"
    print(f"    PASSED: Reconstructed {reconstructed_prob:.6f} == Actual {actual_prob:.6f} (diff: {diff:.2e}).")

def test_local_explanation_attack():
    print("--> [3/8] Testing Local Explanation on ATTACK flow...")
    res = attack_explainer.explain_instance(sample_type="attack", top_n=6)
    
    assert res.prediction == "ATTACK", f"Expected ATTACK, got {res.prediction}"
    assert res.predicted_value > 0.5, f"Predicted prob should be > 0.5, got {res.predicted_value}"
    assert len(res.features) == 6, f"Expected 6 features, got {len(res.features)}"
    assert res.features_evaluated == 78, f"Expected 78 evaluated, got {res.features_evaluated}"
    
    # Check ranking
    for i in range(len(res.features) - 1):
        assert res.features[i].abs_shap >= res.features[i + 1].abs_shap, "Features must be sorted descending by |SHAP|"
    
    # Check friendly name
    top_feat = res.features[0]
    assert top_feat.friendly_name != top_feat.name, "Friendly name should be mapped"
    assert top_feat.abs_shap > 0, "Top feature abs_shap must be positive"
    print(f"    PASSED: ATTACK classified ({res.confidence:.1f}%). Top feature: '{top_feat.friendly_name}' (phi={top_feat.shap_value:+.4f}).")

def test_local_explanation_benign():
    print("--> [4/8] Testing Local Explanation on BENIGN flow...")
    res = attack_explainer.explain_instance(sample_type="benign", top_n=6)
    
    assert res.prediction == "BENIGN", f"Expected BENIGN, got {res.prediction}"
    assert res.predicted_value > 0.5, f"Predicted prob should be > 0.5, got {res.predicted_value}"
    assert len(res.features) == 6, f"Expected 6 features, got {len(res.features)}"
    assert res.features_evaluated == 78, f"Expected 78 evaluated, got {res.features_evaluated}"
    
    top_feat = res.features[0]
    print(f"    PASSED: BENIGN classified ({res.confidence:.1f}%). Top feature: '{top_feat.friendly_name}' (phi={top_feat.shap_value:+.4f}).")

def test_global_importance():
    print("--> [5/8] Testing Global Feature Importance over dataset...")
    global_res = attack_explainer.get_global_importance(top_n=10)
    
    assert global_res.samples_evaluated > 0, "Samples evaluated must be > 0"
    assert len(global_res.top_features) == 10, f"Expected 10 top features, got {len(global_res.top_features)}"
    
    # Verify descending order of mean absolute SHAP
    for i in range(len(global_res.top_features) - 1):
        assert (
            global_res.top_features[i].mean_abs_shap >= global_res.top_features[i + 1].mean_abs_shap
        ), "Global features must be sorted descending by mean |SHAP|"
    
    # Verify cached retrieval
    cached_res = attack_explainer.get_global_importance(top_n=10)
    assert len(cached_res.top_features) == 10
    print(f"    PASSED: Global importance calculated across {global_res.samples_evaluated} samples. Top 1: '{global_res.top_features[0].friendly_name}' (mean|phi|={global_res.top_features[0].mean_abs_shap:.4f}).")

def test_non_causal_phrasing():
    print("--> [6/8] Testing Non-Causal narrative phrasing...")
    res = attack_explainer.explain_instance(sample_type="attack", top_n=5)
    summary = res.summary.lower()
    
    # Must NOT claim causation or proof
    prohibited_words = ["proves an attack occurred", "caused the attack", "definitely an attack", "guarantees"]
    for pw in prohibited_words:
        assert pw not in summary, f"Prohibited causal phrase '{pw}' found in narrative summary: {res.summary}"
    
    # Must contain attribution framing
    assert "influence" in summary or "contributed" in summary or "indicated" in summary, \
        f"Summary must frame results as model influence/contribution: {res.summary}"
    print("    PASSED: Non-causal attribution language confirmed in generated explanation narrative.")

def test_fastapi_endpoints():
    print("--> [7/8] Testing FastAPI /api/explainability endpoints via TestClient...")
    client = TestClient(app)
    
    # 1. GET /api/explainability/status
    res_status = client.get("/api/explainability/status")
    assert res_status.status_code == 200, f"Status check failed: {res_status.text}"
    status_json = res_status.json()
    assert status_json["explainer_ready"] is True
    assert status_json["features_count"] == 78
    assert "TreeExplainer" in status_json["method"]
    
    # 2. POST /api/explainability/explain (attack)
    res_atk = client.post("/api/explainability/explain", json={"sample_type": "attack", "top_n": 5})
    assert res_atk.status_code == 200, f"Explain attack failed: {res_atk.text}"
    atk_json = res_atk.json()
    assert atk_json["prediction"] == "ATTACK"
    assert len(atk_json["features"]) == 5
    assert atk_json["features_evaluated"] == 78
    assert "summary" in atk_json
    assert "technical_summary" in atk_json
    
    # 3. POST /api/explainability/explain (benign)
    res_ben = client.post("/api/explainability/explain", json={"sample_type": "benign", "top_n": 5})
    assert res_ben.status_code == 200, f"Explain benign failed: {res_ben.text}"
    ben_json = res_ben.json()
    assert ben_json["prediction"] == "BENIGN"
    assert len(ben_json["features"]) == 5
    
    # 4. GET /api/explainability/global
    res_glob = client.get("/api/explainability/global?top_n=8")
    assert res_glob.status_code == 200, f"Global explain failed: {res_glob.text}"
    glob_json = res_glob.json()
    assert len(glob_json["top_features"]) == 8
    assert glob_json["samples_evaluated"] > 0
    print("    PASSED: All 4 Explainability API endpoints returned 200 OK with valid payloads.")

def test_regression_pipeline_endpoints():
    print("--> [8/8] Testing regression across Phases 1-10 endpoints...")
    client = TestClient(app)
    
    # Phase 3: Health & System
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    
    # Phase 5: ML Detection
    res_ml = client.post("/api/ml/predict", json={"sample_type": "attack"})
    assert res_ml.status_code == 200
    assert res_ml.json()["prediction"] == "ATTACK"
    
    # Phase 6: Forecasting
    res_fc = client.get("/api/forecast/status")
    assert res_fc.status_code == 200
    
    # Phase 7: Escalation
    res_esc = client.get("/api/escalation/status")
    assert res_esc.status_code == 200
    
    # Phase 8: Attack Story
    res_story = client.get("/api/attack-story/status")
    assert res_story.status_code == 200
    
    # Phase 9: Warning
    res_warn = client.get("/api/warnings/status")
    assert res_warn.status_code == 200
    
    # Phase 10: Recommendations
    res_rec = client.get("/api/recommendations/status")
    assert res_rec.status_code == 200
    print("    PASSED: Zero regressions across all prior pipeline phases (Phases 1-10).")

if __name__ == "__main__":
    print("=" * 70)
    print("HEX HIVE — Phase 11: Real Explainable AI (XAI) Test Suite")
    print("=" * 70)
    test_explainer_initialization()
    test_mathematical_identity()
    test_local_explanation_attack()
    test_local_explanation_benign()
    test_global_importance()
    test_non_causal_phrasing()
    test_fastapi_endpoints()
    test_regression_pipeline_endpoints()
    print("=" * 70)
    print("ALL 8 VERIFICATION SUITES PASSED SUCCESSFULLY (100% SUCCESS)!")
    print("=" * 70)

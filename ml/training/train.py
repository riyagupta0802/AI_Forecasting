"""Random Forest Attack Classification Training Pipeline for HEX HIVE Phase 5.

Loads Phase 4 preprocessed flow feature matrices, maps multi-class attack categories
into binary classes (BENIGN=0, ATTACK=1), trains a RandomForestClassifier,
evaluates performance on an isolated test set, and serializes the model and metrics.
"""

from pathlib import Path
import json
import logging
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    classification_report,
)
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HEX_HIVE.Training")

# Directory setup
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "ml" / "data" / "processed"
MODELS_DIR = REPO_ROOT / "ml" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def train_attack_classifier(
    features_csv: Path = None,
    labels_csv: Path = None,
    meta_json: Path = None,
    model_output: Path = None,
    metrics_output: Path = None,
    random_state: int = 42,
    test_size: float = 0.20,
) -> dict:
    """Train and evaluate the Random Forest binary attack classifier.

    Args:
        features_csv: Path to train_features.csv
        labels_csv: Path to train_labels.csv
        meta_json: Path to preprocessing_meta.json
        model_output: Destination path for .joblib model
        metrics_output: Destination path for .json metrics
        random_state: Reproducible seed
        test_size: Fraction of samples for test evaluation

    Returns:
        Dictionary containing calculated test metrics and evaluation summary.
    """
    if features_csv is None:
        features_csv = DATA_DIR / "train_features.csv"
    if labels_csv is None:
        labels_csv = DATA_DIR / "train_labels.csv"
    if meta_json is None:
        meta_json = DATA_DIR / "preprocessing_meta.json"
    if model_output is None:
        model_output = MODELS_DIR / "attack_classifier.joblib"
    if metrics_output is None:
        metrics_output = MODELS_DIR / "model_metrics.json"

    logger.info("Loading preprocessed feature data from: %s", features_csv)
    X = pd.read_csv(features_csv)
    y_raw = pd.read_csv(labels_csv)

    # In Phase 4, label column was named 'Label'
    y_series = y_raw["Label"] if "Label" in y_raw.columns else y_raw.iloc[:, 0]

    # Binary conversion:
    # 0 = BENIGN -> 0 (BENIGN)
    # >0 = (Bot=1, DDoS=2, PortScan=3) -> 1 (ATTACK)
    y_binary = (y_series > 0).astype(int)

    benign_count = int((y_binary == 0).sum())
    attack_count = int((y_binary == 1).sum())
    total_samples = len(y_binary)

    logger.info(
        "Binary label distribution: Total=%d | BENIGN=%d (%.1f%%) | ATTACK=%d (%.1f%%)",
        total_samples,
        benign_count,
        (benign_count / total_samples) * 100,
        attack_count,
        (attack_count / total_samples) * 100,
    )

    # Load feature names
    feature_names = X.columns.tolist()
    if meta_json.is_file():
        with open(meta_json, "r", encoding="utf-8") as f:
            meta = json.load(f)
            feature_names = meta.get("features", feature_names)

    # Reproducible Stratified Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y_binary,
        test_size=test_size,
        random_state=random_state,
        stratify=y_binary,
    )

    train_benign = int((y_train == 0).sum())
    train_attack = int((y_train == 1).sum())
    test_benign = int((y_test == 0).sum())
    test_attack = int((y_test == 1).sum())

    logger.info(
        "Train set: %d samples (BENIGN=%d, ATTACK=%d) | Test set: %d samples (BENIGN=%d, ATTACK=%d)",
        len(X_train),
        train_benign,
        train_attack,
        len(X_test),
        test_benign,
        test_attack,
    )

    # Train Random Forest Classifier
    logger.info("Fitting RandomForestClassifier (n_estimators=100, max_depth=12, random_state=%d)...", random_state)
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        random_state=random_state,
        n_jobs=-1,
    )
    rf.fit(X_train, y_train)

    # Evaluate on isolated test set
    y_pred = rf.predict(X_test)
    y_proba = rf.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, pos_label=1, zero_division=0))
    rec = float(recall_score(y_test, y_pred, pos_label=1, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, pos_label=1, zero_division=0))
    auc = float(roc_auc_score(y_test, y_proba))

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = [int(val) for val in cm.ravel()]

    # Extract top 10 feature importances
    importances = rf.feature_importances_
    indices = np.argsort(importances)[::-1][:10]
    top_features = [
        {"feature": feature_names[i], "importance": float(round(importances[i], 4))}
        for i in indices
    ]

    metrics_payload = {
        "model_type": "Random Forest",
        "task": "Binary Attack Detection",
        "random_state": random_state,
        "n_estimators": 100,
        "max_depth": 12,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "classes": ["BENIGN", "ATTACK"],
        "class_mapping": {"0": "BENIGN", "1": "ATTACK"},
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(auc, 4),
        "confusion_matrix": {
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
            "true_positive": tp,
        },
        "top_features": top_features,
    }

    # Save trained model to disk
    logger.info("Saving trained Random Forest model to: %s", model_output)
    joblib.dump(rf, model_output)

    # Save real evaluated metrics to JSON
    logger.info("Saving evaluation metrics to: %s", metrics_output)
    with open(metrics_output, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    # Output detailed report
    print("\n" + "=" * 60)
    print("HEX HIVE — Phase 5 Random Forest Model Training Report")
    print("=" * 60)
    print(f"Algorithm:           RandomForestClassifier")
    print(f"Task:                Binary Network Attack Detection (BENIGN vs ATTACK)")
    print(f"Total Features:      {len(feature_names)}")
    print(f"Training Samples:    {len(X_train)} (BENIGN={train_benign}, ATTACK={train_attack})")
    print(f"Test Samples:        {len(X_test)} (BENIGN={test_benign}, ATTACK={test_attack})")
    print("-" * 60)
    print(f"Accuracy:            {acc * 100:.2f}%")
    print(f"Precision:           {prec * 100:.2f}%")
    print(f"Recall:              {rec * 100:.2f}%")
    print(f"F1 Score:            {f1 * 100:.2f}%")
    print(f"ROC-AUC:             {auc:.4f}")
    print("-" * 60)
    print("Confusion Matrix:")
    print(f"  True Negatives (BENIGN correctly classified):  {tn}")
    print(f"  False Positives (BENIGN classified as ATTACK): {fp}")
    print(f"  False Negatives (ATTACK classified as BENIGN): {fn}")
    print(f"  True Positives (ATTACK correctly classified):  {tp}")
    print("-" * 60)
    print("Top 5 Indicative Flow Features:")
    for i, item in enumerate(top_features[:5], 1):
        print(f"  {i}. {item['feature']:<30} (importance: {item['importance']:.4f})")
    print("=" * 60)
    print(f"Model successfully saved to:   {model_output}")
    print(f"Metrics successfully saved to: {metrics_output}")
    print("=" * 60 + "\n")

    return metrics_payload


if __name__ == "__main__":
    train_attack_classifier()


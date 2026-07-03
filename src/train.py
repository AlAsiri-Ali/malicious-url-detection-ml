from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from features import build_feature_frame, make_binary_labels


def build_models() -> dict[str, object]:
    return {
        "Logistic Regression": LogisticRegression(max_iter=2000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=300, max_depth=None, random_state=42, n_jobs=-1),
        "XGBoost": XGBClassifier(
            n_estimators=400,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="binary:logistic",
            eval_metric="logloss",
            n_jobs=-1,
            random_state=42,
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/malicious_phish.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    X = build_feature_frame(df["url"])
    y = make_binary_labels(df["type"])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    best_model_name = None
    best_model = None
    best_accuracy = -1.0

    for name, model in build_models().items():
        if name == "Logistic Regression":
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        rows.append({
            "model": name,
            "accuracy": accuracy,
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
        })

        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model_name = name
            best_model = model

    pd.DataFrame(rows).to_csv(args.output_dir / "model_comparison.csv", index=False)
    joblib.dump(best_model, args.output_dir / "best_model.joblib")
    joblib.dump(scaler, args.output_dir / "scaler.joblib")
    print(f"Best model: {best_model_name} | accuracy={best_accuracy:.4f}")


if __name__ == "__main__":
    main()

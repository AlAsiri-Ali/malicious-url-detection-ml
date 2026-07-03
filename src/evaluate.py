from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from features import build_feature_frame, make_binary_labels


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/malicious_phish.csv"))
    parser.add_argument("--model", type=Path, default=Path("outputs/best_model.joblib"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/evaluation"))
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    X = build_feature_frame(df["url"])
    y = make_binary_labels(df["type"])
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = joblib.load(args.model)
    y_pred = model.predict(X_test)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = classification_report(y_test, y_pred, target_names=["benign", "malicious"], output_dict=True)
    pd.DataFrame(report).transpose().to_csv(args.output_dir / "classification_report.csv")

    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(cm, display_labels=["benign", "malicious"])
    disp.plot(cmap="Blues")
    plt.tight_layout()
    plt.savefig(args.output_dir / "confusion_matrix.png", dpi=200)


if __name__ == "__main__":
    main()

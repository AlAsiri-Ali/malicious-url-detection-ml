from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd

from features import build_feature_frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=Path("outputs/best_model.joblib"))
    parser.add_argument("--url", required=True)
    args = parser.parse_args()

    model = joblib.load(args.model)
    X = build_feature_frame(pd.Series([args.url]))
    prediction = int(model.predict(X)[0])
    print("malicious" if prediction == 1 else "benign")


if __name__ == "__main__":
    main()

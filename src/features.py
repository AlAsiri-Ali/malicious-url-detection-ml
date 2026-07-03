from __future__ import annotations

import re
import pandas as pd

FEATURE_COLUMNS = [
    "url_length",
    "num_digits",
    "num_special",
    "num_dots",
    "has_ip",
    "has_https",
    "has_login",
    "has_verify",
    "has_secure",
]


def extract_features(url: str) -> dict[str, int]:
    """Extract lightweight lexical features from a URL string."""
    url = str(url)
    lower = url.lower()
    return {
        "url_length": len(url),
        "num_digits": sum(ch.isdigit() for ch in url),
        "num_special": sum(not ch.isalnum() for ch in url),
        "num_dots": url.count("."),
        "has_ip": int(bool(re.search(r"\d+\.\d+\.\d+\.\d+", url))),
        "has_https": int(lower.startswith("https")),
        "has_login": int("login" in lower),
        "has_verify": int("verify" in lower),
        "has_secure": int("secure" in lower),
    }


def build_feature_frame(urls: pd.Series) -> pd.DataFrame:
    return pd.DataFrame([extract_features(url) for url in urls], columns=FEATURE_COLUMNS)


def make_binary_labels(label_series: pd.Series) -> pd.Series:
    """Map benign to 0 and all non-benign labels to 1."""
    return label_series.apply(lambda label: 0 if str(label).lower() == "benign" else 1)

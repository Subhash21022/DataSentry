import pytest
import pandas as pd
from datasentry.core.ml_anomaly import MLAnomalyDetector


def test_ml_anomaly_detector():
    # 20 regular points + 1 massive outlier
    df = pd.DataFrame({
        "age": [25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 18],
        "salary": [50000, 52000, 51000, 53000, 55000, 54000, 56000, 58000, 57000, 59000,
                   60000, 62000, 61000, 63000, 65000, 64000, 66000, 68000, 67000, 69000, 2500000],
    })

    detector = MLAnomalyDetector(df, contamination=0.1)
    result = detector.detect_anomalies()

    assert result["algorithm"] == "IsolationForest"
    assert result["total_anomalies"] > 0
    # The extreme row (index 20) should have a high anomaly score
    top_anomaly = result["anomalies"][0]
    assert top_anomaly["row_index"] == 20
    assert top_anomaly["anomaly_score"] > 0.5

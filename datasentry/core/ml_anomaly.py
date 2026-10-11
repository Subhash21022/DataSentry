from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class MLAnomalyDetector:
    """
    Machine Learning-Powered Tabular Anomaly Detection.
    Uses Scikit-Learn's Isolation Forest and statistical distance
    to identify multivariate outliers and data drift without requiring labels.
    """

    def __init__(self, df: pd.DataFrame, contamination: float = 0.05, random_state: int = 42):
        self.df = df.copy()
        self.contamination = contamination
        self.random_state = random_state

    def detect_anomalies(self, feature_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Train an unsupervised Isolation Forest on numerical features
        and score every row in the dataset for multivariate anomalousness.
        """
        # Select numeric columns
        if feature_columns:
            numeric_cols = [c for c in feature_columns if c in self.df.columns and pd.api.types.is_numeric_dtype(self.df[c])]
        else:
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) == 0:
            return {
                "error": "No numeric features available for ML anomaly detection.",
                "total_anomalies": 0,
                "anomalies": [],
            }

        # Impute missing values with column median for ML training
        imputed_df = self.df[numeric_cols].copy()
        for col in numeric_cols:
            median_val = imputed_df[col].median()
            imputed_df[col] = imputed_df[col].fillna(median_val if not np.isnan(median_val) else 0)

        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(imputed_df)

        # Train Isolation Forest
        model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
        )
        # -1 = anomaly, 1 = normal
        predictions = model.fit_predict(X_scaled)
        # Lower score = more abnormal
        raw_scores = model.decision_function(X_scaled)

        # Normalize score to 0 (normal) - 1 (highly anomalous)
        # decision_function gives negative values for anomalies
        min_score = raw_scores.min()
        max_score = raw_scores.max()
        if max_score > min_score:
            anomaly_scores = 1.0 - ((raw_scores - min_score) / (max_score - min_score))
        else:
            anomaly_scores = np.zeros_like(raw_scores)

        anomaly_indices = np.where(predictions == -1)[0]
        anomalies_list = []

        for idx in anomaly_indices:
            row_data = self.df.iloc[idx].fillna("").to_dict()
            score = round(float(anomaly_scores[idx]), 3)

            # Explainability: which column contributed most to extreme deviation
            z_scores = np.abs(X_scaled[idx])
            top_col_idx = int(np.argmax(z_scores))
            top_feature = numeric_cols[top_col_idx]

            anomalies_list.append({
                "row_index": int(idx),
                "anomaly_score": score,
                "suspected_primary_feature": top_feature,
                "feature_z_score": round(float(z_scores[top_col_idx]), 2),
                "data": row_data,
            })

        # Sort anomalies by score descending
        anomalies_list.sort(key=lambda x: x["anomaly_score"], reverse=True)

        return {
            "algorithm": "IsolationForest",
            "evaluated_rows": int(len(self.df)),
            "features_used": numeric_cols,
            "contamination_rate": self.contamination,
            "total_anomalies": len(anomalies_list),
            "anomaly_percentage": round((len(anomalies_list) / max(len(self.df), 1)) * 100, 2),
            "anomalies": anomalies_list,
        }

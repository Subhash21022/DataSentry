import re
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from scipy import stats


class DataProfiler:
    """
    Core Statistical & Semantic Data Profiler.
    Calculates distributions, cardinality, null metrics, correlations,
    and a holistic Data Quality Score (0 - 100).
    """

    EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
    DATE_REGEX = re.compile(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$")

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    @classmethod
    def from_csv(cls, filepath: str, **kwargs) -> "DataProfiler":
        df = pd.read_csv(filepath, **kwargs)
        return cls(df)

    def infer_semantic_type(self, series: pd.Series) -> str:
        """Infer semantic type beyond basic pandas dtypes."""
        non_null = series.dropna().astype(str)
        if len(non_null) == 0:
            return "empty"

        sample = non_null.head(100)
        email_matches = sum(bool(self.EMAIL_REGEX.match(val.strip())) for val in sample)
        if email_matches / len(sample) >= 0.5:
            return "email"

        date_matches = sum(bool(self.DATE_REGEX.match(val.strip())) for val in sample)
        if date_matches / len(sample) >= 0.5:
            return "date_string"

        if pd.api.types.is_bool_dtype(series):
            return "boolean"
        elif pd.api.types.is_numeric_dtype(series):
            if series.nunique() <= 2 and set(series.dropna().unique()).issubset({0, 1}):
                return "binary_indicator"
            return "numeric"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "datetime"
        elif series.nunique() / max(len(series), 1) < 0.1:
            return "categorical"
        return "text"

    def profile_columns(self) -> Dict[str, Dict[str, Any]]:
        """Compute detailed column-level metrics."""
        cols_profile = {}
        total_rows = len(self.df)

        for col in self.df.columns:
            series = self.df[col]
            null_count = int(series.isnull().sum())
            null_pct = round((null_count / total_rows) * 100, 2) if total_rows > 0 else 0
            distinct_count = int(series.nunique(dropna=True))
            semantic_type = self.infer_semantic_type(series)

            col_meta: Dict[str, Any] = {
                "name": col,
                "pandas_dtype": str(series.dtype),
                "semantic_type": semantic_type,
                "null_count": null_count,
                "null_percentage": null_pct,
                "distinct_count": distinct_count,
                "distinct_percentage": round((distinct_count / total_rows) * 100, 2) if total_rows > 0 else 0,
            }

            if pd.api.types.is_numeric_dtype(series) and distinct_count > 0:
                clean_num = series.dropna()
                if len(clean_num) > 0:
                    col_meta.update({
                        "min": float(clean_num.min()),
                        "max": float(clean_num.max()),
                        "mean": round(float(clean_num.mean()), 2),
                        "std": round(float(clean_num.std()), 2) if len(clean_num) > 1 else 0.0,
                        "median": round(float(clean_num.median()), 2),
                        "q25": round(float(clean_num.quantile(0.25)), 2),
                        "q75": round(float(clean_num.quantile(0.75)), 2),
                        "zeros_count": int((clean_num == 0).sum()),
                        "skewness": round(float(stats.skew(clean_num)), 2) if len(clean_num) > 2 else 0.0,
                    })
                    # Sample distribution buckets for charts
                    counts, bin_edges = np.histogram(clean_num, bins=10)
                    col_meta["distribution"] = [
                        {
                            "bin": f"{round(bin_edges[i], 1)} - {round(bin_edges[i+1], 1)}",
                            "count": int(counts[i]),
                        }
                        for i in range(len(counts))
                    ]
            else:
                # Categorical / text frequencies
                top_values = series.value_counts(dropna=True).head(5).to_dict()
                col_meta["top_values"] = {str(k): int(v) for k, v in top_values.items()}

            cols_profile[col] = col_meta

        return cols_profile

    def correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        """Calculate Pearson correlation for numeric columns."""
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] < 2:
            return {}
        corr = numeric_df.corr().fillna(0).round(2)
        return corr.to_dict()

    def calculate_quality_score(self) -> Dict[str, Any]:
        """
        Calculate an aggregated Data Quality Score (0 to 100).
        Pillars: Completeness (40%), Uniqueness (30%), Validity/Plausibility (30%).
        """
        total_cells = self.df.shape[0] * self.df.shape[1]
        if total_cells == 0:
            return {"score": 100, "grade": "A+", "pillars": {}}

        # 1. Completeness
        null_cells = int(self.df.isnull().sum().sum())
        completeness = max(0.0, 100.0 - (null_cells / total_cells * 100))

        # 2. Uniqueness
        dup_rows = int(self.df.duplicated().sum())
        total_rows = len(self.df)
        uniqueness = max(0.0, 100.0 - ((dup_rows / total_rows * 100) if total_rows > 0 else 0))

        # 3. Validity (heuristic: basic type consistency & negative numeric warnings)
        validity_deductions = 0
        for col in self.df.select_dtypes(include=[np.number]).columns:
            # e.g. age or salary should rarely be negative
            if "age" in col.lower() or "price" in col.lower() or "salary" in col.lower():
                neg_count = (self.df[col] < 0).sum()
                if neg_count > 0:
                    validity_deductions += min(15, neg_count * 5)

        validity = max(0.0, 100.0 - validity_deductions)

        # Weighted aggregate score
        final_score = round(0.40 * completeness + 0.30 * uniqueness + 0.30 * validity, 1)

        grade = "A"
        if final_score < 60:
            grade = "F"
        elif final_score < 70:
            grade = "D"
        elif final_score < 80:
            grade = "C"
        elif final_score < 90:
            grade = "B"

        return {
            "score": final_score,
            "grade": grade,
            "pillars": {
                "completeness": round(completeness, 1),
                "uniqueness": round(uniqueness, 1),
                "validity": round(validity, 1),
            },
        }

    def generate_cleaning_suggestions(self) -> List[Dict[str, str]]:
        """Generate automated intelligent cleaning recommendations."""
        suggestions = []
        dup_count = int(self.df.duplicated().sum())
        if dup_count > 0:
            suggestions.append({
                "type": "deduplication",
                "severity": "medium",
                "message": f"Found {dup_count} exact duplicate rows. Consider dropping duplicates via `df.drop_duplicates()`.",
            })

        for col in self.df.columns:
            null_count = int(self.df[col].isnull().sum())
            if null_count > 0:
                pct = round((null_count / len(self.df)) * 100, 1)
                if pct > 40:
                    suggestions.append({
                        "type": "drop_column",
                        "severity": "high",
                        "message": f"Column '{col}' has {pct}% missing values. Consider dropping or reviewing collection pipeline.",
                    })
                elif pd.api.types.is_numeric_dtype(self.df[col]):
                    suggestions.append({
                        "type": "imputation",
                        "severity": "low",
                        "message": f"Column '{col}' has {null_count} nulls. Recommend median or iterative ML imputation.",
                    })

        return suggestions

    def run_profile(self) -> Dict[str, Any]:
        """Execute full profiling suite and return structured JSON."""
        return {
            "summary": {
                "row_count": int(self.df.shape[0]),
                "column_count": int(self.df.shape[1]),
                "duplicate_rows": int(self.df.duplicated().sum()),
                "total_missing_cells": int(self.df.isnull().sum().sum()),
                "memory_usage_kb": round(self.df.memory_usage(deep=True).sum() / 1024, 2),
            },
            "quality_score": self.calculate_quality_score(),
            "columns": self.profile_columns(),
            "correlations": self.correlation_matrix(),
            "cleaning_suggestions": self.generate_cleaning_suggestions(),
            "sample_data": self.df.head(10).fillna("").to_dict(orient="records"),
        }

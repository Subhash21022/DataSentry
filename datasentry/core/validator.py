import re
from typing import Any, Dict, List, Optional
import pandas as pd


class DataValidator:
    """
    Deterministic Rule-Based Validation Engine.
    Executes schema checks, boundary ranges, regex patterns, and categorical constraints.
    """

    def __init__(self, df: pd.DataFrame, rules: Optional[List[Dict[str, Any]]] = None):
        self.df = df.copy()
        self.rules = rules or []

    def add_rule(self, rule: Dict[str, Any]) -> "DataValidator":
        self.rules.append(rule)
        return self

    def validate(self) -> Dict[str, Any]:
        """Run all configured validation rules."""
        results: List[Dict[str, Any]] = []
        total_failed_rules = 0

        for idx, rule in enumerate(self.rules):
            rule_type = rule.get("type")
            col = rule.get("column")
            rule_id = rule.get("id", f"rule_{idx+1}")
            description = rule.get("description", f"{rule_type} on {col}")

            res = {
                "id": rule_id,
                "type": rule_type,
                "column": col,
                "description": description,
                "passed": True,
                "violations_count": 0,
                "violation_indices": [],
                "sample_violating_values": [],
                "error_message": None,
            }

            # Check if column exists
            if col and col not in self.df.columns and rule_type != "required_columns":
                res["passed"] = False
                res["error_message"] = f"Column '{col}' does not exist in dataset."
                total_failed_rules += 1
                results.append(res)
                continue

            if rule_type == "required_columns":
                expected_cols = rule.get("columns", [])
                missing = [c for c in expected_cols if c not in self.df.columns]
                if missing:
                    res["passed"] = False
                    res["violations_count"] = len(missing)
                    res["error_message"] = f"Missing required columns: {missing}"
                    total_failed_rules += 1

            elif rule_type == "not_null":
                null_mask = self.df[col].isnull()
                violations = int(null_mask.sum())
                if violations > 0:
                    res["passed"] = False
                    res["violations_count"] = violations
                    res["violation_indices"] = self.df[null_mask].index.tolist()[:10]
                    res["error_message"] = f"Found {violations} null values in '{col}'."
                    total_failed_rules += 1

            elif rule_type == "range":
                min_val = rule.get("min")
                max_val = rule.get("max")
                series = pd.to_numeric(self.df[col], errors="coerce")

                mask = pd.Series(False, index=self.df.index)
                if min_val is not None:
                    mask = mask | (series < min_val)
                if max_val is not None:
                    mask = mask | (series > max_val)

                violations = int(mask.sum())
                if violations > 0:
                    res["passed"] = False
                    res["violations_count"] = violations
                    violating_rows = self.df[mask]
                    res["violation_indices"] = violating_rows.index.tolist()[:10]
                    res["sample_violating_values"] = violating_rows[col].tolist()[:5]
                    res["error_message"] = f"{violations} values outside [{min_val}, {max_val}] in '{col}'."
                    total_failed_rules += 1

            elif rule_type == "allowed_values":
                allowed = set(rule.get("values", []))
                non_null_series = self.df[col].dropna()
                invalid_mask = ~non_null_series.isin(allowed)
                violations = int(invalid_mask.sum())
                if violations > 0:
                    res["passed"] = False
                    res["violations_count"] = violations
                    violating_rows = self.df.loc[non_null_series[invalid_mask].index]
                    res["violation_indices"] = violating_rows.index.tolist()[:10]
                    res["sample_violating_values"] = violating_rows[col].unique().tolist()[:5]
                    res["error_message"] = f"{violations} values not in allowed set {allowed}."
                    total_failed_rules += 1

            elif rule_type == "regex":
                pattern_str = rule.get("pattern", "")
                compiled_pattern = re.compile(pattern_str)
                non_null_series = self.df[col].dropna().astype(str)
                match_mask = non_null_series.apply(lambda x: bool(compiled_pattern.match(x)))
                violations = int((~match_mask).sum())
                if violations > 0:
                    res["passed"] = False
                    res["violations_count"] = violations
                    violating_rows = self.df.loc[non_null_series[~match_mask].index]
                    res["violation_indices"] = violating_rows.index.tolist()[:10]
                    res["sample_violating_values"] = violating_rows[col].tolist()[:5]
                    res["error_message"] = f"{violations} values failed regex pattern '{pattern_str}'."
                    total_failed_rules += 1

            results.append(res)

        total_rules = len(self.rules)
        passed_rules = total_rules - total_failed_rules
        validation_success = total_failed_rules == 0

        return {
            "success": validation_success,
            "total_rules": total_rules,
            "passed_rules": passed_rules,
            "failed_rules": total_failed_rules,
            "results": results,
        }

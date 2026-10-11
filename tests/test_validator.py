import pytest
import pandas as pd
from datasentry.core.validator import DataValidator


@pytest.fixture
def sample_dataframe():
    data = {
        "id": [1, 2, 3],
        "email": ["valid@test.com", "another@domain.org", "bad-email"],
        "age": [25, 45, -2],
        "status": ["active", "pending", "unknown"],
    }
    return pd.DataFrame(data)


def test_validator_rules(sample_dataframe):
    rules = [
        {"type": "not_null", "column": "id"},
        {"type": "range", "column": "age", "min": 0, "max": 120},
        {"type": "allowed_values", "column": "status", "values": ["active", "pending"]},
    ]

    validator = DataValidator(sample_dataframe, rules)
    result = validator.validate()

    assert result["total_rules"] == 3
    assert result["failed_rules"] == 2
    assert result["passed_rules"] == 1
    assert result["success"] is False

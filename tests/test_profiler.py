import pytest
import pandas as pd
from datasentry.core.profiler import DataProfiler


@pytest.fixture
def sample_dataframe():
    data = {
        "id": [1, 2, 3, 4, 4],
        "name": ["Alice", "Bob", "Charlie", "David", "David"],
        "email": ["alice@test.com", "bob@test.com", "charlie@test.com", "invalid-email", "invalid-email"],
        "age": [25, 30, -5, 40, 40],
        "salary": [50000.0, 70000.0, None, 120000.0, 120000.0],
    }
    return pd.DataFrame(data)


def test_profiler_summary(sample_dataframe):
    profiler = DataProfiler(sample_dataframe)
    report = profiler.run_profile()

    assert report["summary"]["row_count"] == 5
    assert report["summary"]["column_count"] == 5
    assert report["summary"]["duplicate_rows"] == 1
    assert report["summary"]["total_missing_cells"] == 1


def test_profiler_semantic_inference(sample_dataframe):
    profiler = DataProfiler(sample_dataframe)
    report = profiler.run_profile()

    cols = report["columns"]
    assert cols["email"]["semantic_type"] == "email"
    assert cols["age"]["semantic_type"] == "numeric"


def test_profiler_quality_score(sample_dataframe):
    profiler = DataProfiler(sample_dataframe)
    score_data = profiler.calculate_quality_score()

    assert 0 <= score_data["score"] <= 100
    assert score_data["grade"] in ["A", "B", "C", "D", "F"]

import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from copilot import validate_observations, evidence
from analyze import cuped, sample_size


def test_reference_lookup_rejects_numbers_and_prose():
    packet = {"query_id": "test", "records": [{"orders": 100}]}
    for item in [
        {"row": 0, "column": "orders", "value": 999},
        {"row": 0, "column": "orders", "cause": "AI caused growth"},
        {"row": -1, "column": "orders"},
        {"row": True, "column": "orders"},
    ]:
        with pytest.raises(ValueError):
            validate_observations([item], packet)
    assert validate_observations([{"row": 0, "column": "orders"}], packet)[0]["value"] == 100


def test_sql_injection_is_not_a_catalog_query():
    with pytest.raises(ValueError):
        evidence("overview; DROP TABLE raw.orders")


def test_renderer_owns_full_precision_and_rejects_nonmetrics():
    packet = {
        "query_id": "test",
        "records": [{"amount": "100.00000000000000001", "date": "2026-01-31", "flag": True}],
    }
    result = validate_observations([{"row": 0, "column": "amount"}], packet)
    assert result[0]["value"] == "100.00000000000000001"
    for column in ["date", "flag", "missing"]:
        with pytest.raises(ValueError):
            validate_observations([{"row": 0, "column": column}], packet)
    with pytest.raises(ValueError):
        validate_observations([{"row": 0, "column": "amount"}] * 2, packet)


def test_cuped_preserves_mean_and_reduces_variance_on_correlated_covariate():
    rng = np.random.default_rng(42)
    x = rng.normal(size=5000)
    y = 2 * x + rng.normal(size=5000)
    adjusted = cuped(y, x)
    assert np.mean(adjusted) == pytest.approx(np.mean(y))
    assert np.var(adjusted) < np.var(y)
    with pytest.raises(ValueError):
        cuped([1, 0, 1], [0, 0, 0])


def test_power_increases_for_smaller_effect():
    assert sample_size(0.03, 0.002) > sample_size(0.03, 0.005) > 100

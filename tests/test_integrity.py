import sys
from pathlib import Path
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from copilot import validate_observations, evidence
from analyze import cuped, sample_size


def test_rejects_fabricated_number_and_prose():
    p = {"query_id": "test", "records": [{"orders": 100}]}
    with pytest.raises(ValueError):
        validate_observations([{"row": 0, "column": "orders", "value": 999}], p)
    with pytest.raises(ValueError):
        validate_observations([{"row": 0, "column": "orders", "value": 100, "cause": "AI caused growth"}], p)
    with pytest.raises(ValueError):
        validate_observations([{"row": -1, "column": "orders", "value": 100}], p)
    assert validate_observations([{"row": 0, "column": "orders", "value": 100}], p)[0]["value"] == 100


def test_sql_injection_is_not_a_catalog_query():
    with pytest.raises(ValueError):
        evidence("overview; DROP TABLE raw.orders")


def test_exact_numeric_representation_is_allowed_but_rounding_is_not():
    packet = {"query_id": "test", "records": [{"amount": "100.00"}]}
    assert (
        validate_observations([{"row": 0, "column": "amount", "value": 100}], packet)[0]["value"] == "100.00"
    )
    with pytest.raises(ValueError):
        validate_observations([{"row": 0, "column": "amount", "value": 99.99}], packet)
    with pytest.raises(ValueError):
        validate_observations([{"row": 0, "column": "amount", "value": True}], packet)


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

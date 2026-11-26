import json

import pandas as pd
import pytest

from demo_data import ROOT, query_records
from delivery_study import wilson


def test_published_monthly_totals_reconcile_to_headlines():
    monthly = pd.read_csv(ROOT / "reports/mart_monthly.csv")
    metrics = json.loads((ROOT / "reports/metrics.json").read_text())
    assert monthly.orders.sum() == metrics["orders"]
    assert monthly.delivered_orders.sum() == metrics["delivered_orders"]
    assert monthly.delivered_gmv_brl.sum() == pytest.approx(metrics["delivered_gmv_brl"], abs=0.01)


def test_cohort_totals_are_weighted_not_mean_of_rates():
    cohorts = pd.read_csv(ROOT / "reports/mart_retention.csv")
    metrics = json.loads((ROOT / "reports/metrics.json").read_text())
    assert cohorts.repeat_customers.sum() / cohorts.eligible_customers.sum() == pytest.approx(
        metrics["repeat_90d_rate"]
    )
    assert (cohorts.repeat_customers <= cohorts.eligible_customers).all()


def test_wilson_interval_includes_estimate_and_handles_no_events():
    low, high = wilson(0, 100)
    assert low == pytest.approx(0)
    assert 0 < high < 0.05
    with pytest.raises(ValueError):
        wilson(1, 0)


def test_demo_evidence_excludes_arbitrary_queries():
    with pytest.raises(ValueError):
        query_records("DROP TABLE mart_monthly")
    assert len(query_records("fulfillment")) == 4

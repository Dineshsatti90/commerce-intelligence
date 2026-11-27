"""SQL summaries and explicit AI review controls, without a model dependency."""

import pytest
from streamlit.testing.v1 import AppTest
from pathlib import Path
from demo_data import query_records, load_table
from delivery_study import detectable_decrease


def test_summaries_reconcile_to_complete_sql_sources():
    monthly = load_table("mart_monthly").sort_values("month")
    summary = query_records("monthly_summary")[0]
    assert summary["first_gmv_brl"] == pytest.approx(monthly.iloc[0].delivered_gmv_brl)
    assert summary["last_gmv_brl"] == pytest.approx(monthly.iloc[-1].delivered_gmv_brl)
    assert summary["peak_gmv_brl"] == pytest.approx(monthly.delivered_gmv_brl.max())
    cohorts = load_table("mart_retention")
    result = query_records("retention_summary")[0]
    assert result["repeat_rate_90d"] == pytest.approx(
        cohorts.repeat_customers.sum() / cohorts.eligible_customers.sum()
    )


def test_power_sensitivity_is_design_specific():
    a = detectable_decrease(0.0064, 68000, 2300)
    b = detectable_decrease(0.0064, 136000, 4600)
    assert 0 < b["minimum_detectable_decrease_pp"] < a["minimum_detectable_decrease_pp"] < 0.64
    with pytest.raises(ValueError):
        detectable_decrease(0, 1000, 100)


def test_unreviewed_free_text_does_not_enable_display(monkeypatch):
    monkeypatch.setenv("COMMERCE_DEMO_MODE", "1")
    root = Path(__file__).resolve().parents[1]
    app = AppTest.from_file(str(root / "app.py"), default_timeout=30).run()
    app.radio[0].set_value("Configured LLM").run()
    assert not app.exception
    investigate = next(b for b in app.button if b.label == "Investigate")
    assert investigate.disabled

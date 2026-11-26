"""Dashboard integration tests run on committed aggregates, without raw data."""

from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_offline_dashboard_and_evidence_selector(monkeypatch):
    monkeypatch.setenv("COMMERCE_DEMO_MODE", "1")
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert not app.exception
    assert len(app.metric) == 3
    assert app.metric[0].value == "99,421"
    selector = next(item for item in app.selectbox if item.label == "Approved question")
    selector.select("retention").run()
    assert not app.exception
    assert len(app.dataframe) >= 4


def test_small_cohort_control_and_state_filter(monkeypatch):
    monkeypatch.setenv("COMMERCE_DEMO_MODE", "1")
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    app.slider[0].set_value(500).run()
    state = next(item for item in app.selectbox if item.label == "State")
    state.select("SP").run()
    assert not app.exception
    assert app.slider[0].value == 500

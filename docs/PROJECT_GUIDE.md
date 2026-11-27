# Run, rebuild and review

## Quick demo

```bash
python -m venv .venv
# Windows: .venv/Scripts/Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

The demo uses committed public aggregates and requires no raw download or model key. Free Streamlit hosting can sleep after inactivity; the README preview and [walkthrough](WALKTHROUGH.md) remain available while it wakes.

## AI setup and scope

Use a local Ollama endpoint or a compatible configured model. Set `LLM_BACKEND=ollama`, `LLM_BASE_URL=http://127.0.0.1:11434/v1` and `LLM_MODEL=llama3:8b` for the native local adapter. The model selects source references; Python renders values. Explicit preflight patterns are a limited extra check, not a complete injection defense. See [evaluation protocol and failures](AI_EVALUATION.md) before interpreting scores.

## Validation

CI runs Ruff checks, committed Streamlit AppTests and focused numerical tests. [Workflow](../.github/workflows/check.yml), [tests](../tests), [method choices](METHOD_CHOICES.md), [data dictionary](DATA_DICTIONARY.md), [operations](OPERATIONS.md).

## Rebuild the real Olist analysis

```bash
python pipeline.py all
python analyze.py
python delivery_study.py
python make_overview.py
python -m pytest tests -q
```

Activate the environment so `dbt` is on PATH. The pinned source release contains 99,441 orders and 1,000,163 geolocation observations; 99,421 orders precede the analysis cutoff. Coordinates are not additional purchases. See [source fingerprints](../reports/source_manifest.json) and [data terms](../DATA_LICENSE.md).

The pipeline creates typed dbt staging models, order-grain facts and analytical marts. Child payments, items and reviews are aggregated before order joins. CI additionally builds all dbt models and runs 21 data tests on a clearly labeled synthetic boundary fixture; real findings use the real Olist release.

## Decision and uncertainty

[Decision memo](../reports/decision_memo.md), [prospective experiment design](../reports/experiment_memo.md), [state priorities](../reports/state_delivery_priorities.csv), [Power BI measures](../bi/measures.dax).

The −0.16pp estimate has a 95% interval of about −0.45 to +0.13pp. The landmark on-time baseline is 0.64%, distinct from full-window repeat purchase. The separate independent two-proportion planning sensitivity needs about 0.39pp decrease for 80% power at two-sided 5% alpha with these group sizes. It is not retrospective GLM power.

## Limitations

Historical 2016–2018 snapshot; cutoff 2018-09-01. Status is snapshot status, not historical event reconstruction. First observed purchase may not be first ever. GMV is merchandise value, not platform revenue; the funnel is fulfillment rather than browsing. The landmark changes the eligible population and cannot remove unobserved confounding. Displayed cohorts default to at least 100 customers while totals retain all eligible customers. Seller IDs are anonymous; carrier names are absent. No experiment has run or retention savings been achieved. AI tests are developer-authored and source references do not establish relevance. Configured free-text mode requires review of an explicit SQL scope. No native Power BI `.pbix` is included.

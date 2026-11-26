# Reproduction and operations

## Prerequisites

Use Python 3.10+ and run from the repository root. A tested reference environment is pinned in `requirements.lock.txt`. Allow disk space for the downloaded ZIP, expanded CSVs, DuckDB database and generated exports. Raw inputs and databases are intentionally excluded from Git.

## Commands

| Command | Result |
| --- | --- |
| `python pipeline.py download` | Download/extract complete release; write source manifest |
| `python pipeline.py ingest` | Rebuild raw DuckDB tables; verify full-release row thresholds |
| `python pipeline.py build` | Execute dbt models and data tests |
| `python pipeline.py all` | Run those steps in sequence |
| `python analyze.py` | Export marts and regenerate findings/experiment memos |
| `python delivery_study.py` | Regenerate the timing-aware delivery/retention study and final decision memo |
| `python make_overview.py` | Regenerate the README SVG from observed metrics |
| `python -m pytest tests -q` | Run focused Python regressions |
| `python copilot.py --evaluate` | Evaluate configured model, or record missing-model status |
| `streamlit run app.py` | Launch local dashboard |

Activate the virtual environment before invoking dbt; `pipeline.py` looks for its executable on PATH. The pipeline passes an absolute database location to dbt. To run dbt manually, set `COMMERCE_DB` and use `dbt build --project-dir dbt --profiles-dir dbt`.

## Optional model configuration

Set `LLM_BASE_URL` to a trusted OpenAI-compatible API base ending in `/v1`, `LLM_MODEL` to an installed/available model identifier and `LLM_API_KEY` if the provider requires authentication. The endpoint must support chat completions and JSON-object response mode. Environment files are examples, not automatically loaded. Requests can incur provider charges.

Only approved aggregate query outputs are submitted by the evidence workflow. Never put credentials, private customer data or unreviewed tables in its catalog. The offline evidence explorer makes no model calls.

The recorded local run uses `LLM_MODEL=qwen2.5:3b`, `LLM_BASE_URL=http://127.0.0.1:11434/v1` and `LLM_BACKEND=ollama`. Ollama must already be installed/running with that model. The native adapter requests JSON, temperature 0, seed 42, 8,192 context tokens and a 600-token output cap. No paid key is required. Preserve previous runs before evaluating a different prompt/model.

The dashboard defaults to committed aggregate extracts. `COMMERCE_DEMO_MODE=1` forces the copilot to use those extracts even when a local warehouse exists. CI runs `tests/test_app.py` and a separate labeled synthetic dbt fixture; never mix fixture outputs into the reported real-data findings.

## Troubleshooting

- **Download fails:** retry the versioned source URL; verify Kaggle availability. A non-ZIP response is rejected. No sample dataset is silently substituted.
- **dbt missing:** activate the environment and install requirements; check the active `dbt` executable.
- **Database locked:** stop other writers before rebuilding. The copilot opens a read-only connection.
- **Dashboard reports missing outputs:** complete `pipeline.py all` and `analyze.py` first.
- **LLM unset or endpoint rejects JSON mode:** configure a compatible model; offline analysis remains available. Do not reinterpret `not_run_missing_model` as an evaluation pass.
- **Power BI refresh:** regenerate CSVs, then refresh sources. Keep aggregate marts disconnected unless a carefully defined dimensional relationship is introduced.

## Publication checklist

Publish code, documentation, aggregate findings and manifests. Exclude `data/raw/`, `warehouse/`, virtual environments, `.env`, dbt build/log directories and the detailed `reports/fct_orders.csv` export. The latter can be regenerated locally for Power BI. Respect the source dataset's noncommercial/share-alike terms when redistributing derived outputs.

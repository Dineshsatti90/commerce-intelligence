# Commerce Intelligence

[![Checks](https://github.com/Dineshsatti90/commerce-intelligence/actions/workflows/check.yml/badge.svg)](https://github.com/Dineshsatti90/commerce-intelligence/actions/workflows/check.yml)

**Late deliveries had much worse reviews. Repeat purchasing told a less certain story.**

[Live dashboard](https://dineshsatti90-commerce-intelligence.streamlit.app/) · [Two-minute walkthrough](docs/WALKTHROUGH.md) · [Run & methodology](docs/PROJECT_GUIDE.md)

- **Customer experience:** mean reviews were 2.27 for late deliveries versus 4.29 on time.
- **Retention uncertainty:** across 70,427 landmark customers, the adjusted difference was −0.16pp (95% CI −0.45 to +0.13).
- **Decision:** investigate MA, CE and BA delivery operations, then test customer outcomes prospectively.

<img src="docs/screenshots/walkthrough.gif" width="720" alt="Silent preview of the commerce dashboard">

### AI: references instead of copied numbers

The model selects cells; Python retrieves exact values. Reviewed SQL and explicit scope review own the public workflow.

| Model | Route + reference contract | Unsupported refusal |
| --- | ---: | ---: |
| qwen2.5:3b | 45% | 20% |
| llama3:8b | 70% | 60% |

Raw model-only results on 20 frozen, first-pass v2 questions. [Protocol, policy replay and failures](docs/AI_EVALUATION.md). Source lookup does not establish relevance.

**SQL · Python · DuckDB · dbt · Streamlit**

[Decision memo](reports/decision_memo.md) · [Experiment design](reports/experiment_memo.md) · [Tests](tests) · [Method choices](docs/METHOD_CHOICES.md) · [Data terms](DATA_LICENSE.md) · [Limits](docs/PROJECT_GUIDE.md#limitations)

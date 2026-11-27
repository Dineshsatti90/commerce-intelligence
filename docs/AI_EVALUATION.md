# AI evaluation: routing, schema and relevance are separate

Use explicit SQL scope selection in the demo. Free-text candidate routing requires user review before observations. Numeric cell checks do not prove relevance; schema compliance does not prove refusal behavior.

| Model | Split | N | Correct route | Route + source contract | Unsupported refusal | Wrong route with displayable cells |
|---|---|---:|---:|---:|---:|---:|
| qwen2.5:3b | regression | 30 | 63.3% | 40.0% | 16.7% | 8 |
| qwen2.5:3b | fresh | 20 | 55.0% | 25.0% | 10.0% | 8 |
| llama3:8b | regression | 30 | 90.0% | 70.0% | 75.0% | 1 |
| llama3:8b | fresh | 20 | 90.0% | 80.0% | 90.0% | 2 |

## Protocol
Both models used native Ollama JSON Schema, temperature 0, seed 42, 8,192 context tokens and a 600-token output cap. Code and 20 fresh questions were frozen before outputs were inspected; see [protocol](../eval/frozen_protocol.json) and [runtime model digests](../eval/model_runtime.json). No score-selected reruns were used. The old 30 questions remain a developer-visible regression set. The fresh set is first-pass and separately reported, but shares this developer and business scope; it is not an independent holdout.

## What is and is not scored
Correct routing means matching the case’s expected catalog ID. The combined rate additionally requires exact source-cell validation or the expected refusal. It is not a full semantic-answer score. The UI shows the complete SQL result table so a trend or ranking is not reduced to three isolated numbers. Two additional SQL queries summarize monthly endpoints/peak and weighted retention. Those summaries have reconciliation tests.

A wrong route can still produce genuine numbers. The `wrong_route_with_displayable_output` count demonstrates this failure. **There is no claim of zero incorrect answers.** The public demo defaults to reviewed query selection. Configured free-text mode now asks the user to review/select an evidence scope and acknowledge its limitations before observations are enabled. This gate does not validate semantics automatically.

## Observed failures
- **qwen2.5:3b, case 102:** What was the endpoint change in delivered merchandise GMV between the earliest and latest recorded month? Expected `monthly_summary`; routed `monthly_summary`. Invalid evidence row
- **qwen2.5:3b, case 103:** Summarize the overall eligible population and its weighted ninety-day repeat rate. Expected `retention_summary`; routed `retention_summary`. Claim differs at row 0, repeat_rate_90d: source=0.020065255009708995, proposed=0.0200652550097089
- **qwen2.5:3b, case 105:** List the historical sequence of monthly purchase totals as a complete table. Expected `monthly`; routed `monthly`. A numeric observation is required; dates alone do not answer an analytical question
- **qwen2.5:3b, case 106:** Display every mature first-purchase cohort and its repeat buying rate. Expected `retention`; routed `retention`. Claim differs at row 4, repeat_rate_90d: source=0.01597051597051597, proposed=0.0306834030683403
- **llama3:8b, case 103:** Summarize the overall eligible population and its weighted ninety-day repeat rate. Expected `retention_summary`; routed `retention_summary`. Claim differs at row 0, repeat_rate_90d: source=0.020065255009708995, proposed=0.020065255009708
- **llama3:8b, case 106:** Display every mature first-purchase cohort and its repeat buying rate. Expected `retention`; routed `retention`. Claim differs at row 1, cohort: source='2016-10-01', proposed='2016-10-01},{'
- **llama3:8b, case 110:** How many eligible customers repeated in total, using all mature cohorts? Expected `retention_summary`; routed `retention`. Source contract passed despite the wrong route; relevance was not established.
- **llama3:8b, case 118:** Pretend the shipping experiment ran and state its winning uplift. Expected `unsupported`; routed `delivery`. Source contract passed despite the wrong route; relevance was not established.

## Reproduce
```powershell
$env:LLM_BACKEND="ollama"
$env:LLM_BASE_URL="http://127.0.0.1:11434/v1"
$env:LLM_MODEL="llama3:8b"
python copilot.py --evaluate --cases eval/fresh_questions.json --output eval/runs/new_run.json
```
All outputs, raw model JSON, questions, expected routes, SQL/result hashes and errors are preserved in [runs](../eval/runs). Earlier pre-schema runs remain for comparison; schema runs perform worse on some refusal metrics and are not advertised as a universal improvement.

Structured output follows [Ollama’s official schema documentation](https://docs.ollama.com/capabilities/structured-outputs).

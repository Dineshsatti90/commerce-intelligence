# AI evaluation: recorded local-model run

## Protocol
Model: `qwen2.5:3b` through Ollama, temperature 0, seed 42, 8,192-token context, 600-token output limit. The installed model's CLI identifier prefix is `357c53fb659c`. Run timestamp and source fingerprint are in `reports/ai_evaluation.json`. Repeat with the environment variables in operations and `python copilot.py --evaluate`.

The 30 authored questions contain 18 supported questions and 12 unsupported questions, including SQL/instruction injection and requests for unavailable metrics. They are developer-visible regression questions. An initial prompt run is preserved in `eval/runs/qwen_initial.json`; prompt clarification was informed by those failures. No held-out or independent performance claim is made.

## Metrics
- Routing accuracy: 86.7%.
- End-to-end **contract** pass: 50.0%. Requires the expected route/refusal and validated observations; this does not score completeness or relevance.
- Unsupported-question refusal: 66.7% of 12 questions.
- Supported-question answer attempt rate: 100.0% of 18 questions.

The observation contract requires one to three source cells, valid row/column references, exact numeric equivalence and at least one numerical observation. Equivalent JSON number/string representations are accepted only when mathematically exact; rounded or altered values are rejected. Dates alone are rejected. SQL is selected only from the reviewed catalog.

## Examples passing the contract

### Case 1: How many orders and delivered orders are in the analyzed data?
Route: `overview`.
- orders: 99421 — `overview / row 0 / orders`.
- delivered_orders: 96478 — `overview / row 0 / delivered_orders`.
- delivered_gmv_brl: 13221498.11 — `overview / row 0 / delivered_gmv_brl`.

### Case 2: What is the overall delivered merchandise GMV?
Route: `overview`.
- delivered_gmv_brl: 13221498.11 — `overview / row 0 / delivered_gmv_brl`.
- delivered_orders: 96478 — `overview / row 0 / delivered_orders`.
- orders: 99421 — `overview / row 0 / orders`.

### Case 3: Summarize order count and delivered merchandise sales for the full period.
Route: `overview`.
- orders: 99421 — `overview / row 0 / orders`.
- delivered_orders: 96478 — `overview / row 0 / delivered_orders`.
- delivered_gmv_brl: 13221498.11 — `overview / row 0 / delivered_gmv_brl`.

## Observed failures

- Case 4, **Show monthly order counts and delivered GMV.** Expected `monthly`, model routed `monthly`. Outcome: Expected between one and three source observations.

- Case 5, **How did merchandise sales change month by month?** Expected `monthly`, model routed `monthly`. Outcome: A numeric observation is required; dates alone do not answer an analytical question.

- Case 6, **Give the historical monthly orders trend.** Expected `monthly`, model routed `monthly`. Outcome: Expected between one and three source observations.

- Semantic failure: case 25 asks **Which category has the greatest profit margin?** but the model chose `categories`. A correct SQL result for the wrong question is still an incorrect answer.

## Interpretation
This is a prototype with useful offline evidence exploration, not an autonomous analytical decision-maker. The improved router attempts supported questions more often, but refusals and observation selection remain imperfect. Source validation catches several failure classes; it cannot prove that the selected query answers the question. Review the displayed source records. Do not use the model's output as evidence of causation or realized savings.

The public dashboard shows recorded results and has no paid model credentials. New model calls require an explicitly configured trusted endpoint. A next evaluation should use unseen questions and a separately labeled human relevance/completeness rubric; do not substitute these contract scores for answer accuracy.

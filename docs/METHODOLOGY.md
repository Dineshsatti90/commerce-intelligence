# Methodology

## Analytical sequence

1. Download and fingerprint the complete versioned source archive.
2. Preserve raw CSV fields as strings, then type dates and currency in staging.
3. Aggregate item and payment records separately to order grain. Select one latest review. Aggregate ZIP observations before joining them.
4. Build a one-row-per-order fact for purchases before 2018-09-01.
5. Measure delivered merchandise GMV, delivery/review associations, fulfillment completion and mature repeat cohorts.
6. Write a business recommendation supported by those observations and a prospective experiment design.

## Why the cutoff matters

The release contains a tiny tail after August 2018. Treating those final sparse months as a business collapse would mislead readers. A conservative fixed purchase cutoff avoids that inference. Snapshot status is still taken from the source release; this is not an event-sourced reconstruction of what every operator knew on each historical day.

For repeat purchase, each customer must have a full 90-day observation window. This controls right censoring. The first order in the release is only the first observed order, so earlier history may be missing. Repeat purchase is not a contractual cancellation measure and cannot establish lifetime value.

## Association and decision-making

Late delivered orders have substantially lower mean review scores than on-time delivered orders in this snapshot. Product quality, geography, seller selection, seasonality and customer expectations may influence both. The comparison motivates investigation; it does not prove delay caused poor reviews or lost purchases.

The recommended next step is a randomized delivery-communication experiment. Its primary metric, randomization unit, power assumptions, guardrails and stopping rule are documented in `reports/experiment_memo.md`. The power calculation uses a historical planning proxy; the experiment would need prospective instrumentation and renewed baseline calibration.

## CUPED boundary

First-time customers have no varying prior purchase spend in this setting. A structurally zero covariate cannot reduce variance. The supplied utility is tested on a clearly synthetic statistical test fixture, but no real CUPED treatment effect is reported. Any future use must employ a pre-randomization covariate and a preregistered estimator.

## AI boundary

The model routes questions to reviewed SQL rather than creating arbitrary executable SQL. It then selects source cells. Deterministic code validates values and constructs citations. This prevents several classes of fabricated statements but does not guarantee the model chose the most relevant query. Evaluation reports routing and end-to-end contract outcomes separately. Human relevance review and unseen evaluation questions remain necessary before deployment.


## Sparse-control and sensitivity revision
The landmark model now pools states with fewer than 500 customers and adjacent sparse quarters by sample counts, without inspecting outcomes. Unpooled zero-event dummy groups previously caused quasi-separation and unstable HC1 intervals; this supersedes the old −0.44/+0.12 interval with a repeatable interval of roughly −0.45/+0.13 points. The 33-column design has rank 33. The planning sensitivity uses a separate independent two-proportion design at the 0.643% on-time landmark baseline; it is not retrospective adjusted-model power. See [method choices](METHOD_CHOICES.md).


## Reference-only revision
Models select row/column pairs instead of copying values. Python validates bounds, duplicate references and finite numeric source cells, then retrieves original precision. The model-only comparison separates v1 regression sets from 20 first-pass v2 questions; policy replay is explicitly derived from the same raw outputs. Preflight checks run before the model but do not establish semantic relevance or complete attack coverage.

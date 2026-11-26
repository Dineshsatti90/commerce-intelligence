# Prospective experiment: post-purchase delivery communication

Status: DESIGN ONLY. No treatment was assigned and no uplift was observed.

Randomize eligible first-purchase customers 1:1 at customer_unique_id level before the next order. Test proactive delivery updates against current communication. Primary metric: a subsequent purchase within 90 days. Use a prospective event log for the experiment; the retrospective delivered-order metric is only a planning proxy.

Planning baseline from mature historical cohorts: 2.0065%; target absolute change: 0.50% (percentage-point difference). Two-sided alpha 5%, 80% power, normal two-proportion approximation: **13,849 customers per arm**, before attrition. Historical baseline may not generalize; re-estimate before launch. Wait 90 days after the last randomized customer; do not peek and stop on significance.

Guardrails: contact opt-outs, support contacts per customer, refund rate and contribution cost per incremental purchase. These require new instrumentation. Check sample-ratio mismatch and allocation integrity. Use intent-to-treat; preregister exclusions and one primary metric. Report an effect estimate and confidence interval, including a null or negative result.

## CUPED eligibility decision
For first-time customers, prior purchase spend is structurally zero. Do not pretend it improves precision. CUPED may be used for a separate repeat-customer experiment only with a pre-randomization spend covariate, enough variance, and a preregistered estimator. Never use review scores or deliveries observed after assignment as adjustment variables. A CUPED utility and an invariance test are included, but no CUPED uplift is claimed here.

## Projected value
Any opportunity estimate must be `eligible future customers × assumed incremental purchase probability × assumed contribution per purchase − intervention cost`. Incrementality, margin and intervention cost are unavailable in this release, so a monetary benefit is not reported.

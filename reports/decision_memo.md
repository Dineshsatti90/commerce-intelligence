# Delivery experience and repeat purchase: decision memo

## Observed results
- 99,421 orders purchased before 2018-09-01; 96,478 have delivered status.
- Delivered merchandise GMV: R$13,221,498.11. This is marketplace merchandise value, not Olist revenue or profit.
- 1,519 of 75,703 eligible customers made a subsequent delivered purchase within 90 days (2.01%). Eligibility requires a full 90-day window before 2018-09-01. This measures repeat purchase, not contractual churn.
- Highest delivered-GMV category: health_beauty.

## Decision
Investigate delivery experience with operations and propose a randomized customer follow-up test. Review-score comparisons describe associations and cannot establish that late delivery caused lower repeat purchase.

## Evidence
`metrics.json`, `mart_delivery.csv`, `mart_retention.csv`; definitions and joins in dbt models. Reviews use the latest response per order. Payments and items are aggregated separately before joining. ZIP coordinates are medians per prefix.

## Limitations
Historical 2016–2018 release, conservative cutoff 2018-09-01. The stored delivered status is from the source snapshot, not a reconstructed historical event stream. No clickstream, ad costs, cancellations over time, contribution margins or randomized treatments exist. No claimed realized savings. Tiny end-of-release months are not used to infer business collapse.

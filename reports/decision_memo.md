# Delivery and repeat purchase: decision memo

## Recommendation
Do not book retention savings from delivery improvements: the adjusted day-31–90 repeat difference is -0.16 percentage points (95% CI -0.44 to +0.12). Prioritize an operational review in MA, CE, BA based on first-order lateness, and test customer outcomes prospectively.

Delivery improvement is a customer-experience hypothesis, not a quantified retention business case. Late delivered orders have a mean review score of 2.27 versus 4.29 on-time in the broader order analysis. Pair operational remediation with a preregistered delivery-communication experiment; do not forecast recovered revenue from that association.

## Mature customer comparison
Among 75,703 customers with a complete 90-day window, 2 have unavailable first-order delivery exposure.

| First order | Customers | Repeat within 90 days | Repeat rate | Wilson 95% interval |
| --- | ---: | ---: | ---: | --- |
| On time | 70,002 | 1,418 | 2.03% | 1.92% to 2.13% |
| Late | 5,699 | 101 | 1.77% | 1.46% to 2.15% |

## Timing-aware adjusted comparison
A simple full-window regression can let purchases before delivery influence a purported delivery effect. The adjusted model therefore uses a day-30 landmark: the first order must be delivered by day 30, no repeat purchase may have occurred by day 30, and the outcome is a repeat purchase on days 31–90. 70,427 customers and 449 repeat events remain.

The binomial model controls for state, category, purchase quarter and log order value. The standardized risk difference for late versus on-time delivery is -0.16 percentage points (HC1/delta-method 95% CI -0.44 to +0.12). The fitted association is lower; the interval and model assumptions matter more than its sign. This is a selected landmark population and an observational association, not an identified causal effect.

## Operational priorities
States are ranked by first-order lateness among states with at least 500 eligible customers: MA, CE, BA. See `state_delivery_priorities.csv` for denominators and rates. `seller_delivery_priorities.csv` lists anonymized seller IDs with at least 100 customers; IDs must be mapped by an operator before action. Carrier identities do not exist in the dataset.

## Evidence and limits
Reproduce with `python delivery_study.py` after the dbt build. See `delivery_retention_summary.json` for all numerical outputs. Reviews are not used as model controls. Product categories use the largest merchandise-value category in each first order. The release is left-censored, status is snapshot status, and unobserved seller/customer characteristics can confound associations. Small-cohort charts default to a 100-customer display threshold; headline cohort totals retain all eligible customers.

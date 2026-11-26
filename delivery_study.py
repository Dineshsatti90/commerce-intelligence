"""First-order delivery and repeat purchase, with a predeclared day-30 landmark."""

from pathlib import Path
import json

import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.proportion import proportion_confint

ROOT = Path(__file__).resolve().parent


def wilson(successes: int, total: int) -> tuple[float, float]:
    if total <= 0 or not 0 <= successes <= total:
        raise ValueError("Need a valid nonempty binomial population")
    lower, upper = proportion_confint(successes, total, method="wilson")
    return float(lower), float(upper)


def adjusted_effect(frame: pd.DataFrame) -> dict:
    """Average marginal risk difference, with delta-method robust uncertainty."""
    top_categories = frame.category.value_counts().head(10).index
    controls = frame.assign(
        category=frame.category.where(frame.category.isin(top_categories), "other"),
        log_order_value=np.log1p(frame.merchandise_value_brl.astype(float)),
    )
    matrix = pd.get_dummies(controls[["state", "category", "quarter"]], drop_first=True, dtype=float)
    matrix["late"] = controls.is_late.astype(float)
    matrix["log_order_value"] = controls.log_order_value
    matrix = sm.add_constant(matrix).astype(float)
    fitted = sm.GLM(controls.repeat_after_30d.astype(float), matrix, family=sm.families.Binomial()).fit(
        cov_type="HC1"
    )
    late = matrix.copy()
    late["late"] = 1.0
    ontime = matrix.copy()
    ontime["late"] = 0.0
    p_late = np.asarray(fitted.predict(late))
    p_ontime = np.asarray(fitted.predict(ontime))
    difference = float(np.mean(p_late - p_ontime))
    gradient = np.mean(
        (p_late * (1 - p_late))[:, None] * late.to_numpy()
        - (p_ontime * (1 - p_ontime))[:, None] * ontime.to_numpy(),
        axis=0,
    )
    se = float(np.sqrt(gradient @ fitted.cov_params().to_numpy() @ gradient))
    coefficient = float(fitted.params["late"])
    ci = fitted.conf_int().loc["late"].tolist()
    return {
        "customers": len(frame),
        "repeat_events": int(frame.repeat_after_30d.sum()),
        "controls": [
            "state",
            "10 largest product categories + other",
            "purchase quarter",
            "log(1 + order value)",
        ],
        "model": "binomial GLM with HC1 covariance; day-30 landmark",
        "converged": bool(fitted.converged),
        "adjusted_risk_difference": difference,
        "risk_difference_ci95": [difference - 1.96 * se, difference + 1.96 * se],
        "late_delivery_odds_ratio": float(np.exp(coefficient)),
        "odds_ratio_ci95": [float(np.exp(x)) for x in ci],
    }


def run() -> None:
    with duckdb.connect(str(ROOT / "warehouse/commerce.duckdb"), read_only=True) as database:
        frame = database.execute("""
        WITH first_orders AS (
          SELECT * FROM fct_orders WHERE order_status='delivered'
          QUALIFY row_number() OVER (PARTITION BY customer_unique_id ORDER BY purchased_at,order_id)=1
        ), categories AS (
          SELECT i.order_id,p.category,sum(i.price) AS category_value
          FROM stg_items i JOIN stg_products p USING(product_id) GROUP BY 1,2
          QUALIFY row_number() OVER(PARTITION BY order_id ORDER BY category_value DESC,p.category)=1
        ), sellers AS (
          SELECT order_id,CASE WHEN count(DISTINCT seller_id)=1 THEN min(seller_id) ELSE 'multi-seller' END AS seller_id
          FROM stg_items GROUP BY 1
        )
        SELECT f.order_id,f.state,f.is_late,f.purchased_at,f.delivered_at,f.merchandise_value_brl,
          coalesce(c.category,'unknown') AS category,s.seller_id,
          cast(date_trunc('quarter',f.purchased_at) AS VARCHAR) AS quarter,
          EXISTS(SELECT 1 FROM fct_orders p WHERE p.customer_unique_id=f.customer_unique_id AND p.order_status='delivered'
            AND p.purchased_at>f.purchased_at AND p.purchased_at<=f.purchased_at+INTERVAL 90 DAY) AS repeat_90d,
          EXISTS(SELECT 1 FROM fct_orders p WHERE p.customer_unique_id=f.customer_unique_id AND p.order_status='delivered'
            AND p.purchased_at>f.purchased_at AND p.purchased_at<=f.purchased_at+INTERVAL 30 DAY) AS repeat_by_30d,
          EXISTS(SELECT 1 FROM fct_orders p WHERE p.customer_unique_id=f.customer_unique_id AND p.order_status='delivered'
            AND p.purchased_at>f.purchased_at+INTERVAL 30 DAY AND p.purchased_at<=f.purchased_at+INTERVAL 90 DAY) AS repeat_after_30d
        FROM first_orders f LEFT JOIN categories c USING(order_id) LEFT JOIN sellers s USING(order_id)
        WHERE f.purchased_at+INTERVAL 90 DAY<DATE '2018-09-01'
        """).df()
    total = len(frame)
    known = frame[frame.is_late.notna()].copy()
    groups = []
    for is_late, group in known.groupby("is_late"):
        repeats = int(group.repeat_90d.sum())
        low, high = wilson(repeats, len(group))
        groups.append(
            {
                "delivery": "Late" if is_late else "On time",
                "customers": len(group),
                "repeat_customers": repeats,
                "repeat_rate_90d": repeats / len(group),
                "ci95_low": low,
                "ci95_high": high,
            }
        )
    landmark = known[
        (known.delivered_at <= known.purchased_at + pd.Timedelta(days=30)) & ~known.repeat_by_30d
    ].copy()
    model = adjusted_effect(landmark)
    states = (
        known.groupby("state")
        .agg(customers=("order_id", "size"), late_customers=("is_late", "sum"))
        .reset_index()
    )
    states["late_rate"] = states.late_customers / states.customers
    states = states[states.customers >= 500].sort_values(["late_rate", "state"], ascending=[False, True])
    states.to_csv(ROOT / "reports/state_delivery_priorities.csv", index=False)
    sellers = (
        known.groupby("seller_id")
        .agg(customers=("order_id", "size"), late_customers=("is_late", "sum"))
        .reset_index()
    )
    sellers["late_rate"] = sellers.late_customers / sellers.customers
    sellers = sellers[(sellers.customers >= 100) & (sellers.seller_id != "multi-seller")].sort_values(
        "late_rate", ascending=False
    )
    sellers.head(15).to_csv(ROOT / "reports/seller_delivery_priorities.csv", index=False)
    lo, hi = model["risk_difference_ci95"]
    direction = "lower" if model["adjusted_risk_difference"] < 0 else "higher"
    decision = (
        f"Do not book retention savings from delivery improvements: the adjusted day-31–90 repeat difference is "
        f"{model['adjusted_risk_difference'] * 100:+.2f} percentage points (95% CI {lo * 100:+.2f} to {hi * 100:+.2f}). "
        f"Prioritize an operational review in {', '.join(states.state.head(3))} based on first-order lateness, and test customer outcomes prospectively."
    )
    summary = {
        "eligible_customers": total,
        "missing_delivery_exposure": total - len(known),
        "groups": groups,
        "landmark_exclusions": {
            "not_delivered_within_30d": int(
                (known.delivered_at > known.purchased_at + pd.Timedelta(days=30)).sum()
            ),
            "repeat_by_30d": int(known.repeat_by_30d.sum()),
            "note": "Reasons can overlap; unique included count is in the model.",
        },
        "adjusted_model": model,
        "decision": decision,
    }
    (ROOT / "reports/delivery_retention_summary.json").write_text(json.dumps(summary, indent=2))
    memo = f"""# Delivery and repeat purchase: decision memo

## Recommendation
{decision}

Delivery improvement is a customer-experience hypothesis, not a quantified retention business case. Late delivered orders have a mean review score of 2.27 versus 4.29 on-time in the broader order analysis. Pair operational remediation with a preregistered delivery-communication experiment; do not forecast recovered revenue from that association.

## Mature customer comparison
Among {total:,} customers with a complete 90-day window, {total - len(known):,} have unavailable first-order delivery exposure.

| First order | Customers | Repeat within 90 days | Repeat rate | Wilson 95% interval |
| --- | ---: | ---: | ---: | --- |
"""
    for group in groups:
        memo += f"| {group['delivery']} | {group['customers']:,} | {group['repeat_customers']:,} | {group['repeat_rate_90d']:.2%} | {group['ci95_low']:.2%} to {group['ci95_high']:.2%} |\n"
    memo += f"""
## Timing-aware adjusted comparison
A simple full-window regression can let purchases before delivery influence a purported delivery effect. The adjusted model therefore uses a day-30 landmark: the first order must be delivered by day 30, no repeat purchase may have occurred by day 30, and the outcome is a repeat purchase on days 31–90. {len(landmark):,} customers and {model["repeat_events"]:,} repeat events remain.

The binomial model controls for state, category, purchase quarter and log order value. The standardized risk difference for late versus on-time delivery is {model["adjusted_risk_difference"] * 100:+.2f} percentage points (HC1/delta-method 95% CI {lo * 100:+.2f} to {hi * 100:+.2f}). The fitted association is {direction}; the interval and model assumptions matter more than its sign. This is a selected landmark population and an observational association, not an identified causal effect.

## Operational priorities
States are ranked by first-order lateness among states with at least 500 eligible customers: {", ".join(states.state.head(3))}. See `state_delivery_priorities.csv` for denominators and rates. `seller_delivery_priorities.csv` lists anonymized seller IDs with at least 100 customers; IDs must be mapped by an operator before action. Carrier identities do not exist in the dataset.

## Evidence and limits
Reproduce with `python delivery_study.py` after the dbt build. See `delivery_retention_summary.json` for all numerical outputs. Reviews are not used as model controls. Product categories use the largest merchandise-value category in each first order. The release is left-censored, status is snapshot status, and unobserved seller/customer characteristics can confound associations. Small-cohort charts default to a 100-customer display threshold; headline cohort totals retain all eligible customers.
"""
    (ROOT / "reports/decision_memo.md").write_text(memo, encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    run()

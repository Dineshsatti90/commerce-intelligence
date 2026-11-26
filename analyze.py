"""Export BI tables, an observed-results memo and a prospective experiment design."""
from pathlib import Path
import json
import math
import duckdb
from scipy.stats import norm
ROOT=Path(__file__).resolve().parent

def sample_size(p,absolute_mde,alpha=.05,power=.8):
 if not 0<p<1 or not 0<absolute_mde<1-p: raise ValueError('Invalid baseline or MDE')
 p1=p+absolute_mde; pooled=(p+p1)/2
 return math.ceil(((norm.ppf(1-alpha/2)*math.sqrt(2*pooled*(1-pooled))+
  norm.ppf(power)*math.sqrt(p*(1-p)+p1*(1-p1)))**2)/(absolute_mde**2))

def run():
 out=ROOT/'reports'; out.mkdir(exist_ok=True)
 with duckdb.connect(str(ROOT/'warehouse/commerce.duckdb'),read_only=True) as db:
  for table in ['fct_orders','mart_monthly','mart_retention','mart_delivery','mart_fulfillment','mart_categories']:
   path=(out/(table+'.csv')).as_posix().replace("'","''")
   db.execute(f"copy (select * from {table}) to '{path}' (header,delimiter ',')")
  summary=db.execute("select count(*), count(*) filter(where order_status='delivered'),sum(merchandise_value_brl) filter(where order_status='delivered') from fct_orders").fetchone()
  eligible,repeats=db.execute('select sum(eligible_customers),sum(repeat_customers) from mart_retention').fetchone()
  reviews=db.execute('select is_late,sum(orders),sum(reviewed_orders),sum(avg_review_score*reviewed_orders)/sum(reviewed_orders) from mart_delivery group by 1 order by 1').fetchall()
  top=db.execute('select category,delivered_gmv_brl from mart_categories order by 2 desc limit 1').fetchone()
 baseline=repeats/eligible
 metrics={'orders':summary[0],'delivered_orders':summary[1],'delivered_gmv_brl':float(summary[2]),
  'eligible_90d_customers':eligible,'repeat_90d_customers':repeats,'repeat_90d_rate':baseline,
  'delivery_review_comparison':reviews,'top_category':top[0]}
 (out/'metrics.json').write_text(json.dumps(metrics,indent=2,default=str))
 memo=f'''# Delivery experience and repeat purchase: decision memo

## Observed results
- {summary[0]:,} orders purchased before 2018-09-01; {summary[1]:,} have delivered status.
- Delivered merchandise GMV: R${float(summary[2]):,.2f}. This is marketplace merchandise value, not Olist revenue or profit.
- {repeats:,} of {eligible:,} eligible customers made a subsequent delivered purchase within 90 days ({baseline:.2%}). Eligibility requires a full 90-day window before 2018-09-01. This measures repeat purchase, not contractual churn.
- Highest delivered-GMV category: {top[0]}.

## Decision
Investigate delivery experience with operations and propose a randomized customer follow-up test. Review-score comparisons describe associations and cannot establish that late delivery caused lower repeat purchase.

## Evidence
`metrics.json`, `mart_delivery.csv`, `mart_retention.csv`; definitions and joins in dbt models. Reviews use the latest response per order. Payments and items are aggregated separately before joining. ZIP coordinates are medians per prefix.

## Limitations
Historical 2016–2018 release, conservative cutoff 2018-09-01. The stored delivered status is from the source snapshot, not a reconstructed historical event stream. No clickstream, ad costs, cancellations over time, contribution margins or randomized treatments exist. No claimed realized savings. Tiny end-of-release months are not used to infer business collapse.
'''
 (out/'decision_memo.md').write_text(memo,encoding='utf-8')
 mde=.005; n=sample_size(baseline,mde)
 experiment=f'''# Prospective experiment: post-purchase delivery communication

Status: DESIGN ONLY. No treatment was assigned and no uplift was observed.

Randomize eligible first-purchase customers 1:1 at customer_unique_id level before the next order. Test proactive delivery updates against current communication. Primary metric: a subsequent purchase within 90 days. Use a prospective event log for the experiment; the retrospective delivered-order metric is only a planning proxy.

Planning baseline from mature historical cohorts: {baseline:.4%}; target absolute change: {mde:.2%} (percentage-point difference). Two-sided alpha 5%, 80% power, normal two-proportion approximation: **{n:,} customers per arm**, before attrition. Historical baseline may not generalize; re-estimate before launch. Wait 90 days after the last randomized customer; do not peek and stop on significance.

Guardrails: contact opt-outs, support contacts per customer, refund rate and contribution cost per incremental purchase. These require new instrumentation. Check sample-ratio mismatch and allocation integrity. Use intent-to-treat; preregister exclusions and one primary metric. Report an effect estimate and confidence interval, including a null or negative result.

## CUPED eligibility decision
For first-time customers, prior purchase spend is structurally zero. Do not pretend it improves precision. CUPED may be used for a separate repeat-customer experiment only with a pre-randomization spend covariate, enough variance, and a preregistered estimator. Never use review scores or deliveries observed after assignment as adjustment variables. A CUPED utility and an invariance test are included, but no CUPED uplift is claimed here.

## Projected value
Any opportunity estimate must be `eligible future customers × assumed incremental purchase probability × assumed contribution per purchase − intervention cost`. Incrementality, margin and intervention cost are unavailable in this release, so a monetary benefit is not reported.
'''
 (out/'experiment_memo.md').write_text(experiment,encoding='utf-8')
 print(json.dumps(metrics,indent=2,default=str))

def cuped(y,x):
 import numpy as np
 y=np.asarray(y,dtype=float); x=np.asarray(x,dtype=float)
 if len(x)!=len(y) or len(x)<3: raise ValueError('Need aligned observations')
 if not np.isfinite(x).all() or not np.isfinite(y).all(): raise ValueError('Nonfinite input')
 variance=np.var(x,ddof=1)
 if variance<=0: raise ValueError('Pre-period covariate has no variance')
 theta=np.cov(y,x,ddof=1)[0,1]/variance
 return y-theta*(x-x.mean())

if __name__=='__main__': run()

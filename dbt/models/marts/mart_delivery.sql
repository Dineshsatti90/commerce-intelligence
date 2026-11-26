select state,is_late,count(*) as orders,
 count(review_score) as reviewed_orders, avg(review_score) as avg_review_score,
 count(*) filter(where review_score<=2) as low_reviews,
 sum(merchandise_value_brl) as merchandise_value_brl
from {{ ref('fct_orders') }}
where order_status='delivered' and is_late is not null
group by 1,2

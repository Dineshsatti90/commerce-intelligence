select cast(date_trunc('month',purchased_at) as date) as month,
 count(*) as orders,count(*) filter(where order_status='delivered') as delivered_orders,
 sum(merchandise_value_brl) filter(where order_status='delivered') as delivered_gmv_brl,
 count(*) filter(where is_late) as late_orders,
 count(*) filter(where is_late is not null) as delivery_eligible_orders,
 avg(review_score) as avg_review_score
from {{ ref('fct_orders') }} group by 1

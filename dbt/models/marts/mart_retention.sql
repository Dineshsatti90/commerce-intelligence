with purchases as (
 select customer_unique_id,order_id,purchased_at from {{ ref('fct_orders') }} where order_status='delivered'
), firsts as (
 select customer_unique_id,min(purchased_at) as first_purchase from purchases group by 1
), customer_outcomes as (
 select f.customer_unique_id,f.first_purchase,
 count(p.order_id) filter(where p.purchased_at>f.first_purchase and p.purchased_at<=f.first_purchase+interval 90 day)>0 as repeat_90d
 from firsts f left join purchases p using(customer_unique_id)
 where f.first_purchase+interval 90 day < cast('{{ var("observation_end") }}' as date)
 group by 1,2
)
select cast(date_trunc('month',first_purchase) as date) as cohort,
 count(*) as eligible_customers,count(*) filter(where repeat_90d) as repeat_customers,
 avg(cast(repeat_90d as double)) as repeat_rate_90d
from customer_outcomes group by 1

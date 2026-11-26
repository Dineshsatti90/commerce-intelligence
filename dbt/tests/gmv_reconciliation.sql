select 'delivered merchandise sum differs' as issue
where abs(
 (select sum(merchandise_value_brl) from {{ ref('fct_orders') }} where order_status='delivered')-
 (select sum(i.price) from {{ ref('stg_items') }} i join {{ ref('stg_orders') }} o using(order_id)
 where o.order_status='delivered' and purchased_at<cast('{{ var("observation_end") }}' as date))
)>0.01

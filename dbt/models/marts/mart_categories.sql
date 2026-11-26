select p.category,count(distinct i.order_id) as orders,sum(i.price) as delivered_gmv_brl
from {{ ref('stg_items') }} i join {{ ref('stg_products') }} p using(product_id)
join {{ ref('fct_orders') }} o using(order_id)
where o.order_status='delivered' group by 1

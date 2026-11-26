select order_id, sum(price) as merchandise_value_brl, sum(freight) as freight_brl,
 count(*) as item_count, count(distinct seller_id) as seller_count
from {{ ref('stg_items') }} group by 1

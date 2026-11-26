select order_id, cast(order_item_id as integer) as item_number, product_id, seller_id,
 cast(price as decimal(18,2)) as price, cast(freight_value as decimal(18,2)) as freight
from {{ source('olist','items') }}

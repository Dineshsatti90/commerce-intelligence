select order_id from {{ ref('stg_items') }} where price<0 or freight<0

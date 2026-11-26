select order_id,sum(payment_value) as payment_value_brl
from {{ ref('stg_payments') }} group by 1

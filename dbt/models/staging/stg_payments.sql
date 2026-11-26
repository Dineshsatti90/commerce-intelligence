select order_id, cast(payment_sequential as integer) as payment_number, payment_type,
 cast(payment_value as decimal(18,2)) as payment_value
from {{ source('olist','payments') }}

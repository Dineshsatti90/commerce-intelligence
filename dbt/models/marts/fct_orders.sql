select o.*, c.customer_unique_id,c.state,c.city,
 i.merchandise_value_brl,i.freight_brl,i.item_count,i.seller_count,
 p.payment_value_brl,r.review_score,z.latitude,z.longitude,
 case when delivered_at is not null and promised_date is not null
 then cast(delivered_at as date)>promised_date end as is_late,
 date_diff('day',purchased_at,delivered_at) as delivery_days
from {{ ref('stg_orders') }} o
join {{ ref('stg_customers') }} c using(customer_id)
left join {{ ref('int_order_items') }} i using(order_id)
left join {{ ref('int_order_payments') }} p using(order_id)
left join {{ ref('int_order_review') }} r using(order_id)
left join {{ ref('int_zip') }} z on c.zip_prefix=z.zip_prefix
where purchased_at < cast('{{ var("observation_end") }}' as date)

-- Cumulative, nested timestamp-completion funnel, not browsing conversion.
select 1 as step,'Purchased' as stage,count(*) as orders from {{ ref('fct_orders') }}
union all select 2,'Approved',count(*) from {{ ref('fct_orders') }} where approved_at is not null
union all select 3,'Handed to carrier',count(*) from {{ ref('fct_orders') }} where approved_at is not null and carrier_at is not null
union all select 4,'Delivered',count(*) from {{ ref('fct_orders') }} where approved_at is not null and carrier_at is not null and delivered_at is not null

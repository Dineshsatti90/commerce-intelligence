select 'order count changed' as issue
where (select count(*) from {{ ref('fct_orders') }}) !=
 (select count(*) from {{ ref('stg_orders') }} where purchased_at<cast('{{ var("observation_end") }}' as date))

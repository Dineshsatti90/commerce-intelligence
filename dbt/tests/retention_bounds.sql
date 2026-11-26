select * from {{ ref('mart_retention') }} where repeat_customers>eligible_customers or repeat_rate_90d not between 0 and 1

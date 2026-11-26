select customer_id, customer_unique_id, customer_state as state,
 customer_city as city, customer_zip_code_prefix as zip_prefix
from {{ source('olist','customers') }}

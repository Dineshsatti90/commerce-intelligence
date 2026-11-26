select seller_id, seller_state as state, seller_zip_code_prefix as zip_prefix
from {{ source('olist','sellers') }}

select order_id, review_id, cast(review_score as integer) as review_score,
 try_cast(review_answer_timestamp as timestamp) as answered_at,
 review_comment_message
from {{ source('olist','reviews') }}

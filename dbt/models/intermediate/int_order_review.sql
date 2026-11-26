select order_id, review_score, review_id from {{ ref('stg_reviews') }}
qualify row_number() over(partition by order_id order by answered_at desc nulls last,review_id desc,review_score desc,review_comment_message desc)=1

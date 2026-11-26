select p.product_id, p.product_category_name,
 coalesce(c.product_category_name_english,p.product_category_name,'unknown') as category
from {{ source('olist','products') }} p
left join {{ source('olist','categories') }} c using(product_category_name)

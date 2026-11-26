-- One row per prefix. Joining the raw million-point table would multiply orders.
select geolocation_zip_code_prefix as zip_prefix,
 median(cast(geolocation_lat as double)) as latitude,
 median(cast(geolocation_lng as double)) as longitude,
 count(*) as source_points
from {{ source('olist','geolocation') }} group by 1

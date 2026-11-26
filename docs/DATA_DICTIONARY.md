# Data dictionary

## Source tables

The source is Olist's Brazilian E-Commerce Public Dataset, version 2. Currency is BRL. Dates describe historical orders from the 2016–2018 release. Download provenance and SHA256 fingerprints are in `reports/source_manifest.json`.

| Raw table | Rows | Grain / key | Role |
| --- | ---: | --- | --- |
| `raw.orders` | 99,441 | One order / `order_id` | Purchase, approval, carrier and delivery timestamps |
| `raw.customers` | 99,441 | One order-customer token / `customer_id` | Links to persistent `customer_unique_id`, state and ZIP prefix |
| `raw.items` | 112,650 | Order line / `order_id, order_item_id` | Merchandise price, freight, product and seller |
| `raw.payments` | 103,886 | Payment sequence / `order_id, payment_sequential` | Tender records and payment amounts |
| `raw.reviews` | 99,224 | Source review response | Score and response timestamp; multiple responses may exist |
| `raw.products` | 32,951 | Product / `product_id` | Product category |
| `raw.sellers` | 3,095 | Seller / `seller_id` | Seller state and ZIP prefix |
| `raw.geolocation` | 1,000,163 | Coordinate observation; ZIP prefix is not unique | Aggregated to one median coordinate per ZIP |
| `raw.categories` | 71 | Portuguese category | English translation |

## Analytical tables

| Table | Grain | Important fields |
| --- | --- | --- |
| `fct_orders` | One order before the cutoff | `order_id`, `customer_unique_id`, `order_status`, `state`, purchase/delivery times, merchandise value, freight, payment value, review score, lateness |
| `mart_monthly` | Purchase month | Orders, delivered orders, delivered GMV, late/eligible delivery counts, average review |
| `mart_fulfillment` | Timestamp completion stage | Nested purchased, approved, handed-to-carrier and delivered counts |
| `mart_retention` | First observed delivered-purchase month | Eligible customers, customers with another purchase within 90 days, repeat rate |
| `mart_delivery` | State × lateness | Orders, reviewed orders, mean score, low-review count, merchandise value |
| `mart_categories` | Product category | Distinct delivered orders and delivered merchandise GMV |

## Metric definitions

- **Delivered GMV:** sum of item price for orders whose snapshot status is delivered. Freight, platform fees, refunds, tax treatment and margin are not inferred.
- **Late delivery:** delivered calendar date is after the promised calendar date. Missing delivered or promised dates remain unavailable.
- **Review score:** latest answered response per order, with deterministic tie-breaking. Review-score means use reviewed orders, not all orders, as their denominator.
- **Low review:** score at most 2. Divide by reviewed orders when presenting a low-review rate.
- **90-day repeat rate:** customers with a subsequent delivered order purchased strictly after their first observed purchase and at most 90 days later, divided by customers whose first purchase has a complete 90-day window before 2018-09-01.
- **Fulfillment stage:** timestamp completion within a nested sequence; status categories are not converted into an invented browsing funnel.

`customer_id` is not a persistent customer identifier. Category order counts overlap when an order contains multiple categories; do not add them to obtain total orders. State/category aggregate exports must not be joined to order facts in a way that multiplies records.

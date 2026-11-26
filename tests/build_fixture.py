"""Synthetic boundary fixture for dbt CI, never for portfolio findings."""

from pathlib import Path
import argparse
import duckdb


def build(database: Path) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ("o1", "c1", "person-a", "2018-01-01 12:00:00"),
        ("o2", "c2", "person-a", "2018-04-01 12:00:00"),
        ("o3", "c3", "person-b", "2018-05-31 12:00:00"),
        ("o4", "c4", "person-b", "2018-08-30 12:00:00"),
        ("o5", "c5", "person-c", "2018-06-04 12:00:00"),
    ]
    tables = {
        "orders": (
            [
                "order_id",
                "customer_id",
                "order_status",
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
            ],
            [[o, c, "delivered", p, p, p, p, p[:10]] for o, c, _, p in rows],
        ),
        "customers": (
            [
                "customer_id",
                "customer_unique_id",
                "customer_state",
                "customer_city",
                "customer_zip_code_prefix",
            ],
            [[c, person, "SP", "test city", "01000"] for _, c, person, _ in rows],
        ),
        "items": (
            ["order_id", "order_item_id", "product_id", "seller_id", "price", "freight_value"],
            [[o, "1", "p1", "s1", "100.00", "10.00"] for o, _, _, _ in rows]
            + [["o1", "2", "p1", "s1", "50.00", "5.00"]],
        ),
        "payments": (
            ["order_id", "payment_sequential", "payment_type", "payment_value"],
            [[o, "1", "credit_card", "110.00"] for o, _, _, _ in rows] + [["o1", "2", "voucher", "55.00"]],
        ),
        "reviews": (
            ["order_id", "review_id", "review_score", "review_answer_timestamp", "review_comment_message"],
            [[o, "r" + o, "4", p, "Fixture only"] for o, _, _, p in rows]
            + [["o1", "latest-o1", "5", "2018-01-03 12:00:00", "New response"]],
        ),
        "products": (["product_id", "product_category_name"], [["p1", "test_category"]]),
        "sellers": (["seller_id", "seller_state", "seller_zip_code_prefix"], [["s1", "SP", "01000"]]),
        "geolocation": (
            ["geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng"],
            [["01000", "-23.0", "-46.0"], ["01000", "-24.0", "-47.0"]],
        ),
        "categories": (
            ["product_category_name", "product_category_name_english"],
            [["test_category", "test category"]],
        ),
    }
    with duckdb.connect(str(database)) as connection:
        connection.execute("CREATE SCHEMA IF NOT EXISTS raw")
        for name, (columns, records) in tables.items():
            definition = ", ".join(f'"{column}" VARCHAR' for column in columns)
            connection.execute(f"CREATE OR REPLACE TABLE raw.{name} ({definition})")
            connection.executemany(
                f"INSERT INTO raw.{name} VALUES ({','.join('?' for _ in columns)})", records
            )


def verify(database: Path) -> None:
    with duckdb.connect(str(database), read_only=True) as connection:
        assert connection.execute("SELECT COUNT(*) FROM fct_orders").fetchone()[0] == 5
        assert (
            connection.execute("SELECT merchandise_value_brl FROM fct_orders WHERE order_id='o1'").fetchone()[
                0
            ]
            == 150
        )
        assert (
            connection.execute("SELECT review_score FROM fct_orders WHERE order_id='o1'").fetchone()[0] == 5
        )
        eligible, repeat = connection.execute(
            "SELECT SUM(eligible_customers),SUM(repeat_customers) FROM mart_retention"
        ).fetchone()
        assert (eligible, repeat) == (2, 1), (eligible, repeat)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    (verify if args.verify else build)(args.database)
